from collections import defaultdict, deque
from fractions import Fraction as Q
from sys import maxsize

from underbar.operations import MNEMONIC_TO_OPCODE, DENOMINATOR_TO_OPERATION
from underbar.register import Register
from underbar.sparse_dict import SparseDict
from underbar.stdio import StandardStream

IR = Register.INSTRUCTION.value
JR = Register.JUMP.value
SR = Register.STACK.value
FR = Register.FRAME.value

HCF_DENOMINATOR = MNEMONIC_TO_OPCODE['hcf'].denominator

STDIN = Q(StandardStream.INPUT.value)
STDOUT = Q(StandardStream.OUTPUT.value)


def generate_rationals(q=Q(0)):
    assert 0 <= q < 1

    yield q
    dq = Q(1, q.denominator)

    while True:
        q += dq

        if q.numerator == q.denominator:
            dq = Q(1, dq.denominator + 1)
            q = dq
            yield q
        elif q.denominator == dq.denominator:
            yield q


class Process:
    def __init__(self, machine_code=[], args=[]):
        self.registers = len(Register) * [Q(0)]
        self.memory = SparseDict(default=Q(0))
        self.streams = defaultdict(deque)
        self.rationals = generate_rationals(Q(1, 2))
        self.pool = []

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

    # TODO: Allocate 1/3, 2/3, 1/4, 3/4, 1/5, 2/5, 3/5, 4/5, 1/6, 5/6, 1/7, ...
    def new(self):
        if self.pool:
            return self.pool.pop()

        return next(self.rationals)

    def delete(self, array):
        self.pool.append(array)

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
