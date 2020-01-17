from enum import Enum
from fractions import Fraction as Q


class StandardStream(Enum):
    INPUT = Q(0)
    OUTPUT = Q(1)
    ERROR = Q(2)
