from enum import Enum


class Mnemonic(Enum):
    LDI = Opcode.LOAD_INTEGER
    SWP = Opcode.SWAP
    DEC = Opcode.DECREMENT
    LDM = Opcode.LOAD_MEMORY
    NEW = Opcode.NEW
    INV = Opcode.INVERT
    DIV = Opcode.DIVIDE
    ADD = Opcode.ADD
    MUL = Opcode.MULTIPLY
    STM = Opcode.STORE_MEMORY
    INC = Opcode.INCREMENT
    NEG = Opcode.NEGATE
    CAL = Opcode.CALL
    DEN = Opcode.DENOMINATOR
    SUB = Opcode.SUBTRACT
    RET = Opcode.RETURN
    JMP = Opcode.JUMP
    DEL = Opcode.DELETE
    LDS = Opcode.LOAD_STREAM
    NUM = Opcode.NUMERATOR
    DIS = Opcode.DISCARD
    LDR = Opcode.LOAD_REGISTER
    STR = Opcode.STORE_REGISTER
    STP = Opcode.STORE_PARAMETER
    DUP = Opcode.DUPLICATE
    LDV = Opcode.LOAD_VARIABLE
    LDP = Opcode.LOAD_PARAMETER
    STS = Opcode.STORE_STREAM
    LDQ = Opcode.LOAD_RATIONAL
    STV = Opcode.STORE_VARIABLE
    JEQ = Opcode.JUMP_EQUAL
    HCF = Opcode.HALT
