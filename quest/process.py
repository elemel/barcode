from collections import defaultdict, deque
from fractions import Fraction as Q
from math import floor

from quest.memory import Memory
from quest.operations import BlockedError, TerminatedError, OPERATIONS
from quest.register import Register
from quest.stdio import StandardStream
from quest.utils import fraction_to_index

IR = Register.IR.value
DR = Register.DR.value
CR = Register.CR.value

STDIN = StandardStream.STDIN.value
STDOUT = StandardStream.STDOUT.value
STDERR = StandardStream.STDERR.value


class Process:
    def __init__(self, machine_code: list = [], argv: list = []) -> None:
        self.registers = len(Register) * [Q(0)]
        self.memory = Memory()

        self.registers[IR] = self.memory.new()
        self.registers[DR] = self.memory.new()
        self.registers[CR] = self.memory.new()

        self.streams = [deque() for _ in StandardStream]

        for instruction in machine_code:
            self.memory.push(Q(0), instruction)

        argv_base = self.memory.new()

        for arg in argv:
            arg_base = self.memory.new()

            for char in arg:
                self.memory.push(arg_base, Q(ord(char)))

            self.memory.push(argv_base, arg_base)

        self.push_data(argv_base)

    def push_data(self, value: Q) -> None:
        self.memory.push(self.registers[DR], value)

    def pop_data(self) -> Q:
        return self.memory.pop(self.registers[DR])

    def push_call(self, value: Q) -> None:
        self.memory.push(self.registers[CR], value)

    def pop_call(self) -> Q:
        return self.memory.pop(self.registers[CR])

    def step(self) -> None:
        instruction = self.memory[self.registers[IR]]
        self.registers[IR] += 1
        operand, opcode = divmod(instruction, 1)
        index = fraction_to_index(opcode)
        func = OPERATIONS[index]
        func(self, operand)

    def run(self) -> bool:
        try:
            while True:
                self.step()
        except BlockedError:
            return True
        except TerminatedError:
            return False

    def read(self, handle: int = STDOUT) -> str:
        chars = []
        stream = self.streams[handle]

        while stream:
            char = chr(floor(stream.popleft()))
            chars.append(char)

        return ''.join(chars)

    def write(self, s, handle: int = STDIN) -> None:
        stream = self.streams[handle]

        for c in s:
            stream.append(Q(ord(c)))

    def print_stack(self, base):
        for offset in range(self.memory.size(base)):
            address = base + offset
            print(f'{address}: {self.memory[address]}')
