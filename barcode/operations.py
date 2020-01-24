from enum import Enum
from fractions import Fraction as Q

from barcode.register import Register

IR = Register.INSTRUCTION.value - 1
SR = Register.STACK.value - 1
FR = Register.FRAME.value - 1

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

        if opcode in OPCODE_TO_OPERATION:
            raise ValueError(f'Duplicate opcode: {opcode}')

        if mnemonic in MNEMONIC_TO_OPCODE:
            raise ValueError(f'Duplicate mnemonic: {mnemonic}')

        OPCODE_TO_OPERATION[opcode] = func
        MNEMONIC_TO_OPCODE[mnemonic] = opcode
        return func

    return decorate


@operation(81)
def add(process):
    process.push(process.pop() + process.pop())
    process.registers[IR] += 1


@operation(33)
def new(process):
    process.push(process.new())
    process.registers[IR] += 1


@operation(164)
def call(process):
    address = process.pop()

    process.push(process.registers[IR] + 1) # return address
    process.push(process.registers[FR])

    process.registers[IR] = address
    process.registers[FR] = process.registers[SR]


@operation(9)
def decrement(process):
    process.push(process.pop() - 1)
    process.registers[IR] += 1


@operation(211)
def delete(process):
    process.delete(process.pop())
    process.registers[IR] += 1


@operation(171)
def denominator(process):
    process.push(Q(process.pop().denominator))
    process.registers[IR] += 1


@operation(223)
def discard(process):
    count = process.memory[process.registers[IR]].numerator
    process.registers[SR] -= count
    process.registers[IR] += 1


@operation(76)
def divide(process):
    process.push(process.pop() / process.pop())
    process.registers[IR] += 1


@operation(236)
def duplicate(process):
    value = process.pop()

    process.push(value)
    process.push(value)

    process.registers[IR] += 1


@operation(255)
def halt(process):
    raise TerminatedError()


@operation(143)
def increment(process):
    process.push(process.pop() + 1)
    process.registers[IR] += 1


@operation(49)
def invert(process):
    process.push(1 / process.pop())
    process.registers[IR] += 1


@operation(199)
def jump(process):
    process.registers[IR] = process.pop()


@operation(252)
def jump_equal(process):
    address = process.pop()

    if not process.pop():
        process.registers[IR] = address
    else:
        process.registers[IR] += 1


@operation(1)
def load_integer(process):
    process.push(Q(process.memory[process.registers[IR]].numerator))
    process.registers[IR] += 1


@operation(18)
def load_memory(process):
    address = process.pop()
    process.push(process.memory[address])
    process.registers[IR] += 1


@operation(241)
def load_parameter(process):
    index = process.memory[process.registers[IR]].numerator
    process.push(process.memory[process.registers[FR] - (index + 2)])
    process.registers[IR] += 1


@operation(247)
def load_rational(process):
    process.push(process.memory[process.registers[IR] + 1])
    process.registers[IR] += 2


@operation(227)
def load_register(process):
    index = process.memory[process.registers[IR]].numerator
    process.push(process.memory[index - 1])
    process.registers[IR] += 1


@operation(214)
def load_stream(process):
    file_descriptor = process.pop()
    stream = process.streams[file_descriptor]

    if not stream:
        raise BlockedError()

    process.push(stream.popleft())
    process.registers[IR] += 1


@operation(239)
def load_variable(process):
    index = process.memory[process.registers[IR]].numerator
    process.push(process.memory[process.registers[FR] + (index - 1)])
    process.registers[IR] += 1


@operation(107)
def multiply(process):
    process.push(process.pop() * process.pop())
    process.registers[IR] += 1


@operation(147)
def negate(process):
    process.push(-process.pop())
    process.registers[IR] += 1


@operation(222)
def numerator(process):
    process.push(Q(process.pop().numerator))
    process.registers[IR] += 1


@operation(193, 'return')
def return_(process):
    process.registers[SR] = process.registers[FR]
    process.registers[FR] = process.pop()
    process.registers[IR] = process.pop()


@operation(125)
def store_memory(process):
    address = process.pop()
    process.memory[address] = process.pop()
    process.registers[IR] += 1


@operation(233)
def store_parameter(process):
    index = process.memory[process.registers[IR]].numerator
    process.memory[process.registers[FR] - (index + 2)] = process.pop()
    process.registers[IR] += 1


@operation(229)
def store_register(process):
    index = process.memory[process.registers[IR]].numerator
    process.registers[index - 1] = process.pop()
    process.registers[IR] += 1


@operation(245)
def store_stream(process):
    file_descriptor = process.pop()
    stream = process.streams[file_descriptor]
    stream.append(process.pop())
    process.registers[IR] += 1


@operation(251)
def store_variable(process):
    index = process.memory[process.registers[IR]].numerator
    process.memory[process.registers[FR] + (index - 1)] = process.pop()
    process.registers[IR] += 1


@operation(183)
def subtract(process):
    process.push(process.pop() - process.pop())
    process.registers[IR] += 1


@operation(3)
def swap(process):
    a = process.pop()
    b = process.pop()

    process.push(a)
    process.push(b)

    process.registers[IR] += 1
