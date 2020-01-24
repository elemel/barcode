from collections import defaultdict, deque
from fractions import Fraction as Q

from barcode.operations import MNEMONIC_TO_OPCODE, OPCODE_TO_OPERATION
from barcode.register import Register
from barcode.sparse_dict import SparseDict
from barcode.stdio import StandardStream

IR = Register.INSTRUCTION.value - 1
SR = Register.STACK.value - 1
FR = Register.FRAME.value - 1
GR = Register.GARBAGE.value - 1
HR = Register.HEAP.value - 1

HCF = MNEMONIC_TO_OPCODE['hcf']

STDIN = Q(StandardStream.INPUT.value)
STDOUT = Q(StandardStream.OUTPUT.value)


class Process:
    def __init__(self, machine_code=[], args=[]):
        self.registers = len(Register) * [Q(0)]
        self.memory = SparseDict(default=Q(0))
        self.streams = defaultdict(deque)

        for i, q in enumerate(machine_code):
            self.memory[Q(i)] = q

        self.registers[IR] = Q(0)
        self.registers[GR] = Q(1, 2)
        self.registers[HR] = Q(1, 3)

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

    # TODO: Allocate 1/3, 2/3, 1/4, 3/4, 1/5, 2/5, 3/5, 4/5, 1/6, 5/6, 1/7, ...
    def new(self):
        if self.registers[GR] > 1:
            self.registers[GR] -= 1
            return self.memory[self.registers[GR]]

        result = self.registers[HR]
        self.registers[HR] = Q(1, self.registers[HR].denominator + 1)
        return result

    def delete(self, array):
        self.memory[self.memory[PR]] = array
        self.memory[PR] += 1

    def step(self):
        opcode = self.memory[self.registers[IR]]

        if opcode.denominator == HCF:
            return False

        operation = OPCODE_TO_OPERATION[opcode.denominator]
        operation(self)
        self.registers[IR] += 1
        return True

    def run(self):
        while self.step():
            pass

    def readLine(self, file_descriptor=STDOUT):
        chars = []
        stream = self.streams[file_descriptor]

        while stream:
            char = chr(int(stream.popleft()))
            chars.append(char)

            if char == '\n':
                break

        return ''.join(chars)
