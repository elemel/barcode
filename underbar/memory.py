from fractions import Fraction as Q


def next_rational(q: Q) -> Q:
    dq = Q(1, q.denominator)

    while True:
        q += dq

        if q >= 1:
            return Q(1, dq.denominator + 1)

        if q.denominator == dq.denominator:
            return q


class Memory:
    def __init__(self, size: int) -> None:
        self.arrays = {Q(0): size * [Q(0)]}
        self.pool = []
        self.next_key = Q(1, 2)

    def __getitem__(self, address: Q) -> Q:
        index, key = divmod(address, 1)
        assert index >= 0
        return self.arrays[key][index]

    def __setitem__(self, address: Q, value: Q) -> None:
        index, key = divmod(address, 1)
        assert index >= 0
        self.arrays[key][index] = value

    def new(self, size: int) -> Q:
        if self.pool:
            key = self.pool.pop()
        else:
            key = self.next_key
            self.next_key = next_rational(self.next_key)

        self.arrays[key] = size * [Q(0)]
        return key

    def delete(self, key: Q) -> None:
        del self.arrays[key]
        self.pool.append(key)
