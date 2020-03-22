from fractions import Fraction as Q


def base_to_index(base: Q) -> int:
	num = base.numerator
	den = base.denominator
	assert 0 <= num < den
	return  (den - 1) * (den - 2) // 2 + num
