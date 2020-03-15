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
        self.next_base = Q(0)

    def __getitem__(self, address: Q) -> Q:
        offset, base = divmod(address, 1)
        return self.stacks[base][offset]

    def __setitem__(self, address: Q, value: Q) -> None:
        offset, base = divmod(address, 1)
        self.stacks[base][offset] = value

    def new(self, size: int = 0) -> Q:
        if self.pool:
            base = self.pool.pop()
        else:
            base = self.next_base
            self.next_base = next_rational(self.next_base)

        self.stacks[base] = size * [Q(0)]
        return base

    def delete(self, base: Q) -> None:
        del self.stacks[base]
        self.pool.append(base)

    def push(self, base: Q, value: Q) -> None:
        self.stacks[base].append(value)

    def pop(self, base: Q) -> Q:
        return self.stacks[base].pop()

    def size(self, base: Q) -> int:
        return len(self.stacks[base])
