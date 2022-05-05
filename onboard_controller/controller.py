import socket
import threading

import pigpio
from stationary_controller.mode import Mode
from tools.agv_socket import AgvSocket
from tools.agv_tools import AgvTools

from onboard_controller.agv_command import AgvCommand
from onboard_controller.instructions import Instruction

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

        self.DIRECTION_GPIO_BCM = 18
        self.MOTOR_GPIO_BCM = 24

        # Note: must first run "sudo pigpiod -t 0" in pi terminal.
        self.pi = pigpio.pi()

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
            self.server.send_message(em)
            return

        inst = Instruction(command=msg[0], value=float(msg[1]))
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

        print(command, value, type(command), type(value))

        if command == AgvCommand.forward.value:
            ramp_inputs = AgvTools.create_ramp_inputs(inches=value)
            AgvTools.generate_ramp(
                pi=self.pi,
                ramp=ramp_inputs,
                motor_pin=self.MOTOR_GPIO_BCM,
                clear_waves=True,
            )
        elif command == AgvCommand.backward.value:
            pass
        elif command == AgvCommand.rotate_cw.value:
            pass
        elif command == AgvCommand.rotate_ccw.value:
            pass
        elif command == AgvCommand.calibrate_home.value:
            pass

    def emergency_stop(self):
        # stop everything, then clear instruction list.
        self.pi.wave_clear()
        return


def main():
    PORT = 1234
    SERVER = socket.gethostbyname(socket.gethostname() + ".local")

    server = AgvSocket(ip=SERVER, port=PORT, isServer=True)

    ctrl = Controller(server)


if __name__ == "__main__":
    main()
