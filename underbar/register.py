from enum import Enum


class Register(Enum):
    IR = 0 # Instruction
    JR = 1 # Jump
    SR = 2 # Stack
    FR = 3 # Frame
