from enum import Enum
from fractions import Fraction as Q


class StandardStream(Enum):
    STDIN = Q(2, 3)
    STDOUT = Q(1, 4)
    STDERR = Q(3, 4)
