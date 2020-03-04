from enum import Enum


class Register(Enum):
    IR = 0 # Instruction
    JR = 1 # Jump
    DR = 2 # Data
    FR = 3 # Frame
