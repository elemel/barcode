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
def add(process, operand):
    process.push(process.pop() + process.pop())


@operation(Q(1, 173), 'bal')
def branch_always(process, operand):
    process.registers[JR] = operand


@operation(Q(1, 252), 'beq')
def branch_equal(process, operand):
    if not process.pop():
        process.registers[JR] = operand


@operation(Q(1, 164), 'cal')
def call(process, operand):
    address = process.pop()

    process.push(process.registers[JR]) # return address
    process.push(process.registers[FR])

    process.registers[JR] = address
    process.registers[FR] = process.registers[SR]


@operation(Q(1, 9), 'dec')
def decrement(process, operand):
    process.push(process.pop() - 1)


@operation(Q(1, 211), 'del')
def delete(process, operand):
    process.memory.delete(process.pop())


@operation(Q(1, 171), 'den')
def denominator(process, operand):
    process.push(Q(process.pop().denominator))


@operation(Q(1, 76), 'div')
def divide(process, operand):
    process.push(process.pop() / process.pop())


@operation(Q(1, 236), 'dup')
def duplicate(process, operand):
    value = process.pop()

    process.push(value)
    process.push(value)


@operation(Q(1, 214))
def get(process, operand):
    stream = process.streams[process.peek()]

    if not stream:
        raise BlockedError()

    process.pop()
    process.push(stream.popleft())


@operation(Q(1, 255), 'hcf')
def halt(process, operand):
    raise TerminatedError()


@operation(Q(1, 143), 'inc')
def increment(process, operand):
    process.push(process.pop() + 1)


@operation(Q(1, 49), 'inv')
def invert(process, operand):
    process.push(1 / process.pop())


@operation(Q(0), 'ldi')
def load_integer(process, operand):
    process.push(Q(operand))


@operation(Q(1, 239), 'ldl')
def load_local(process, operand):
    process.push(process.memory[process.registers[FR] + operand])


@operation(Q(1, 18), 'ldm')
def load_memory(process, operand):
    process.push(process.memory[process.pop()])


@operation(Q(1, 241), 'ldp')
def load_parameter(process, operand):
    process.push(process.memory[process.registers[FR] - (operand + 3)])


@operation(Q(1, 227), 'ldr')
def load_register(process, operand):
    process.push(process.registers[operand])


@operation(Q(1, 107), 'mul')
def multiply(process, operand):
    process.push(process.pop() * process.pop())


@operation(Q(1, 147), 'neg')
def negate(process, operand):
    process.push(-process.pop())


@operation(Q(1, 33))
def new(process, operand):
    process.push(process.memory.new(process.pop()))


@operation(Q(1, 222), 'num')
def numerator(process, operand):
    process.push(Q(process.pop().numerator))


@operation(Q(1, 245))
def put(process, operand):
    stream = process.streams[process.pop()]
    stream.append(process.pop())


@operation(Q(1, 193), 'ret')
def return_(process, operand):
    process.registers[SR] = process.registers[FR]
    process.registers[FR] = process.pop()
    process.registers[JR] = process.pop()


@operation(Q(1, 251), 'stl')
def store_local(process, operand):
    process.memory[process.registers[FR] + operand] = process.pop()


@operation(Q(1, 125), 'stm')
def store_memory(process, operand):
    address = process.pop()
    process.memory[address] = process.pop()


@operation(Q(1, 233), 'stp')
def store_parameter(process, operand):
    process.memory[process.registers[FR] - (operand + 3)] = process.pop()


@operation(Q(1, 229), 'str')
def store_register(process, operand):
    process.registers[operand] = process.pop()


@operation(Q(1, 183), 'sub')
def subtract(process, operand):
    process.push(process.pop() - process.pop())


@operation(Q(1, 3), 'swp')
def swap(process, operand):
    a = process.pop()
    b = process.pop()

    process.push(a)
    process.push(b)

@operation(Q(1, 223), 'top')
def top(process, operand):
    process.registers[SR] += operand
