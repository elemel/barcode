from enum import Enum
from fractions import Fraction as Q

from underbar.register import Register

IR = Register.IR.value
JR = Register.JR.value
DR = Register.DR.value
CR = Register.CR.value

DENOMINATOR_TO_OPERATION = {}
MNEMONIC_TO_OPCODE = {}
OPCODE_TO_OPERATION = {}


class BlockedError(Exception):
    pass


class ClosedError(Exception):
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
    right = process.pop()
    left = process.pop()

    process.push(left + right)


@operation(Q(1, 173), 'bal')
def branch_always(process, operand):
    process.registers[JR] = operand


@operation(Q(1, 252), 'beq')
def branch_equal(process, operand):
    if not process.pop():
        process.registers[JR] = operand


@operation(Q(1, 7), 'bge')
def branch_greater_equal(process, operand):
    if process.pop() >= 0:
        process.registers[JR] = operand


@operation(Q(1, 51), 'bgt')
def branch_greater_than(process, operand):
    if process.pop() > 0:
        process.registers[JR] = operand


@operation(Q(1, 55), 'ble')
def branch_less_equal(process, operand):
    if process.pop() <= 0:
        process.registers[JR] = operand


@operation(Q(1, 248), 'blt')
def branch_less_than(process, operand):
    if process.pop() < 0:
        process.registers[JR] = operand


@operation(Q(1, 106), 'bne')
def branch_not_equal(process, operand):
    if process.pop():
        process.registers[JR] = operand


@operation(Q(1, 164), 'cal')
def call(process, operand):
    function = process.pop()
    process.push_frame(process.registers[JR])
    process.registers[JR] = function


@operation(Q(1, 213), 'clo')
def call_operand(process, operand):
    process.push_frame(process.registers[JR])
    process.registers[JR] = operand


@operation(Q(1, 9), 'dec')
def decrement(process, operand):
    value = process.pop()
    process.push(value - 1)


@operation(Q(1, 211), 'del')
def delete(process, operand):
    array = process.pop()
    process.memory.delete(array)


@operation(Q(1, 171), 'den')
def denominator(process, operand):
    value = process.pop()
    value = Q(value.denominator)
    process.push(value)


@operation(Q(1, 76), 'div')
def divide(process, operand):
    right = process.pop()
    left = process.pop()

    process.push(left / right)


@operation(Q(1, 236), 'dup')
def duplicate(process, operand):
    value = process.pop()

    process.push(value)
    process.push(value)


@operation(Q(1, 115), 'ent')
def enter(process, operand):
    process.registers[CR] += operand


@operation(Q(1, 206), 'flr')
def duplicate(process, operand):
    value = process.pop()
    value //= 1
    process.push(value)


@operation(Q(1, 214))
def get(process, operand):
    handle = process.peek()
    stream = process.streams[handle]

    if not stream:
        # User can provide input and resume
        raise BlockedError()

    if stream[0] is None:
        # End of file
        raise ClosedError()

    process.pop()
    value = stream.popleft()
    process.push(value)


@operation(Q(1, 255), 'hcf')
def halt(process, operand):
    raise TerminatedError()


@operation(Q(1, 143), 'inc')
def increment(process, operand):
    value = process.pop()
    process.push(value + 1)


@operation(Q(1, 49), 'inv')
def invert(process, operand):
    value = process.pop()
    process.push(1 / value)


@operation(Q(1, 239), 'ldl')
def load_local(process, operand):
    address = process.registers[CR] - 1 - operand
    value = process.memory[address]
    process.push(value)


@operation(Q(1, 18), 'ldm')
def load_memory(process, operand):
    address = process.pop() + operand
    value = process.memory[address]
    process.push(value)


@operation(Q(0), 'ldo')
def load_operand(process, operand):
    process.push(Q(operand))


@operation(Q(1, 227), 'ldr')
def load_register(process, operand):
    value = process.registers[operand]
    process.push(value)


@operation(Q(1, 200), 'mod')
def modulo(process, operand):
    right = process.pop()
    left = process.pop()

    process.push(left % right)


@operation(Q(1, 107), 'mul')
def multiply(process, operand):
    right = process.pop()
    left = process.pop()

    process.push(left * right)


@operation(Q(1, 147), 'neg')
def negate(process, operand):
    process.push(-process.pop())


@operation(Q(1, 33))
def new(process, operand):
    size = process.pop()
    array = process.memory.new(size)
    process.push(array)


@operation(Q(1, 222), 'num')
def numerator(process, operand):
    value = process.pop()
    value = Q(value.numerator)
    process.push(value)


@operation(Q(1, 245))
def put(process, operand):
    handle = process.pop()
    value = process.pop()

    stream = process.streams[handle]
    stream.append(value)


@operation(Q(1, 193), 'ret')
def return_(process, operand):
    process.registers[CR] -= operand
    process.registers[JR] = process.pop_frame()


@operation(Q(1, 2), 'siz')
def size(process, operand):
    handle = process.pop()
    stream = process.streams[handle]
    size = len(stream)
    
    if size and stream[0] is None:
        size -= 1

        if not size:
            size -= 1

    process.push(Q(size))


@operation(Q(1, 251), 'stl')
def store_local(process, operand):
    address = process.registers[CR] - 1 - operand
    value = process.pop()
    process.memory[address] = value


@operation(Q(1, 125), 'stm')
def store_memory(process, operand):
    address = process.pop() + operand
    value = process.pop()
    process.memory[address] = value


@operation(Q(1, 229), 'str')
def store_register(process, operand):
    value = process.pop()
    process.registers[operand] = value


@operation(Q(1, 183), 'sub')
def subtract(process, operand):
    right = process.pop()
    left = process.pop()

    process.push(left - right)


@operation(Q(1, 3), 'swp')
def swap(process, operand):
    a = process.pop()
    b = process.pop()

    process.push(a)
    process.push(b)


@operation(Q(1, 223), 'top')
def top(process, operand):
    process.registers[DR] += operand
