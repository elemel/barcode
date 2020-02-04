from enum import Enum
from fractions import Fraction as Q

from underbar.register import Register

IR = Register.INSTRUCTION.value
JR = Register.JUMP.value
SR = Register.STACK.value
FR = Register.FRAME.value

DENOMINATOR_TO_OPERATION = {}
MNEMONIC_TO_OPCODE = {}
OPCODE_TO_OPERATION = {}


class BlockedError(Exception):
    pass


class TerminatedError(Exception):
    pass


def operation(opcode, mnemonic=None):
    def decorate(func):
        nonlocal mnemonic
        mnemonic = mnemonic or func.__name__

        if opcode.denominator in DENOMINATOR_TO_OPERATION:
            raise ValueError(f'Duplicate denominator: {opcode.denominator}')

        if mnemonic in MNEMONIC_TO_OPCODE:
            raise ValueError(f'Duplicate mnemonic: {mnemonic}')

        if opcode in OPCODE_TO_OPERATION:
            raise ValueError(f'Duplicate opcode: {opcode}')

        DENOMINATOR_TO_OPERATION[opcode.denominator] = func
        MNEMONIC_TO_OPCODE[mnemonic] = opcode
        OPCODE_TO_OPERATION[opcode] = func
        return func

    return decorate


@operation(Q(1, 81))
def add(process):
    process.push(process.pop() + process.pop())


@operation(Q(1, 173), 'bal')
def branch_always(process):
    opcode = process.memory[process.registers[IR]]
    address = opcode.numerator // opcode.denominator
    process.registers[JR] = address


@operation(Q(1, 252), 'beq')
def branch_equal(process):
    opcode = process.memory[process.registers[IR]]
    address = opcode.numerator // opcode.denominator

    if not process.pop():
        process.registers[JR] = address


@operation(Q(1, 164), 'cal')
def call(process):
    address = process.pop()

    process.push(process.registers[JR]) # return address
    process.push(process.registers[FR])

    process.registers[JR] = address
    process.registers[FR] = process.registers[SR]


@operation(Q(1, 9), 'dec')
def decrement(process):
    process.push(process.pop() - 1)


@operation(Q(1, 211), 'del')
def delete(process):
    process.memory.delete(process.pop())


@operation(Q(1, 171), 'den')
def denominator(process):
    process.push(Q(process.pop().denominator))


@operation(Q(1, 76), 'div')
def divide(process):
    process.push(process.pop() / process.pop())


@operation(Q(1, 236), 'dup')
def duplicate(process):
    value = process.pop()

    process.push(value)
    process.push(value)


@operation(Q(1, 214))
def get(process):
    handle = process.pop()
    stream = process.streams[handle]

    if not stream:
        raise BlockedError()

    process.push(stream.popleft())


@operation(Q(1, 255), 'hcf')
def halt(process):
    raise TerminatedError()


@operation(Q(1, 143), 'inc')
def increment(process):
    process.push(process.pop() + 1)


@operation(Q(1, 49), 'inv')
def invert(process):
    process.push(1 / process.pop())


@operation(Q(0), 'ldi')
def load_integer(process):
    process.push(Q(process.memory[process.registers[IR]].numerator))


@operation(Q(1, 239), 'ldl')
def load_local(process):
    opcode = process.memory[process.registers[IR]]
    index = opcode.numerator // opcode.denominator
    process.push(process.memory[process.registers[FR] + index])


@operation(Q(1, 18), 'ldm')
def load_memory(process):
    address = process.pop()
    process.push(process.memory[address])


@operation(Q(1, 241), 'ldp')
def load_parameter(process):
    opcode = process.memory[process.registers[IR]]
    index = opcode.numerator // opcode.denominator
    process.push(process.memory[process.registers[FR] - (index + 3)])


@operation(Q(1, 227), 'ldr')
def load_register(process):
    opcode = process.memory[process.registers[IR]]
    index = opcode.numerator // opcode.denominator
    process.push(process.memory[index])


@operation(Q(1, 107), 'mul')
def multiply(process):
    process.push(process.pop() * process.pop())


@operation(Q(1, 147), 'neg')
def negate(process):
    process.push(-process.pop())


@operation(Q(1, 33))
def new(process):
    process.push(process.memory.new(process.pop()))


@operation(Q(1, 222), 'num')
def numerator(process):
    process.push(Q(process.pop().numerator))


@operation(Q(1, 245))
def put(process):
    handle = process.pop()
    stream = process.streams[handle]
    stream.append(process.pop())


@operation(Q(1, 193), 'ret')
def return_(process):
    process.registers[SR] = process.registers[FR]
    process.registers[FR] = process.pop()
    process.registers[JR] = process.pop()


@operation(Q(1, 251), 'stl')
def store_local(process):
    opcode = process.memory[process.registers[IR]]
    index = opcode.numerator // opcode.denominator
    process.memory[process.registers[FR] + index] = process.pop()


@operation(Q(1, 125), 'stm')
def store_memory(process):
    address = process.pop()
    process.memory[address] = process.pop()


@operation(Q(1, 233), 'stp')
def store_parameter(process):
    opcode = process.memory[process.registers[IR]]
    index = opcode.numerator // opcode.denominator
    process.memory[process.registers[FR] - (index + 3)] = process.pop()


@operation(Q(1, 229), 'str')
def store_register(process):
    opcode = process.memory[process.registers[IR]]
    index = opcode.numerator // opcode.denominator
    process.registers[index] = process.pop()


@operation(Q(1, 183), 'sub')
def subtract(process):
    process.push(process.pop() - process.pop())


@operation(Q(1, 3), 'swp')
def swap(process):
    a = process.pop()
    b = process.pop()

    process.push(a)
    process.push(b)

@operation(Q(1, 223), 'top')
def top(process):
    opcode = process.memory[process.registers[IR]]
    offset = opcode.numerator // opcode.denominator
    process.registers[SR] += offset
