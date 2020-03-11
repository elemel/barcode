from collections import defaultdict, deque
from fractions import Fraction as Q
from math import floor
from sys import maxsize

from underbar.memory import Memory

from underbar.operations import (
    BlockedError, TerminatedError, MNEMONIC_TO_OPCODE, OPCODE_TO_OPERATION)

from underbar.register import Register
from underbar.stdio import StandardStream

PR = Register.PR.value
DR = Register.DR.value
CR = Register.CR.value

STDIN = Q(StandardStream.STDIN.value)
STDOUT = Q(StandardStream.STDOUT.value)


class Process:
    def __init__(self, machine_code=[], args=[]):
        self.registers = len(Register) * [Q(0)]
        self.memory = Memory(len(machine_code))
        self.streams = {handle.value: deque() for handle in StandardStream}

        for i, q in enumerate(machine_code):
            self.memory[Q(i)] = q

        self.registers[PR] = Q(0)
        self.registers[DR] = self.memory.new(1024)
        self.registers[CR] = self.memory.new(1024)

        args_address = self.memory.new(len(args))

        for i, arg in enumerate(args):
            arg_address = self.memory.new(len(arg) + 1)

            for j, char in enumerate(arg):
                self.memory[arg_address + j] = Q(ord(char))

            self.memory[arg_address + len(arg)] = Q(0)
            self.memory[args_address + i] = arg_address

        self.push_data(args_address) # argv
        self.push_data(Q(len(args))) # argc

    def push_data(self, value: Q):
        self.memory[self.registers[DR]] = value
        self.registers[DR] += 1

    def pop_data(self):
        self.registers[DR] -= 1
        return self.memory[self.registers[DR]]

    def push_call(self, value: Q):
        self.memory[self.registers[CR]] = value
        self.registers[CR] += 1

    def pop_call(self):
        self.registers[CR] -= 1
        return self.memory[self.registers[CR]]

    def peek(self):
        return self.memory[self.registers[DR] - 1]

    def step(self):
        opcode = self.memory[self.registers[PR]]
        self.registers[PR] += 1
        operand, opcode = divmod(opcode, 1)
        operation = OPCODE_TO_OPERATION[opcode]
        operation(self, operand)

    def run(self):
        try:
            while True:
                self.step()
        except BlockedError:
            return True
        except TerminatedError:
            return False

    def readLine(self, handle=STDOUT):
        chars = []
        stream = self.streams[handle]

        while stream:
            char = chr(floor(stream.popleft()))
            chars.append(char)

            if char == '\n':
                break

        return ''.join(chars)

    def write(self, s, handle=STDIN):
        stream = self.streams[handle]

        for c in s:
            stream.append(Q(ord(c)))

    def close(self, handle=STDIN):
        stream = self.streams[handle]
        stream.append(None)
