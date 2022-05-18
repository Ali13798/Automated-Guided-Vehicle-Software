"""
File:       onboard_controller/controller.py
Author:     Ali Karimiafshar
"""

import math
import socket
import threading
import time
import webbrowser

import cv2
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
        self.destinations_list: list[str] = []

        # Flags
        self.is_e_stopped = False
        self.is_halted = False
        self.is_agv_busy = False
        self.is_verifying_orientation = False
        self.is_obstructed = False
        self.is_left_vos_actuated = False
        self.is_right_vos_actuated = False
        self.is_userful_qr_code_scanned = False

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
        self.pi.set_mode(self.MOTORS_GPIO_BCM, pigpio.OUTPUT)
        self.pi.set_pull_up_down(self.MOTORS_GPIO_BCM, pigpio.PUD_UP)
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
            self.is_obstructed = (
                self.horizontal_os.value == 1 or self.is_halted
            )
            self.is_left_vos_actuated = self.vertical_left_os.value == 1
            self.is_right_vos_actuated = self.vertical_right_os.value == 1

            qr_text = self.get_string_from_qr_code()
            if not qr_text:
                time.sleep(self.timer_interval)
                continue

            print(qr_text)

            # lst = qr_text.split()
            # start_name = lst[1]
            # end_names = lst[3:]

            # if (
            #     self.start_station_name != start_name
            #     or self.end_station_name not in end_names
            # ):
            #     time.sleep(self.timer_interval)
            #     continue

            # self.is_userful_qr_code_scanned = True

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

        # self.server.send_message(str(self.instructions))

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
                self.is_e_stopped = True
                return

            em = "[EMERGENCY STOP] Removing E-Stop..."
            self.server.send_message(em)
            self.is_e_stopped = False
            return

        if msg[0] == AgvCommand.halt.value:
            if not self.is_halted:
                em = "[HALT] Halting AGV..."
                self.server.send_message(em)
                self.is_halted = True
                return

            em = "[HALT] Removing AGV Halt..."
            self.server.send_message(em)
            self.is_halted = False
            return

        if msg[0] == AgvCommand.traverse_route.value:
            if not self.mode == Mode.Production:
                em = "[INVALID COMMAND] AGV must be in production mode."
                self.server.send_message(em)
                return

        if msg[0] == "STARTNAME":
            self.start_station_name = msg[1]
            return

        if msg[0] == "ENDNAME":
            self.end_station_name = msg[1]
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
            float(msg[1])
        except ValueError:
            em = f'[INVALID COMMAND] expected a number as second term, but got "{msg[1]}."'
            self.server.send_message(em)
            return

        inst = Instruction(command=msg[0], value=float(msg[1]))
        return inst

    def instruction_handler(self):
        was_e_stopped = False
        while self.server.connected:
            if not len(self.instructions) > 0:
                time.sleep(self.timer_interval)
                continue

            if self.is_halted:
                time.sleep(self.timer_interval)
                continue

            self.mutex_shared_list.acquire()
            if self.is_e_stopped:
                self.instructions = []
                was_e_stopped = True
            else:
                inst = self.instructions.pop(0)
            self.mutex_shared_list.release()

            while self.is_agv_busy and self.server.connected:
                time.sleep(self.timer_interval)
                continue

            while self.is_e_stopped:
                time.sleep(self.timer_interval)
                continue

            if was_e_stopped:
                was_e_stopped = False
                continue

            self.execute_instruction(inst)

    def execute_instruction(
        self,
        instruction: Instruction,
        remain_pulse: int = -1,
        is_orienting=False,
    ):
        if not is_orienting:
            self.is_agv_busy = True

        command = instruction.command
        value = instruction.value

        expected_pulse_count = (
            AgvTools.calc_pulse_num_from_dist(inches=value)
            if remain_pulse == -1
            else remain_pulse
        )

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

            ramp_inputs = (
                AgvTools.create_ramp_inputs(inches=value)
                if remain_pulse == -1
                else AgvTools.create_ramp_inputs(
                    inches=0, remain_pulse=remain_pulse
                )
            )
            AgvTools.generate_ramp(
                pi=self.pi,
                ramp=ramp_inputs,
                motor_pin=self.MOTORS_GPIO_BCM,
                clear_waves=True,
            )

            while self.is_agv_busy and self.server.connected:
                cur_pulse_count = self.motors_edge_counter.tally()
                if self.is_e_stopped:
                    self.emergency_stop()
                    break

                elif self.is_userful_qr_code_scanned and not is_orienting:
                    remaining_pulses = expected_pulse_count - cur_pulse_count
                    self.emergency_stop()
                    self.simple_search()
                    inst = Instruction(command=command, value=0)
                    self.execute_instruction(inst, remaining_pulses)
                    break

                elif self.is_obstructed:
                    self.emergency_stop()
                    remaining_pulses = expected_pulse_count - cur_pulse_count

                    while self.is_obstructed or self.is_e_stopped:
                        time.sleep(self.timer_interval)
                        continue

                    inst = Instruction(command=command, value=0)

                    self.execute_instruction(inst, remaining_pulses)
                    break

                diff = abs(expected_pulse_count - cur_pulse_count)
                if not self.is_e_stopped and diff > 11:
                    time.sleep(self.timer_interval)
                    continue
                break

            if not is_orienting:
                self.is_agv_busy = False

            self.motors_edge_counter.reset_tally()
            return

        elif command in [
            AgvCommand.rotate_cw.value,
            AgvCommand.rotate_ccw.value,
        ]:
            if not is_orienting:
                if command == AgvCommand.rotate_cw.value:
                    self.right_motor_kill_switch.on()
                    self.left_motor_kill_switch.off()
                else:
                    self.right_motor_kill_switch.off()
                    self.left_motor_kill_switch.on()

                for dir in self.backward_directions:
                    dir.off()
                    time.sleep(0.050)
            else:
                self.right_motor_kill_switch.off()
                self.left_motor_kill_switch.off()

                if command == AgvCommand.rotate_cw.value:
                    self.backward_directions[0].off()
                    self.backward_directions[1].on()
                else:
                    self.backward_directions[0].on()
                    self.backward_directions[1].off()

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

            time.sleep(wait_time + 0.050)

            self.right_motor_kill_switch.off()
            self.left_motor_kill_switch.off()
            self.motors_edge_counter.reset_tally()
            if not is_orienting:
                self.is_agv_busy = False
            return

        elif command == AgvCommand.calibrate_home.value:
            pass

    def emergency_stop(self):
        # stop everything, then clear instruction list.
        AgvTools.wave_clear(pi=self.pi, motor=self.MOTORS_GPIO_BCM)
        self.motors_edge_counter.reset_tally()
        self.left_motor_kill_switch.off()
        self.right_motor_kill_switch.off()
        for dir in self.backward_directions:
            dir.off()
        return

    def run_auto(self):
        pass

    def get_string_from_qr_code(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, 640)  # Set horizontal resolution
        cap.set(4, 640)  # Set vertical resolution
        # initialize the cv2 QRCode detector
        detector = cv2.QRCodeDetector()
        while True:
            _, img = cap.read()
            data, bbox, _ = detector.detectAndDecode(img)
            if data:
                a = data
                break
            if cv2.waitKey(1) == ord("q"):
                break
        text = str(a)
        cap.release()
        cv2.destroyAllWindows()
        return text

    def simple_search(self):
        if (
            self.is_userful_qr_code_scanned
            and not self.is_left_vos_actuated
            and not self.is_right_vos_actuated
        ):
            # Starting from current position traverse forward
            # half an inch at a time and search bands.
            is_found = False
            search_band_total = 4
            for i in range(0, search_band_total, 0.5):
                temp_inst = Instruction(
                    command=AgvCommand.forward.value, value=0.5
                )
                self.execute_instruction(
                    instruction=temp_inst, is_orienting=True
                )

                is_found = self.pivot_helper()
                if is_found:
                    return

            # never found targets.
            temp_inst = Instruction(
                command=AgvCommand.backward.value, value=search_band_total
            )
            self.execute_instruction(instruction=temp_inst, is_orienting=True)
            return

        # Else block of the if statement above
        return

    def pivot_helper(self):
        inc = 4
        total_one_way = 28
        is_found = self.incremental_turns(
            is_cw=True, increment=inc, sweep_angle=total_one_way
        )
        if is_found:
            return is_found

        temp_inst = Instruction(
            command=AgvCommand.rotate_ccw.value, value=total_one_way
        )
        self.execute_instruction(instruction=temp_inst, is_orienting=True)
        is_found = self.incremental_turns(
            is_cw=False, increment=inc, sweep_angle=total_one_way
        )
        if is_found:
            return is_found

        temp_inst = Instruction(
            command=AgvCommand.rotate_cw.value, value=total_one_way
        )
        self.execute_instruction(instruction=temp_inst, is_orienting=True)
        return is_found

    def incremental_turns(
        self, is_cw: bool, increment: int = 4, sweep_angle: int = 52
    ):
        cmd = (
            AgvCommand.rotate_cw.value
            if is_cw
            else AgvCommand.rotate_ccw.value
        )
        is_found = False
        for i in range(sweep_angle // increment):
            inst = Instruction(command=cmd, value=increment)
            self.execute_instruction(instruction=inst, is_orienting=True)
            is_found = (
                self.is_left_vos_actuated and self.is_right_vos_actuated
            )
            if is_found:
                return is_found

        return is_found


def main():
    PORT = 1234
    SERVER = socket.gethostbyname(socket.gethostname() + ".local")

    server = AgvSocket(ip=SERVER, port=PORT, isServer=True)

    ctrl = Controller(server)

    input()


if __name__ == "__main__":
    main()
