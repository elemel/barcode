from enum import Enum


class Opcode(Enum):
    LOAD_INTEGER = 1 # any numerator
    SWAP = 3
    DECREMENT = 9
    LOAD_MEMORY = 18
    NEW = 33
    INVERT = 49
    DIVIDE = 76
    ADD = 81
    MULTIPLY = 107
    STORE_MEMORY = 125
    INCREMENT = 143
    NEGATE = 147
    CALL = 164
    DENOMINATOR = 171
    SUBTRACT = 183
    RETURN = 193
    JUMP = 199
    DELETE = 211
    LOAD_STREAM = 214
    NUMERATOR = 222
    DISCARD = 223 # prime
    LOAD_REGISTER = 227 # prime
    STORE_REGISTER = 229 # prime
    STORE_PARAMETER = 233 # prime
    DUPLICATE = 236
    LOAD_VARIABLE = 239 # prime
    LOAD_PARAMETER = 241 # prime
    STORE_STREAM = 245
    LOAD_RATIONAL = 247 # prime
    STORE_VARIABLE = 251 # prime
    JUMP_FALSE = 252
    HALT = 255
