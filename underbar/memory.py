from fractions import Fraction as Q


class Memory:
    def __init__(self, size):
        self.arrays = [size * [Q(0)]]
        self.pool = []

    def __getitem__(self, key):
        i = key.denominator - 1
        j = key.numerator // key.denominator
        assert j >= 0
        return self.arrays[i][j]

    def __setitem__(self, key, value):
        i = key.denominator - 1
        j = key.numerator // key.denominator
        assert j >= 0
        self.arrays[i][j] = value

    def new(self, size):
        if self.pool:
            key = self.pool.pop()
        else:
            self.arrays.append(None)
            key = Q(1, len(self.arrays))

        i = key.denominator - 1
        self.arrays[i] = size * [Q(0)]
        return key

    def delete(self, key):
        i = key.denominator - 1
        assert i >= 1 and key.numerator == 1
        assert self.arrays[i] is not None
        self.arrays[i] = None

        if i == self.next_denominator - 2:
            self.next_denominator -= 1
        else:
            self.pool.append(key)
