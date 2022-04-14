import math
import threading

from agv_command import AgvCommand
from agv_tools import AgvTools as agv_tools
from instructions import Instruction
from mode import Mode


class Controller:
    def __init__(self) -> None:
        self.mode = Mode.Unselected

        self.mutex = threading.Lock()
        self.instructions: list[Instruction] = []
        self.valid_commands = [cmd.value for cmd in AgvCommand]

    def establish_connection(self):
        pass

    def add_instruction(self, inst: Instruction) -> None:
        self.mutex.acquire()
        self.instructions.append(inst)
        self.mutex.release()

    def consume_instruction(self) -> Instruction:
        self.mutex.acquire()
        inst = self.instructions.pop(0)
        self.mutex.release()
        return inst

    def parse_message(self, msg: str) -> Instruction | None:
        msg = msg.split()
        msg = [n.upper() for n in msg]
        # print(msg)
        if len(msg) != 2:
            print(f"[INVALID COMMAND] Expected 2 words, but got {len(msg)}.")
            self.send_message(AgvCommand.invalid_command.value)
            return

        if msg[0] not in self.valid_commands:
            print(f'[INVALID COMMAND] command "{msg[0]}" is not valid.')
            self.send_message(AgvCommand.invalid_command.value)
            return

        try:
            int(msg[1])
        except ValueError:
            print(
                f'[INVALID COMMAND] expected a number as second term, but got "{msg[1]}."'
            )
            self.send_message(AgvCommand.invalid_command.value)
            return

        # TODO: FInd the actual command corresponding with the msg
        inst = Instruction(command=msg[0], value=msg[1])
        self.send_message(AgvCommand.valid_command.value)

        return inst

    def instruction_handler(self):
        while True:
            self.mutex.acquire()
            n = len(self.instructions)
            if n > 0:
                # process instruction then pop
                pass

            self.mutex.release()

    def emergency_stop(self):
        # stop everything, then clear instruction list.
        return


def main():
    print(agv_tools.calc_pulse_freq(velocity=2.25))

    dist = 10
    print(agv_tools.calc_pulse_num(dist))


if __name__ == "__main__":
    main()
