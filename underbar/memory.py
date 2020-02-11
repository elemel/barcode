from fractions import Fraction as Q


class Memory:
    def __init__(self, size):
        self.arrays = [None, size * [Q(0)]]
        self.pool = []

    def __getitem__(self, key):
        i = key.denominator
        j = key.numerator // key.denominator
        assert j >= 0
        return self.arrays[i][j]

    def __setitem__(self, key, value):
        i = key.denominator
        j = key.numerator // key.denominator
        assert j >= 0
        self.arrays[i][j] = value

    def new(self, size):
        if self.pool:
            key = self.pool.pop()
        else:
            self.arrays.append(None)
            key = Q(1, len(self.arrays) - 1)

        i = key.denominator
        self.arrays[i] = size * [Q(0)]
        return key

    def delete(self, key):
        i = key.denominator
        assert i >= 2 and key.numerator == 1
        assert self.arrays[i] is not None
        self.arrays[i] = None

        if i == len(self.arrays) - 1:
            self.arrays.pop()
        else:
            self.pool.append(key)
