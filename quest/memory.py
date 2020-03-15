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
    def __init__(self) -> None:
        self.stacks = {}
        self.pool = []
        self.next_key = Q(0)

    def __getitem__(self, address: Q) -> Q:
        index, key = divmod(address, 1)
        assert index >= 0
        return self.stacks[key][index]

    def __setitem__(self, address: Q, value: Q) -> None:
        index, key = divmod(address, 1)
        assert index >= 0
        self.stacks[key][index] = value

    def new(self, size: int = 0) -> Q:
        if self.pool:
            key = self.pool.pop()
        else:
            key = self.next_key
            self.next_key = next_rational(self.next_key)

        self.stacks[key] = size * [Q(0)]
        return key

    def delete(self, key: Q) -> None:
        del self.stacks[key]
        self.pool.append(key)

    def push(self, key: Q, value: Q) -> None:
        self.stacks[key].append(value)

    def pop(self, key: Q) -> Q:
        return self.stacks[key].pop()

    def size(self, key: Q) -> int:
        return len(self.stacks[key])
