from enum import Enum
from fractions import Fraction as Q

from serviam.register import Register

IR = Register.INSTRUCTION.value - 1
SR = Register.STACK.value - 1
FR = Register.FRAME.value - 1


class BlockedError(Exception):
    pass


class TerminatedError(Exception):
    pass


def add(process):
    process.push(process.pop() + process.pop())
    process.registers[IR] += 1


def allocate(process):
    process.push(process.allocate())
    process.registers[IR] += 1


def call(process):
    address = process.pop()

    process.push(process.registers[IR] + 1) # return address
    process.push(process.registers[FR])

    process.registers[IR] = address
    process.registers[FR] = process.registers[SR]


def copy(process):
    value = process.pop()

    process.push(value)
    process.push(value)

    process.registers[IR] += 1


def deallocate(process):
    process.deallocate(process.pop())
    process.registers[IR] += 1


def decrement(process):
    process.push(process.pop() - 1)
    process.registers[IR] += 1


def denominator(process):
    process.push(Q(process.pop().denominator))
    process.registers[IR] += 1


def discard(process):
    count = process.memory[process.registers[IR]].numerator
    process.registers[SR] -= count
    process.registers[IR] += 1


def divide(process):
    process.push(process.pop() / process.pop())
    process.registers[IR] += 1


def halt(process):
    raise TerminatedError()


def increment(process):
    process.push(process.pop() + 1)
    process.registers[IR] += 1


def invert(process):
    process.push(1 / process.pop())
    process.registers[IR] += 1


def jump(process):
    process.registers[IR] = process.pop()


def jump_false(process):
    address = process.pop()

    if not process.pop():
        process.registers[IR] = address
    else:
        process.registers[IR] += 1


def load(process):
    address = process.pop()
    process.push(process.memory[address])
    process.registers[IR] += 1


def load_integer(process):
    process.push(Q(process.memory[process.registers[IR]].numerator))
    process.registers[IR] += 1


def load_parameter(process):
    index = process.memory[process.registers[IR]].numerator
    process.push(process.memory[process.registers[FR] - (index + 2)])
    process.registers[IR] += 1


def load_rational(process):
    process.push(process.memory[process.registers[IR] + 1])
    process.registers[IR] += 2


def load_register(process):
    index = process.memory[process.registers[IR]].numerator
    process.push(process.memory[index - 1])
    process.registers[IR] += 1


def load_variable(process):
    index = process.memory[process.registers[IR]].numerator
    process.push(process.memory[process.registers[FR] + (index - 1)])
    process.registers[IR] += 1


def multiply(process):
    process.push(process.pop() * process.pop())
    process.registers[IR] += 1


def negate(process):
    process.push(-process.pop())
    process.registers[IR] += 1


def numerator(process):
    process.push(Q(process.pop().numerator))
    process.registers[IR] += 1


def read(process):
    file_descriptor = process.pop()
    stream = process.streams[file_descriptor]

    if not stream:
        raise BlockedError()

    process.push(stream.popleft())
    process.registers[IR] += 1


def return_(process):
    process.registers[SR] = process.registers[FR]
    process.registers[FR] = process.pop()
    process.registers[IR] = process.pop()


def store(process):
    address = process.pop()
    process.memory[address] = process.pop()
    process.registers[IR] += 1


def store_parameter(process):
    index = process.memory[process.registers[IR]].numerator
    process.memory[process.registers[FR] - (index + 2)] = process.pop()
    process.registers[IR] += 1


def store_register(process):
    index = process.memory[process.registers[IR]].numerator
    process.registers[index - 1] = process.pop()
    process.registers[IR] += 1


def store_variable(process):
    index = process.memory[process.registers[IR]].numerator
    process.memory[process.registers[FR] + (index - 1)] = process.pop()
    process.registers[IR] += 1


def subtract(process):
    process.push(process.pop() - process.pop())
    process.registers[IR] += 1


def swap(process):
    a = process.pop()
    b = process.pop()

    process.push(a)
    process.push(b)

    process.registers[IR] += 1


def write(process):
    file_descriptor = process.pop()
    stream = process.streams[file_descriptor]
    stream.append(process.pop())
    process.registers[IR] += 1
