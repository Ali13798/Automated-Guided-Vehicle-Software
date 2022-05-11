import socket
import threading
import time

import gpiozero
import pigpio
from stationary_controller.mode import Mode
from tools.agv_socket import AgvSocket
from tools.agv_tools import AgvTools

from onboard_controller.agv_command import AgvCommand
from onboard_controller.instructions import Instruction
from onboard_controller.pi_bcm_pin_assignment import Pin

MAX_VELOCITY = 2.25


class Controller:
    def __init__(self, server: AgvSocket) -> None:
        self.mode = Mode.Unselected

        self.shared_list: list[str] = []
        self.server = server

        self.mutex_shared_list = threading.Lock()
        self.mutex_instruction = threading.Lock()
        self.instructions: list[Instruction] = []
        self.valid_commands = [cmd.value for cmd in AgvCommand]

        # Flags
        self.is_e_stopped = False
        self.is_halted = False
        self.is_agv_busy = False

        server.start_server(self.shared_list, self.mutex_shared_list)

        self.MOTORS_GPIO_BCM = Pin.motors.value

        LDBW_BCM = Pin.left_motor_backward_direction.value
        RDBW_BCM = Pin.right_motor_backward_direction.value

        TOGGLE_LEFT_MOTOR = Pin.left_motor_kill_switch.value
        TOGGLE_RIGHT_MOTOR = Pin.right_motor_kill_switch.value

        try:
            ld = gpiozero.OutputDevice(pin=LDBW_BCM, active_high=False)
            rd = gpiozero.OutputDevice(pin=RDBW_BCM)

            self.backward_directions = [ld, rd]
            self.right_motor_kill_switch = gpiozero.OutputDevice(
                pin=TOGGLE_RIGHT_MOTOR
            )
            self.left_motor_kill_switch = gpiozero.OutputDevice(
                pin=TOGGLE_LEFT_MOTOR
            )
        except gpiozero.exc.BadPinFactory:
            print("GPIOZERO Bad Pin Factory.")

        # Note: must first run "sudo pigpiod -t 0 -s 4" in pi terminal. \
        # The -s 4 option selects sample rate of 4 (rows of the freq table)
        self.pi = pigpio.pi()
        self.motors_edge_counter = self.pi.callback(
            user_gpio=self.MOTORS_GPIO_BCM
        )

        message_handler = threading.Thread(target=self.shared_list_handler)
        inst_handler = threading.Thread(target=self.instruction_handler)
        message_handler.start()
        inst_handler.start()

        inst = Instruction(command=AgvCommand.forward, value=10)
        # self.execute_instruction(inst)
        time.sleep(2)
        print(self.motors_edge_counter.tally())

    def shared_list_handler(self):
        while self.server.connected:
            if not len(self.shared_list) > 0:
                time.sleep(0.25)
                continue

            self.mutex_shared_list.acquire()
            message = self.shared_list.pop(0)
            self.mutex_shared_list.release()

            instruction = self.parse_message(message)
            if instruction is None:
                continue

            self.add_instruction(instruction)

    def add_instruction(self, inst: Instruction) -> None:
        self.mutex_instruction.acquire()
        self.instructions.append(inst)
        self.mutex_instruction.release()

        self.server.send_message(str(self.instructions))

    def consume_instruction(self) -> Instruction:
        self.mutex_instruction.acquire()
        inst = self.instructions.pop(0)
        self.mutex_instruction.release()

        return inst

    def parse_message(self, msg: str) -> Instruction:
        msg = msg.split()
        msg = [n.upper() for n in msg]

        if msg[0] == AgvCommand.e_stop.value:
            if not self.is_e_stopped:
                em = "[EMERGENCY STOP] E-Stopping AGV..."
                self.server.send_message(em)
                self.emergency_stop()
                return

            em = "[EMERGENCY STOP] Removing E-Stop..."
            self.server.send_message(em)
            self.is_e_stopped = False

        if msg[0] == AgvCommand.halt.value:
            if not self.is_halted:
                em = "[HALT] Halting AGV..."
                self.server.send_message(em)
                self.is_halted = True
                return

            em = "[HALT] Removing AGV Halt..."
            self.server.send_message(em)
            self.is_halted = False

        if len(msg) != 2:
            em = f"[INVALID COMMAND] Expected 2 words, but got {len(msg)}."
            self.server.send_message(em)
            return

        if msg[0] == AgvCommand.set_mode.value:
            if msg[1] == "TEACH":
                self.mode = Mode.Teach
                self.velocity = MAX_VELOCITY * 0.2
            elif msg[1] == "AUTO":
                self.mode = Mode.Production
                self.velocity = MAX_VELOCITY
            return

        if msg[0] not in self.valid_commands:
            em = f'[INVALID COMMAND] command "{msg[0]}" is not valid.'
            self.server.send_message(em)
            return

        try:
            int(msg[1])
        except ValueError:
            em = f'[INVALID COMMAND] expected a number as second term, but got "{msg[1]}."'
            self.server.send_message(em)
            return

        inst = Instruction(command=msg[0], value=float(msg[1]))
        return inst

    def instruction_handler(self):
        while self.server.connected:
            if not len(self.instructions) > 0:
                time.sleep(0.25)
                continue

            if self.is_halted:
                time.sleep(0.25)
                continue

            self.mutex_shared_list.acquire()
            inst = self.instructions.pop(0)
            self.mutex_shared_list.release()

            while self.is_agv_busy:
                time.sleep(0.25)
                continue

            self.execute_instruction(inst)

    def execute_instruction(self, instruction: Instruction):
        self.is_agv_busy = True

        command = instruction.command
        value = instruction.value

        expected_pulse_count = AgvTools.calc_pulse_num_from_dist(inches=value)

        # print(command, value, type(command), type(value))

        if command in [
            AgvCommand.forward.value,
            AgvCommand.backward.value,
        ]:
            if command == AgvCommand.forward.value:
                for dir in self.backward_directions:
                    dir.off()
            else:
                for dir in self.backward_directions:
                    dir.on()

            self.right_motor_kill_switch.off()
            self.left_motor_kill_switch.off()

            ramp_inputs = AgvTools.create_ramp_inputs(inches=value)
            AgvTools.generate_ramp(
                pi=self.pi,
                ramp=ramp_inputs,
                motor_pin=self.MOTORS_GPIO_BCM,
                clear_waves=True,
            )

        elif command in [
            AgvCommand.rotate_cw.value,
            AgvCommand.rotate_ccw.value,
        ]:
            if command == AgvCommand.rotate_cw.value:
                self.right_motor_kill_switch.on()
                self.left_motor_kill_switch.off()
            else:
                self.left_motor_kill_switch.on()
                self.right_motor_kill_switch.off()

            dist = AgvTools.calc_arc_length(angle=value)
            ramp_inputs = AgvTools.create_ramp_inputs(inches=dist)

            AgvTools.generate_ramp(
                pi=self.pi,
                ramp=ramp_inputs,
                motor_pin=self.MOTORS_GPIO_BCM,
                clear_waves=True,
            )

        elif command == AgvCommand.calibrate_home.value:
            pass

        while self.is_agv_busy:
            cur_pulse_count = self.motors_edge_counter.tally()
            if cur_pulse_count != expected_pulse_count:
                time.sleep(0.25)
                continue
            expected_pulse_count = 0
            self.motors_edge_counter.reset_tally()
            self.is_agv_busy = False
            return

    def emergency_stop(self):
        # stop everything, then clear instruction list.
        self.is_e_stopped = True
        self.pi.wave_clear()
        self.left_motor_kill_switch.off()
        self.right_motor_kill_switch.off()
        for dir in self.backward_directions:
            dir.off()
        return


def main():
    PORT = 1234
    SERVER = socket.gethostbyname(socket.gethostname() + ".local")

    server = AgvSocket(ip=SERVER, port=PORT, isServer=True)

    ctrl = Controller(server)

    input()


if __name__ == "__main__":
    main()
