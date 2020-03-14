from collections import defaultdict, deque
from fractions import Fraction as Q
from math import floor

from quest.memory import Memory

from quest.operations import (
    BlockedError, TerminatedError, MNEMONIC_TO_OPCODE, OPCODE_TO_OPERATION)

from quest.register import Register
from quest.stdio import StandardStream

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

        self.memory.new() # stdin = 2/3
        self.memory.new() # stdout = 1/4
        self.memory.new() # stderr = 3/4

        for i, q in enumerate(machine_code):
            self.memory.put(Q(0), q)

        argv_key = self.memory.new()

        for arg in argv:
            arg_key = self.memory.new()

            for char in arg:
                self.memory.put(arg_key, Q(ord(char)))

            self.memory.put(argv_key, arg_key)

        self.push_data(argv_key) # argv

    def push_data(self, value: Q) -> None:
        self.memory.put(self.registers[DR], value)

    def pop_data(self) -> Q:
        return self.memory.unput(self.registers[DR])

    def push_call(self, value: Q) -> None:
        self.memory.unget(self.registers[CR], value)

    def pop_call(self) -> Q:
        return self.memory.get(self.registers[CR])

    def step(self) -> None:
        opcode = self.memory[self.registers[IR]]
        self.registers[IR] += 1
        operand, opcode = divmod(opcode, 1)
        operation = OPCODE_TO_OPERATION[opcode]
        operation(self, operand)

    def run(self) -> bool:
        try:
            while True:
                self.step()
        except BlockedError:
            return True
        except TerminatedError:
            return False

    def read_line(self, handle: Q = STDOUT) -> str:
        chars = []

        while self.memory.size(handle):
            char = chr(floor(self.memory.get(handle)))
            chars.append(char)

            if char == '\n':
                break

        return ''.join(chars)

    def write(self, s, handle: Q = STDIN) -> None:
        for c in s:
            self.memory.put(handle, Q(ord(c)))

    def close(self, handle: Q = STDIN) -> None:
        self.memory.put(handle, Q(4)) # EOT

    def print_queue(self, key):
        for i in range(self.memory.size(key)):
            print(i, self.memory[key + i])
