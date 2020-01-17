from enum import Enum
from fractions import Fraction as Q


class Opcode(Enum):
    LOAD_NUMERATOR = Q(1, 1) # any numerator
    SWAP = Q(1, 3)
    DECREMENT = Q(1, 9)
    LOAD = Q(1, 18)
    ALLOCATE = Q(1, 33)
    INVERT = Q(1, 49)
    DIVIDE = Q(1, 76)
    ADD = Q(1, 81)
    MULTIPLY = Q(1, 107)
    STORE = Q(1, 125)
    INCREMENT = Q(1, 143)
    NEGATE = Q(1, 147)
    CALL = Q(1, 164)
    DENOMINATOR = Q(1, 171)
    SUBTRACT = Q(1, 183)
    RETURN = Q(1, 193)
    JUMP = Q(1, 199)
    DEALLOCATE = Q(1, 211)
    READ = Q(1, 214)
    NUMERATOR = Q(1, 222)
    DISCARD = Q(1, 223) # prime
    LOAD_REGISTER = Q(1, 227) # prime
    STORE_REGISTER = Q(1, 229) # prime
    STORE_PARAMETER = Q(1, 233) # prime
    COPY = Q(1, 236)
    LOAD_VARIABLE = Q(1, 239) # prime
    LOAD_PARAMETER = Q(1, 241) # prime
    WRITE = Q(1, 245)
    LOAD_RATIONAL = Q(1, 247) # prime
    STORE_VARIABLE = Q(1, 251) # prime
    JUMP_FALSE = Q(1, 252)
    HALT = Q(1, 255)
