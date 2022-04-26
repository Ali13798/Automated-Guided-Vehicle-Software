import threading

from stationary_controller.mode import Mode
from tools.agv_socket import AgvSocket
from tools.agv_tools import AgvTools as agv_tools

from onboard_controller.agv_command import AgvCommand
from onboard_controller.instructions import Instruction


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

        message_handler = threading.Thread(target=self.shared_list_handler)
        message_handler.start()
        inst_handler = threading.Thread(target=self.instruction_handler)
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
        pass

    def emergency_stop(self):
        # stop everything, then clear instruction list.
        return


def main():
    print(agv_tools.calc_pulse_freq(velocity=2.25))

    dist = 10
    print(agv_tools.calc_pulse_num(dist))


if __name__ == "__main__":
    main()
