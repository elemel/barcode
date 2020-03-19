from enum import Enum
from fractions import Fraction as Q
from math import floor

from quest.register import Register

IR = Register.IR.value
DR = Register.DR.value
CR = Register.CR.value

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

        if mnemonic in MNEMONIC_TO_OPCODE:
            raise ValueError(f'Duplicate mnemonic: {mnemonic}')

        if opcode in OPCODE_TO_OPERATION:
            raise ValueError(f'Duplicate opcode: {opcode}')

        MNEMONIC_TO_OPCODE[mnemonic] = opcode
        OPCODE_TO_OPERATION[opcode] = func
        return func

    return decorate


@operation(Q(5, 7))
def add(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left + right)


@operation(Q(3, 7), 'adi')
def add_integer(process, operand):
    value = process.pop_data()
    process.push_data(value + operand)


@operation(Q(7, 10), 'bal')
def branch_always(process, operand):
    process.registers[IR] = Q(operand)


@operation(Q(9, 10), 'beq')
def branch_equal(process, operand):
    if not process.pop_data():
        process.registers[IR] = Q(operand)


@operation(Q(2, 5), 'bge')
def branch_greater_equal(process, operand):
    if process.pop_data() >= 0:
        process.registers[IR] = Q(operand)


@operation(Q(5, 9), 'bgt')
def branch_greater_than(process, operand):
    if process.pop_data() > 0:
        process.registers[IR] = Q(operand)


@operation(Q(1, 10), 'ble')
def branch_less_equal(process, operand):
    if process.pop_data() <= 0:
        process.registers[IR] = Q(operand)


@operation(Q(3, 11), 'blt')
def branch_less_than(process, operand):
    if process.pop_data() < 0:
        process.registers[IR] = Q(operand)


@operation(Q(3, 10), 'bne')
def branch_not_equal(process, operand):
    if process.pop_data():
        process.registers[IR] = Q(operand)


@operation(Q(5, 11), 'cal')
def call(process, operand):
    function = process.pop_data()
    process.push_call(process.registers[IR])
    process.registers[IR] = function


@operation(Q(4, 11), 'cls')
def call_static(process, operand):
    process.push_call(process.registers[IR])
    process.registers[IR] = Q(operand)


@operation(Q(4, 9), 'del')
def delete(process, operand):
    array = process.pop_data()
    process.memory.delete(array)


@operation(Q(6, 11), 'den')
def denominator(process, operand):
    value = process.pop_data()
    value = Q(value.denominator)
    process.push_data(value)


@operation(Q(1, 9), 'div')
def divide(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left / right)


@operation(Q(1, 5), 'dup')
def duplicate(process, operand):
    address = process.registers[DR] - 1 - operand
    value = process.memory[address]
    process.push_data(value)


@operation(Q(1, 2), 'ent')
def enter(process, operand):
    for _ in range(operand):
        process.push_call(Q(0))


@operation(Q(4, 7), 'fdi')
def floor_divide_integer(process, operand):
    value = process.pop_data()
    process.push_data(Q(value // operand))


@operation(Q(10, 11))
def get(process, operand):
    handle = floor(process.pop_data())
    stream = process.streams[handle]
    value = stream.popleft()
    process.push_data(value)


@operation(Q(7, 9), 'hcf')
def halt(process, operand):
    process.registers[IR] -= 1
    raise TerminatedError()


@operation(Q(5, 6), 'inv')
def invert(process, operand):
    value = process.pop_data()
    process.push_data(1 / value)


@operation(Q(1, 7), 'ldd')
def load_dynamic(process, operand):
    address = process.pop_data() + operand
    value = process.memory[address]
    process.push_data(value)


@operation(Q(1, 11), 'ldl')
def load_local(process, operand):
    address = process.registers[CR] - 1 - operand
    value = process.memory[address]
    process.push_data(value)


@operation(Q(7, 11), 'ldr')
def load_register(process, operand):
    value = process.registers[operand]
    process.push_data(value)


@operation(Q(8, 11), 'lds')
def load_static(process, operand):
    value = process.memory[Q(operand)]
    process.push_data(value)


@operation(Q(2, 9), 'mod')
def modulo(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left % right)


@operation(Q(1, 8), 'mul')
def multiply(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left * right)


@operation(Q(1, 4), 'mli')
def multiply_integer(process, operand):
    value = process.pop_data()
    process.push_data(value * operand)


@operation(Q(3, 8), 'neg')
def negate(process, operand):
    process.push_data(-process.pop_data())


@operation(Q(2, 3))
def new(process, operand):
    array = process.memory.new(operand)
    process.push_data(array)


@operation(Q(4, 5), 'num')
def numerator(process, operand):
    value = process.pop_data()
    value = Q(value.numerator)
    process.push_data(value)


@operation(Q(2, 11), 'dis')
def discard(process, operand):
    process.pop_data()


@operation(Q(0), 'ldi')
def load_integer(process, operand):
    process.push_data(Q(operand))


@operation(Q(2, 7))
def pop(process, operand):
    handle = process.pop_data()

    try:
        value = process.memory.pop(handle)
        process.push_data(value)
    except:
        # User can provide input and resume
        process.push_data(handle)
        process.registers[IR] -= 1
        raise BlockedError()


@operation(Q(1, 3), 'psh')
def push(process, operand):
    handle = process.pop_data()
    value = process.pop_data()

    process.memory.push(handle, value)


@operation(Q(9, 11))
def put(process, operand):
    handle = floor(process.pop_data())
    stream = process.streams[handle]
    value = process.pop_data()
    stream.append(value)


@operation(Q(8, 9), 'ret')
def return_(process, operand):
    for _ in range(operand):
        process.pop_call()

    process.registers[IR] = process.pop_call()


@operation(Q(3, 4), 'siz')
def size(process, operand):
    handle = process.pop_data()
    size = process.memory.size(handle)
    process.push_data(Q(size))


@operation(Q(3, 5), 'std')
def store_dynamic(process, operand):
    address = process.pop_data() + operand
    value = process.pop_data()
    process.memory[address] = value


@operation(Q(7, 8), 'stl')
def store_local(process, operand):
    address = process.registers[CR] - 1 - operand
    value = process.pop_data()
    process.memory[address] = value


@operation(Q(5, 8), 'str')
def store_register(process, operand):
    value = process.pop_data()
    process.registers[operand] = value


@operation(Q(5, 12), 'sts')
def store_static(process, operand):
    address = Q(operand)
    value = process.pop_data()
    process.memory[address] = value


@operation(Q(1, 6), 'sub')
def subtract(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left - right)


@operation(Q(6, 7), 'swp')
def swap(process, operand):
    a = process.pop_data()
    b = process.pop_data()

    process.push_data(a)
    process.push_data(b)


@operation(Q(1, 12), 'tel')
def tell(process, operand):
    handle = floor(process.pop_data())
    stream = process.streams[handle]
    size = len(stream)
    process.push_data(Q(size))
