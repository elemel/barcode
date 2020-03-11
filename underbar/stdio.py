from enum import Enum
from fractions import Fraction as Q


class StandardStream(Enum):
    STDIN = Q(1, 2)
    STDOUT = Q(1, 3)
    STDERR = Q(2, 3)
