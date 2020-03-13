from collections import deque
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
        self.queues = {}
        self.pool = []
        self.next_key = Q(0)

    def __getitem__(self, address: Q) -> Q:
        index, key = divmod(address, 1)
        assert index >= 0
        return self.queues[key][index]

    def __setitem__(self, address: Q, value: Q) -> None:
        index, key = divmod(address, 1)
        assert index >= 0
        self.queues[key][index] = value

    def new(self, size: int = 0) -> Q:
        if self.pool:
            key = self.pool.pop()
        else:
            key = self.next_key
            self.next_key = next_rational(self.next_key)

        self.queues[key] = deque(size * [Q(0)])
        return key

    def delete(self, key: Q) -> None:
        del self.queues[key]
        self.pool.append(key)

    def put(self, key: Q, value: Q) -> None:
        self.queues[key].append(value)

    def unput(self, key: Q) -> Q:
        return self.queues[key].pop()

    def get(self, key: Q) -> Q:
        return self.queues[key].popleft()

    def unget(self, key: Q, value: Q) -> None:
        self.queues[key].appendleft(value)

    def size(self, key: Q) -> int:
        return len(self.queues[key])
