from collections import defaultdict, deque
from fractions import Fraction as Q
from sys import maxsize

from underbar.memory import Memory
from underbar.operations import MNEMONIC_TO_OPCODE, DENOMINATOR_TO_OPERATION
from underbar.register import Register
from underbar.stdio import StandardStream

IR = Register.INSTRUCTION.value
JR = Register.JUMP.value
SR = Register.STACK.value
FR = Register.FRAME.value

HCF_DENOMINATOR = MNEMONIC_TO_OPCODE['hcf'].denominator

STDIN = Q(StandardStream.INPUT.value)
STDOUT = Q(StandardStream.OUTPUT.value)


class Process:
    def __init__(self, machine_code=[], args=[]):
        self.registers = len(Register) * [Q(0)]
        self.memory = Memory(1024)
        self.streams = defaultdict(deque)

        for i, q in enumerate(machine_code):
            self.memory[Q(i)] = q

        self.registers[IR] = Q(0)
        self.registers[JR] = Q(0)
        self.registers[SR] = self.new()
        self.registers[FR] = self.registers[SR]

        args_address = self.new()

        for i, arg in enumerate(args):
            arg_address = self.new()

            for j, char in enumerate(arg):
                self.memory[arg_address + j] = Q(ord(char))

            self.memory[arg_address + len(arg)] = Q(0)
            self.memory[args_address + i] = arg_address

        self.push(args_address) # argv
        self.push(Q(len(args))) # argc
        self.push(Q(0)) # return value (exit code)

    def push(self, value):
        self.memory[self.registers[SR]] = value
        self.registers[SR] += 1

    def pop(self):
        self.registers[SR] -= 1
        return self.memory[self.registers[SR]]

    def peek(self):
        return self.memory[self.registers[SR] - 1]

    def new(self):
        return self.memory.new(1024)

    def delete(self, array):
        self.memory.delete(array)

    def step(self):
        denominator = self.memory[self.registers[IR]].denominator

        if denominator == HCF_DENOMINATOR:
            return False

        operation = DENOMINATOR_TO_OPERATION[denominator]
        self.registers[JR] = self.registers[IR] + 1
        operation(self)
        self.registers[IR] = self.registers[JR]
        return True

    def run(self):
        while self.step():
            pass

    def readLine(self, handle=STDOUT):
        chars = []
        stream = self.streams[handle]

        while stream:
            char = chr(int(stream.popleft()))
            chars.append(char)

            if char == '\n':
                break

        return ''.join(chars)
