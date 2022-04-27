import math
import socket
import threading
import time

import gpiozero
from stationary_controller.mode import Mode
from tools.agv_socket import AgvSocket
from tools.agv_tools import AgvTools

from agv_command import AgvCommand
from instructions import Instruction

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

        server.start_server(self.shared_list, self.mutex_shared_list)

        direction_gpio_bcm = 18
        left_motor_gpio_bcm = 24
        right_motor_gpio_bcm = 23

        freq = AgvTools.calc_pulse_freq(velocity=2.25)
        duty_cycle = 1

        # self.direction = gpiozero.OutputDevice(direction_gpio_bcm)
        # self.left_motor = gpiozero.PWMOutputDevice(
        #     left_motor_gpio_bcm, initial_value=duty_cycle, frequency=freq
        # )
        # self.right_motor = gpiozero.PWMOutputDevice(
        #     right_motor_gpio_bcm, initial_value=duty_cycle, frequency=freq
        # )

        message_handler = threading.Thread(target=self.shared_list_handler)
        inst_handler = threading.Thread(target=self.instruction_handler)
        message_handler.start()
        inst_handler.start()

    def shared_list_handler(self):
        while self.server.connected:
            if not len(self.shared_list) > 0:
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
        # print(msg)
        if len(msg) != 2:
            em = f"[INVALID COMMAND] Expected 2 words, but got {len(msg)}."
            self.server.send_message(em)
            return

        if msg[0] == "SETMODE":
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
            # print()
            self.server.send_message(em)
            return

        # TODO: FInd the actual command corresponding with the msg
        inst = Instruction(command=msg[0], value=msg[1])
        # self.server.send_message(AgvCommand.valid_command.value)

        return inst

    def instruction_handler(self):
        while self.server.connected:
            if not len(self.instructions) > 0:
                continue

            self.mutex_shared_list.acquire()
            inst = self.instructions.pop(0)
            self.mutex_shared_list.release()

            self.execute_instruction(inst)

    def execute_instruction(self, instruction: Instruction):
        command = instruction.command
        value = instruction.value

        print(command, value)

        if command == AgvCommand.forward.value:
            acceleration_freqs = self.accelerate()
            # self.direction.on()

            # freq1 = acceleration_freqs.pop(0)
            # self.right_motor.frequency = freq1
            # self.right_motor.frequency = freq1
            # self.right_motor.blink()
            # self.left_motor.blink()

            # for freq in acceleration_freqs:
            #     self.right_motor.frequency = freq
            #     self.left_motor.frequency = freq
            #     send_n_pulses = 2
            #     sleep_time = round(1 / freq * send_n_pulses, 5)
            #     time.sleep(sleep_time)

            # self.right_motor.off()
            # self.left_motor.off()

        elif command == AgvCommand.backward.value:
            deceleration_freqs = self.accelerate(is_decelerating=True)

        elif command == AgvCommand.rotate_cw.value:
            pass
        elif command == AgvCommand.rotate_ccw.value:
            pass
        elif command == AgvCommand.calibrate_home.value:
            pass

    def accelerate(self, is_decelerating: bool = False) -> list[int]:
        steps = 10
        v_inc = float(self.velocity / steps)

        frequencies = []

        for i in range(1, steps + 1):
            cur_v = v_inc * i
            freq = AgvTools.calc_pulse_freq(cur_v)
            frequencies.append(freq)

        if is_decelerating:
            frequencies.reverse()

        return frequencies

    def emergency_stop(self):
        # stop everything, then clear instruction list.
        return


def main():
    PORT = 1234
    SERVER = socket.gethostbyname(socket.gethostname() + ".local")

    server = AgvSocket(ip=SERVER, port=PORT, isServer=True)

    ctrl = Controller(server)


if __name__ == "__main__":
    main()
