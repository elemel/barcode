from collections import defaultdict, deque
from fractions import Fraction as Q

from serviam import operations
from serviam.opcode import Opcode
from serviam.register import Register
from serviam.sparse_dict import SparseDict
from serviam.standard_stream import StandardStream

IR = Register.INSTRUCTION.value
SR = Register.STACK.value
FR = Register.FRAME.value
GR = Register.GARBAGE.value
HR = Register.HEAP.value

HALT = Opcode.HALT.value

STDIN = StandardStream.INPUT.value
STDOUT = StandardStream.OUTPUT.value

DENOMINATOR_TO_OPERATION = {
    opcode.value.denominator:
    getattr(operations, 'return_' if opcode.name == 'RETURN' else opcode.name.lower())
    for opcode in Opcode
}


class Process:
    def __init__(self, machine_code=[], args=[]):
        self.registers = len(Register) * [Q(0)]
        self.memory = SparseDict(default=Q(0))
        self.streams = defaultdict(deque)

        for i, q in enumerate(machine_code, start=1):
            self.memory[Q(i)] = q

        self.registers[IR] = Q(1)
        self.registers[GR] = Q(1, 2)
        self.registers[HR] = Q(1, 3)

        self.registers[SR] = self.allocate()
        self.registers[FR] = self.registers[SR]

        args_address = self.allocate()

        for i, arg in enumerate(args):
            arg_address = self.allocate()

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

    def allocate(self):
        if self.registers[GR] > 1:
            self.registers[GR] -= 1
            return self.memory[self.registers[GR]]

        result = self.registers[HR]
        self.registers[HR] = Q(1, self.registers[HR].denominator + 1)
        return result

    def deallocate(self, array):
        self.memory[self.memory[PR]] = array
        self.memory[PR] += 1

    def step(self):
        opcode = self.memory[self.registers[IR]]

        if opcode == HALT:
            return False

        operation = DENOMINATOR_TO_OPERATION[opcode.denominator]
        operation(self)
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
