from enum import Enum


class Register(Enum):
    INSTRUCTION = 1
    GARBAGE = 2
    HEAP = 3
    STACK = 4
    FRAME = 5
