from enum import Enum


class Register(Enum):
    IR = 0 # Instruction
    JR = 1 # Jump
    DR = 2 # Data
    CR = 3 # Call
