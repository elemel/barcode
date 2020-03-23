from fractions import Fraction as Q
from math import floor

from quest.opcode import Opcode
from quest.register import Register

IR = Register.IR.value
DR = Register.DR.value
CR = Register.CR.value


def add(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left + right)


def add_integer(process, operand):
    value = process.pop_data()
    process.push_data(value + operand)


def branch_always(process, operand):
    process.registers[IR] = Q(operand)


def branch_equal(process, operand):
    if not process.pop_data():
        process.registers[IR] = Q(operand)


def branch_greater_equal(process, operand):
    if process.pop_data() >= 0:
        process.registers[IR] = Q(operand)


def branch_greater_than(process, operand):
    if process.pop_data() > 0:
        process.registers[IR] = Q(operand)


def branch_less_equal(process, operand):
    if process.pop_data() <= 0:
        process.registers[IR] = Q(operand)


def branch_less_than(process, operand):
    if process.pop_data() < 0:
        process.registers[IR] = Q(operand)


def branch_not_equal(process, operand):
    if process.pop_data():
        process.registers[IR] = Q(operand)


def call_dynamic(process, operand):
    function = process.pop_data()
    process.push_call(process.registers[IR])
    process.registers[IR] = function


def call_static(process, operand):
    process.push_call(process.registers[IR])
    process.registers[IR] = Q(operand)


def delete(process, operand):
    array = process.pop_data()
    process.memory.delete(array)


def denominator(process, operand):
    value = process.pop_data()
    value = Q(value.denominator)
    process.push_data(value)


def divide(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left / right)


def duplicate(process, operand):
    address = process.registers[DR] - 1 - operand
    value = process.memory[address]
    process.push_data(value)


def enter(process, operand):
    for _ in range(operand):
        process.push_call(Q(0))


def floor_divide_integer(process, operand):
    value = process.pop_data()
    process.push_data(Q(value // operand))


def get(process, operand):
    handle = floor(process.pop_data())
    stream = process.streams[handle]
    value = stream.popleft()
    process.push_data(value)


def halt(process, operand):
    raise RuntimeError('Halt')


def invert(process, operand):
    value = process.pop_data()
    process.push_data(1 / value)


def load_dynamic(process, operand):
    address = process.pop_data() + operand
    value = process.memory[address]
    process.push_data(value)


def load_local(process, operand):
    address = process.registers[CR] - 1 - operand
    value = process.memory[address]
    process.push_data(value)


def load_register(process, operand):
    value = process.registers[operand]
    process.push_data(value)


def load_static(process, operand):
    value = process.memory[Q(operand)]
    process.push_data(value)


def modulo(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left % right)


def multiply(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left * right)


def multiply_integer(process, operand):
    value = process.pop_data()
    process.push_data(value * operand)


def negate(process, operand):
    process.push_data(-process.pop_data())


def new(process, operand):
    array = process.memory.new(operand)
    process.push_data(array)


def numerator(process, operand):
    value = process.pop_data()
    value = Q(value.numerator)
    process.push_data(value)


def discard(process, operand):
    process.pop_data()


def load_integer(process, operand):
    process.push_data(Q(operand))


def pop(process, operand):
    handle = process.pop_data()
    value = process.memory.pop(handle)
    process.push_data(value)


def push(process, operand):
    handle = process.pop_data()
    value = process.pop_data()
    process.memory.push(handle, value)


def put(process, operand):
    handle = floor(process.pop_data())
    stream = process.streams[handle]
    value = process.pop_data()
    stream.append(value)


def return_(process, operand):
    for _ in range(operand):
        process.pop_call()

    process.registers[IR] = process.pop_call()


def size(process, operand):
    handle = process.pop_data()
    size = process.memory.size(handle)
    process.push_data(Q(size))


def store_dynamic(process, operand):
    address = process.pop_data() + operand
    value = process.pop_data()
    process.memory[address] = value


def store_local(process, operand):
    address = process.registers[CR] - 1 - operand
    value = process.pop_data()
    process.memory[address] = value


def store_register(process, operand):
    value = process.pop_data()
    process.registers[operand] = value


def store_static(process, operand):
    address = Q(operand)
    value = process.pop_data()
    process.memory[address] = value


def subtract(process, operand):
    right = process.pop_data()
    left = process.pop_data()

    process.push_data(left - right)


def swap(process, operand):
    a = process.pop_data()
    b = process.pop_data()

    process.push_data(a)
    process.push_data(b)


def tell(process, operand):
    handle = floor(process.pop_data())
    stream = process.streams[handle]
    size = len(stream)
    process.push_data(Q(size))


OPERATIONS = {
    Opcode.ADD: add,
    Opcode.ADI: add_integer,
    Opcode.BAL: branch_always,
    Opcode.BEQ: branch_equal,
    Opcode.BGE: branch_greater_equal,
    Opcode.BGT: branch_greater_than,
    Opcode.BLE: branch_less_equal,
    Opcode.BLT: branch_less_than,
    Opcode.BNE: branch_not_equal,
    Opcode.CLD: call_dynamic,
    Opcode.CLS: call_static,
    Opcode.DEL: delete,
    Opcode.DEN: denominator,
    Opcode.DIV: divide,
    Opcode.DUP: duplicate,
    Opcode.ENT: enter,
    Opcode.FDI: floor_divide_integer,
    Opcode.GET: get,
    Opcode.HCF: halt,
    Opcode.INV: invert,
    Opcode.LDD: load_dynamic,
    Opcode.LDL: load_local,
    Opcode.LDR: load_register,
    Opcode.LDS: load_static,
    Opcode.MOD: modulo,
    Opcode.MUL: multiply,
    Opcode.MLI: multiply_integer,
    Opcode.NEG: negate,
    Opcode.NEW: new,
    Opcode.NUM: numerator,
    Opcode.DIS: discard,
    Opcode.LDI: load_integer,
    Opcode.POP: pop,
    Opcode.PSH: push,
    Opcode.PUT: put,
    Opcode.RET: return_,
    Opcode.SIZ: size,
    Opcode.STD: store_dynamic,
    Opcode.STL: store_local,
    Opcode.STR: store_register,
    Opcode.STS: store_static,
    Opcode.SUB: subtract,
    Opcode.SWP: swap,
    Opcode.TEL: tell,
}
