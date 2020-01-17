from enum import Enum
from fractions import Fraction as Q


class Register(Enum):
    INSTRUCTION = 0
    GARBAGE = 1
    HEAP = 2
    STACK = 3
    FRAME = 4
