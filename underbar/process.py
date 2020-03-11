from collections import defaultdict, deque
from fractions import Fraction as Q
from math import floor
from sys import maxsize

from underbar.memory import Memory

from underbar.operations import (
    BlockedError, TerminatedError, MNEMONIC_TO_OPCODE, OPCODE_TO_OPERATION)

from underbar.register import Register
from underbar.stdio import StandardStream

IR = Register.IR.value
SR = Register.SR.value

STDIN = Q(StandardStream.STDIN.value)
STDOUT = Q(StandardStream.STDOUT.value)


class Process:
    def __init__(self, machine_code: list = [], args: list = []) -> None:
        self.registers = len(Register) * [Q(0)]
        self.memory = Memory(len(machine_code))
        self.streams = {handle.value: deque() for handle in StandardStream}

        for i, q in enumerate(machine_code):
            self.memory[Q(i)] = q

        self.registers[IR] = Q(0)
        self.registers[SR] = self.memory.new(0)

        args_address = self.memory.new(len(args))

        for i, arg in enumerate(args):
            arg_address = self.memory.new(len(arg) + 1)

            for j, char in enumerate(arg):
                self.memory[arg_address + j] = Q(ord(char))

            self.memory[arg_address + len(arg)] = Q(0)
            self.memory[args_address + i] = arg_address

        self.push_data(args_address) # argv
        self.push_data(Q(len(args))) # argc

    def push_data(self, value: Q) -> None:
        self.memory.put(self.registers[SR], value)

    def pop_data(self) -> Q:
        return self.memory.unput(self.registers[SR])

    def push_call(self, value: Q) -> None:
        self.memory.unget(self.registers[SR], value)

    def pop_call(self) -> Q:
        return self.memory.get(self.registers[SR])

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
        stream = self.streams[handle]

        while stream:
            char = chr(floor(stream.popleft()))
            chars.append(char)

            if char == '\n':
                break

        return ''.join(chars)

    def write(self, s, handle: Q = STDIN) -> None:
        stream = self.streams[handle]

        for c in s:
            stream.append(Q(ord(c)))

    def close(self, handle: Q = STDIN) -> None:
        stream = self.streams[handle]
        stream.append(None)
