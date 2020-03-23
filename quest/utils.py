from fractions import Fraction as Q


def fraction_to_index(q: Q) -> int:
    num = q.numerator
    den = q.denominator
    assert 0 <= num < den
    return (den - 1) * (den - 2) // 2 + num


def next_fraction(q: Q) -> Q:
    assert 0 <= q.numerator < q.denominator
    dq = Q(1, q.denominator)

    while True:
        q += dq

        if q >= 1:
            return Q(1, dq.denominator + 1)

        if q.denominator == dq.denominator:
            return q
