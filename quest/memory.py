from fractions import Fraction as Q

from quest.utils import base_to_index


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
        self.stacks = []
        self.pool = []
        self.next_base = Q(0)

    def __getitem__(self, address: Q) -> Q:
        offset, base = divmod(address, 1)
        index = base_to_index(base)
        stack = self.stacks[index]
        return stack[offset % len(stack)]

    def __setitem__(self, address: Q, value: Q) -> None:
        offset, base = divmod(address, 1)
        index = base_to_index(base)
        stack = self.stacks[index]
        stack[offset % len(stack)] = value

    def new(self, size: int = 0) -> Q:
        if self.pool:
            base = self.pool.pop()
        else:
            base = self.next_base
            self.next_base = next_rational(self.next_base)

        index = base_to_index(base)

        while len(self.stacks) <= index:
            self.stacks.append(None)

        self.stacks[index] = size * [Q(0)]
        return base

    def delete(self, base: Q) -> None:
        base %= 1
        index = base_to_index(base)

        if self.stacks[index] is not None:
            self.stacks[index] = None
            self.pool.append(base)

    def push(self, base: Q, value: Q) -> None:
        index = base_to_index(base % 1)
        self.stacks[index].append(value)

    def pop(self, base: Q) -> Q:
        index = base_to_index(base % 1)
        return self.stacks[index].pop()

    def size(self, base: Q) -> int:
        index = base_to_index(base % 1)
        return len(self.stacks[index])
