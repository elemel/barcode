from enum import Enum
from fractions import Fraction as Q
from math import floor

from quest.opcode import Opcode
from quest.register import Register
from quest.utils import fraction_to_index

IR = Register.IR.value
DR = Register.DR.value
CR = Register.CR.value

OPERATIONS = 256 * [None]


def operation(opcode: Opcode):
    def decorate(func):
        index = fraction_to_index(opcode.value)
        OPERATIONS[index] = func
        return func

    return decorate


@operation(Opcode.ADD)
def add(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left + right)


@operation(Opcode.ADI)
def add_integer(process, operand):
    value = process.pop_data()
    process.push_data(value + operand)


@operation(Opcode.BAL)
def branch_always(process, operand):
    process.registers[IR] = Q(operand)


@operation(Opcode.BEQ)
def branch_equal(process, operand):
    if not process.pop_data():
        process.registers[IR] = Q(operand)


@operation(Opcode.BGE)
def branch_greater_equal(process, operand):
    if process.pop_data() >= 0:
        process.registers[IR] = Q(operand)


@operation(Opcode.BGT)
def branch_greater_than(process, operand):
    if process.pop_data() > 0:
        process.registers[IR] = Q(operand)


@operation(Opcode.BLE)
def branch_less_equal(process, operand):
    if process.pop_data() <= 0:
        process.registers[IR] = Q(operand)


@operation(Opcode.BLT)
def branch_less_than(process, operand):
    if process.pop_data() < 0:
        process.registers[IR] = Q(operand)


@operation(Opcode.BNE)
def branch_not_equal(process, operand):
    if process.pop_data():
        process.registers[IR] = Q(operand)


@operation(Opcode.CLD)
def call_dynamic(process, operand):
    function = process.pop_data()
    process.push_call(process.registers[IR])
    process.registers[IR] = function


@operation(Opcode.CLS)
def call_static(process, operand):
    process.push_call(process.registers[IR])
    process.registers[IR] = Q(operand)


@operation(Opcode.DEL)
def delete(process, operand):
    array = process.pop_data()
    process.memory.delete(array)


@operation(Opcode.DEN)
def denominator(process, operand):
    value = process.pop_data()
    value = Q(value.denominator)
    process.push_data(value)


@operation(Opcode.DIV)
def divide(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left / right)


@operation(Opcode.DUP)
def duplicate(process, operand):
    address = process.registers[DR] - 1 - operand
    value = process.memory[address]
    process.push_data(value)


@operation(Opcode.ENT)
def enter(process, operand):
    for _ in range(operand):
        process.push_call(Q(0))


@operation(Opcode.FDI)
def floor_divide_integer(process, operand):
    value = process.pop_data()
    process.push_data(Q(value // operand))


@operation(Opcode.GET)
def get(process, operand):
    handle = floor(process.pop_data())
    stream = process.streams[handle]
    value = stream.popleft()
    process.push_data(value)


@operation(Opcode.HCF)
def halt(process, operand):
    raise RuntimeError('Halt')


@operation(Opcode.INV)
def invert(process, operand):
    value = process.pop_data()
    process.push_data(1 / value)


@operation(Opcode.LDD)
def load_dynamic(process, operand):
    address = process.pop_data() + operand
    value = process.memory[address]
    process.push_data(value)


@operation(Opcode.LDL)
def load_local(process, operand):
    address = process.registers[CR] - 1 - operand
    value = process.memory[address]
    process.push_data(value)


@operation(Opcode.LDR)
def load_register(process, operand):
    value = process.registers[operand]
    process.push_data(value)


@operation(Opcode.LDS)
def load_static(process, operand):
    value = process.memory[Q(operand)]
    process.push_data(value)


@operation(Opcode.MOD)
def modulo(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left % right)


@operation(Opcode.MUL)
def multiply(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left * right)


@operation(Opcode.MLI)
def multiply_integer(process, operand):
    value = process.pop_data()
    process.push_data(value * operand)


@operation(Opcode.NEG)
def negate(process, operand):
    process.push_data(-process.pop_data())


@operation(Opcode.NEW)
def new(process, operand):
    array = process.memory.new(operand)
    process.push_data(array)


@operation(Opcode.NUM)
def numerator(process, operand):
    value = process.pop_data()
    value = Q(value.numerator)
    process.push_data(value)


@operation(Opcode.DIS)
def discard(process, operand):
    process.pop_data()


@operation(Opcode.LDI)
def load_integer(process, operand):
    process.push_data(Q(operand))


@operation(Opcode.POP)
def pop(process, operand):
    handle = process.pop_data()
    value = process.memory.pop(handle)
    process.push_data(value)


@operation(Opcode.PSH)
def push(process, operand):
    handle = process.pop_data()
    value = process.pop_data()
    process.memory.push(handle, value)


@operation(Opcode.PUT)
def put(process, operand):
    handle = floor(process.pop_data())
    stream = process.streams[handle]
    value = process.pop_data()
    stream.append(value)


@operation(Opcode.RET)
def return_(process, operand):
    for _ in range(operand):
        process.pop_call()

    process.registers[IR] = process.pop_call()


@operation(Opcode.SIZ)
def size(process, operand):
    handle = process.pop_data()
    size = process.memory.size(handle)
    process.push_data(Q(size))


@operation(Opcode.STD)
def store_dynamic(process, operand):
    address = process.pop_data() + operand
    value = process.pop_data()
    process.memory[address] = value


@operation(Opcode.STL)
def store_local(process, operand):
    address = process.registers[CR] - 1 - operand
    value = process.pop_data()
    process.memory[address] = value


@operation(Opcode.STR)
def store_register(process, operand):
    value = process.pop_data()
    process.registers[operand] = value


@operation(Opcode.STS)
def store_static(process, operand):
    address = Q(operand)
    value = process.pop_data()
    process.memory[address] = value


@operation(Opcode.SUB)
def subtract(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left - right)


@operation(Opcode.SWP)
def swap(process, operand):
    a = process.pop_data()
    b = process.pop_data()

    process.push_data(a)
    process.push_data(b)


@operation(Opcode.TEL)
def tell(process, operand):
    handle = floor(process.pop_data())
    stream = process.streams[handle]
    size = len(stream)
    process.push_data(Q(size))
