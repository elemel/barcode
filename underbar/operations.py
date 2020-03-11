from enum import Enum
from fractions import Fraction as Q

from underbar.register import Register

PR = Register.PR.value
DR = Register.DR.value
CR = Register.CR.value

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
    process.registers[PR] = Q(operand)


@operation(Q(9, 10), 'beq')
def branch_equal(process, operand):
    if not process.pop_data():
        process.registers[PR] = Q(operand)


@operation(Q(2, 5), 'bge')
def branch_greater_equal(process, operand):
    if process.pop_data() >= 0:
        process.registers[PR] = Q(operand)


@operation(Q(5, 9), 'bgt')
def branch_greater_than(process, operand):
    if process.pop_data() > 0:
        process.registers[PR] = Q(operand)


@operation(Q(1, 10), 'ble')
def branch_less_equal(process, operand):
    if process.pop_data() <= 0:
        process.registers[PR] = Q(operand)


@operation(Q(3, 11), 'blt')
def branch_less_than(process, operand):
    if process.pop_data() < 0:
        process.registers[PR] = Q(operand)


@operation(Q(3, 10), 'bne')
def branch_not_equal(process, operand):
    if process.pop_data():
        process.registers[PR] = Q(operand)


@operation(Q(5, 11), 'cal')
def call(process, operand):
    function = process.pop_data()
    process.push_call(process.registers[PR])
    process.registers[PR] = function


@operation(Q(4, 11), 'cli')
def call_integer(process, operand):
    process.push_call(process.registers[PR])
    process.registers[PR] = Q(operand)


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
    value = process.pop_data()

    process.push_data(value)
    process.push_data(value)


@operation(Q(1, 2), 'ent')
def enter(process, operand):
    process.registers[CR] += operand


@operation(Q(4, 7), 'fdi')
def floor_divide_integer(process, operand):
    value = process.pop_data()
    process.push_data(Q(value // operand))


@operation(Q(2, 7))
def get(process, operand):
    handle = process.peek()
    stream = process.streams[handle]

    if not stream:
        # User can provide input and resume
        process.registers[PR] -= 1
        raise BlockedError()

    if stream[0] is None:
        # End of file
        process.registers[PR] -= 1
        raise ClosedError()

    process.pop_data()
    value = stream.popleft()
    process.push_data(value)


@operation(Q(7, 9), 'hcf')
def halt(process, operand):
    process.registers[PR] -= 1
    raise TerminatedError()


@operation(Q(5, 6), 'inv')
def invert(process, operand):
    value = process.pop_data()
    process.push_data(1 / value)


@operation(Q(0), 'ldi')
def load_integer(process, operand):
    process.push_data(Q(operand))


@operation(Q(1, 11), 'ldl')
def load_local(process, operand):
    address = process.registers[CR] - 1 - operand
    value = process.memory[address]
    process.push_data(value)


@operation(Q(1, 7), 'ldm')
def load_memory(process, operand):
    address = process.pop_data() + operand
    value = process.memory[address]
    process.push_data(value)


@operation(Q(7, 11), 'ldr')
def load_register(process, operand):
    value = process.registers[operand]
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
    size = process.pop_data()
    array = process.memory.new(size)
    process.push_data(array)


@operation(Q(4, 5), 'num')
def numerator(process, operand):
    value = process.pop_data()
    value = Q(value.numerator)
    process.push_data(value)


@operation(Q(2, 11))
def pop(process, operand):
    process.registers[DR] -= 1


@operation(Q(1, 3))
def put(process, operand):
    handle = process.pop_data()
    value = process.pop_data()

    stream = process.streams[handle]
    stream.append(value)


@operation(Q(8, 9), 'ret')
def return_(process, operand):
    process.registers[CR] -= operand
    process.registers[PR] = process.pop_call()


@operation(Q(3, 4), 'siz')
def size(process, operand):
    handle = process.pop_data()
    stream = process.streams[handle]
    size = len(stream)
    
    if size and stream[0] is None:
        size -= 1

        if not size:
            size -= 1

    process.push_data(Q(size))


@operation(Q(7, 8), 'stl')
def store_local(process, operand):
    address = process.registers[CR] - 1 - operand
    value = process.pop_data()
    process.memory[address] = value


@operation(Q(3, 5), 'stm')
def store_memory(process, operand):
    address = process.pop_data() + operand
    value = process.pop_data()
    process.memory[address] = value


@operation(Q(5, 8), 'str')
def store_register(process, operand):
    value = process.pop_data()
    process.registers[operand] = value


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
