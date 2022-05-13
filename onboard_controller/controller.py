import socket
import threading
import time
from tkinter import HORIZONTAL

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

        self.timer_interval = 0.25

        # Flags
        self.is_e_stopped = False
        self.is_halted = False
        self.is_agv_busy = False
        self.is_verifying_orientation = False
        self.is_obstructed = False
        self.is_left_vos_actuated = False
        self.is_right_vos_actuated = False

        server.start_server(self.shared_list, self.mutex_shared_list)

        self.MOTORS_GPIO_BCM = Pin.motors.value

        LDBW_BCM = Pin.left_motor_backward_direction.value
        RDBW_BCM = Pin.right_motor_backward_direction.value

        TOGGLE_LEFT_MOTOR = Pin.left_motor_kill_switch.value
        TOGGLE_RIGHT_MOTOR = Pin.right_motor_kill_switch.value

        HORIZONTAL_OS = Pin.horizontal_os.value
        RIGHT_VERTICAL_OS = Pin.right_vertical_os.value
        LEFT_VERTICAL_OS = Pin.left_vertical_os.value

        try:
            self.backward_directions = [
                gpiozero.OutputDevice(pin=LDBW_BCM, active_high=False),
                gpiozero.OutputDevice(pin=RDBW_BCM),
            ]
            self.right_motor_kill_switch = gpiozero.OutputDevice(
                pin=TOGGLE_RIGHT_MOTOR
            )
            self.left_motor_kill_switch = gpiozero.OutputDevice(
                pin=TOGGLE_LEFT_MOTOR
            )
            self.horizontal_os = gpiozero.InputDevice(pin=HORIZONTAL_OS)
            self.vertical_right_os = gpiozero.InputDevice(
                pin=RIGHT_VERTICAL_OS
            )
            self.vertical_left_os = gpiozero.InputDevice(pin=LEFT_VERTICAL_OS)
        except gpiozero.exc.BadPinFactory:
            print("GPIOZERO Bad Pin Factory.")

        # Note: must first run "sudo pigpiod -t 0 -s 4" in pi terminal. \
        # The -s 4 option selects sample rate of 4 (rows of the freq table)
        self.pi = pigpio.pi()
        self.motors_edge_counter = self.pi.callback(
            user_gpio=self.MOTORS_GPIO_BCM
        )
        self.motors_edge_counter.tally()
        self.motors_edge_counter.reset_tally()

        message_handler = threading.Thread(target=self.shared_list_handler)
        inst_handler = threading.Thread(target=self.instruction_handler)
        flag_handler = threading.Thread(target=self.flag_handler)
        message_handler.start()
        inst_handler.start()
        flag_handler.start()

    def flag_handler(self):
        while self.server.connected:
            self.is_obstructed = self.horizontal_os.value == 1
            self.is_left_vos_actuated = self.vertical_left_os.value == 1
            self.is_right_vos_actuated = self.vertical_right_os.value == 1

            if self.is_obstructed:
                # TODO: implement
                print("OBSTRUCTION DETECTED")
            time.sleep(self.timer_interval)

    def shared_list_handler(self):
        while self.server.connected:
            if not len(self.shared_list) > 0:
                time.sleep(self.timer_interval)
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

        if msg[0] == AgvCommand.traverse_route.value:
            if not self.mode == Mode.Production:
                em = "[INVALID COMMAND] AGV must be in production mode."
                self.server.send_message(em)
                return

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
                time.sleep(self.timer_interval)
                continue

            if self.is_halted:
                time.sleep(self.timer_interval)
                continue

            self.mutex_shared_list.acquire()
            inst = self.instructions.pop(0)
            self.mutex_shared_list.release()

            while self.is_agv_busy and self.server.connected:
                time.sleep(self.timer_interval)
                continue

            self.execute_instruction(inst)

    def execute_instruction(self, instruction: Instruction):
        self.is_agv_busy = True

        command = instruction.command
        value = instruction.value

        expected_pulse_count = AgvTools.calc_pulse_num_from_dist(inches=value)

        if command in [
            AgvCommand.forward.value,
            AgvCommand.backward.value,
        ]:
            if command == AgvCommand.forward.value:
                for dir in self.backward_directions:
                    dir.off()
                    time.sleep(0.050)
            else:
                for dir in self.backward_directions:
                    dir.on()
                    time.sleep(0.050)

            self.right_motor_kill_switch.off()
            self.left_motor_kill_switch.off()

            ramp_inputs = AgvTools.create_ramp_inputs(inches=value)
            AgvTools.generate_ramp(
                pi=self.pi,
                ramp=ramp_inputs,
                motor_pin=self.MOTORS_GPIO_BCM,
                clear_waves=True,
            )

            while self.is_agv_busy and self.server.connected:
                cur_pulse_count = self.motors_edge_counter.tally()
                if cur_pulse_count != expected_pulse_count:
                    time.sleep(self.timer_interval)
                    continue

                self.motors_edge_counter.reset_tally()
                self.is_agv_busy = False
                return

        elif command in [
            AgvCommand.rotate_cw.value,
            AgvCommand.rotate_ccw.value,
        ]:
            if command == AgvCommand.rotate_cw.value:
                self.right_motor_kill_switch.on()
                self.left_motor_kill_switch.off()
            else:
                self.right_motor_kill_switch.off()
                self.left_motor_kill_switch.on()

            for dir in self.backward_directions:
                dir.off()
                time.sleep(0.050)

            dist = AgvTools.calc_arc_length(angle=value)
            ramp_inputs = AgvTools.create_ramp_inputs(inches=dist)

            AgvTools.generate_ramp(
                pi=self.pi,
                ramp=ramp_inputs,
                motor_pin=self.MOTORS_GPIO_BCM,
                clear_waves=True,
            )

            wait_time = 0
            for ri in ramp_inputs:
                frequency = ri[0]
                steps = ri[1]

            wait_time += steps * (1 / frequency)

            time.sleep(wait_time)

            self.right_motor_kill_switch.off()
            self.left_motor_kill_switch.off()
            self.motors_edge_counter.reset_tally()
            self.is_agv_busy = False
            return

        elif command == AgvCommand.calibrate_home.value:
            pass

    def emergency_stop(self):
        # stop everything, then clear instruction list.
        self.is_e_stopped = True
        self.pi.wave_clear()
        self.left_motor_kill_switch.off()
        self.right_motor_kill_switch.off()
        for dir in self.backward_directions:
            dir.off()
        return

    def run_auto(self):
        pass


def main():
    PORT = 1234
    SERVER = socket.gethostbyname(socket.gethostname() + ".local")

    server = AgvSocket(ip=SERVER, port=PORT, isServer=True)

    ctrl = Controller(server)

    input()


if __name__ == "__main__":
    main()
