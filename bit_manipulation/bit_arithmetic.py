"""Bit-level arithmetic — add without +, multiply by shifts, reverse bits, range AND.

Signs: "sum of two integers without + or -", "multiply without *", "reverse
       the bits of a 32-bit unsigned integer", "bitwise AND of all numbers in
       [left, right]".
Approach:
  - Add: a ^ b is the sum without carries; (a & b) << 1 is the carries.
    Repeat until no carry. In Python mask both to 32 bits every round, or a
    negative operand keeps carrying forever. Convert the result back to signed.
  - Multiply: shift-and-add. For each set bit i of b, add a << i.
  - Reverse bits: pull bits off the right of n, push onto the left of out,
    exactly 32 times (leading zeros count).
  - Range AND [l, r]: any bit that changes inside the range becomes 0. What
    survives is the common binary prefix of l and r. Shift both right until
    equal, then shift back; or clear r's lowest bit while r > l.
  - Divide without * / %: see math_algorithms/integer_division.py
    (divide_32bit, doubling + INT_MIN / -1 overflow rule).
Complexity: add O(32) rounds; multiply O(log b); reverse O(32); range AND O(32).
Gotchas:
  - Add with Python ints: (-1) + 1 never terminates without the 32-bit mask.
    The carry keeps moving left through infinite leading 1s.
  - Reverse bits must loop 32 times, not while n: 1 reverses to 2^31.
  - Range AND: l == 0 -> 0. Do not loop over the range (up to 2^31 values).

Run the tests at the bottom with:  python3 bit_manipulation/bit_arithmetic.py
"""

import random
from functools import reduce
from operator import and_

MASK32 = 0xFFFFFFFF
INT_MIN, INT_MAX = -(2**31), 2**31 - 1


# ---------------------------------------------------------------- implementation


def get_sum(a, b):
    """a + b in 32-bit two's complement using only bit ops (LeetCode 371)."""
    a &= MASK32
    b &= MASK32
    while b:
        a, b = (a ^ b) & MASK32, ((a & b) << 1) & MASK32
    return a - (1 << 32) if a >> 31 else a


def get_difference(a, b):
    """a - b = a + (~b + 1): negate in two's complement, then add."""
    return get_sum(a, get_sum(~b, 1))


def multiply(a, b):
    """a * b for any ints, by shift-and-add on |b|."""
    negative = (a < 0) != (b < 0)
    a, b = abs(a), abs(b)
    out = 0
    while b:
        if b & 1:
            out += a
        a <<= 1
        b >>= 1
    return -out if negative else out


def reverse_bits(n):
    """Reverse the 32 bits of an unsigned int (LeetCode 190)."""
    out = 0
    for _ in range(32):
        out = (out << 1) | (n & 1)
        n >>= 1
    return out


def range_bitwise_and(left, right):
    """AND of every integer in [left, right] = common prefix (LeetCode 201)."""
    shift = 0
    while left != right:
        left >>= 1
        right >>= 1
        shift += 1
    return left << shift


def range_bitwise_and_kernighan(left, right):
    """Same: clear right's lowest set bit until it is <= left."""
    while right > left:
        right &= right - 1
    return right


# ------------------------------------------------------------------------ tests


def _wrap32(x):
    x &= MASK32
    return x - (1 << 32) if x >> 31 else x


def test_get_sum_against_python_with_wraparound():
    rng = random.Random(30)
    edges = [0, 1, -1, INT_MAX, INT_MIN]
    pairs = [(a, b) for a in edges for b in edges]
    pairs += [(rng.randint(INT_MIN, INT_MAX), rng.randint(INT_MIN, INT_MAX)) for _ in range(5000)]
    for a, b in pairs:
        assert get_sum(a, b) == _wrap32(a + b), (a, b)
        assert get_difference(a, b) == _wrap32(a - b), (a, b)
    assert get_sum(INT_MAX, 1) == INT_MIN  # overflow wraps like C


def test_get_sum_small_exhaustive():
    for a in range(-64, 65):
        for b in range(-64, 65):
            assert get_sum(a, b) == a + b


def test_multiply_against_python():
    rng = random.Random(31)
    for _ in range(5000):
        a, b = rng.randint(-(10**9), 10**9), rng.randint(-(10**9), 10**9)
        assert multiply(a, b) == a * b
    for a in range(-20, 21):
        for b in range(-20, 21):
            assert multiply(a, b) == a * b


def test_reverse_bits_against_string():
    rng = random.Random(32)
    for n in [0, 1, MASK32, 0x80000000, 43261596] + [rng.randrange(2**32) for _ in range(3000)]:
        assert reverse_bits(n) == int(format(n, "032b")[::-1], 2)
        assert reverse_bits(reverse_bits(n)) == n
    assert reverse_bits(1) == 2**31  # leading zeros count


def test_range_and_against_reduce():
    rng = random.Random(33)
    for _ in range(3000):
        left = rng.randrange(0, 10**6)
        right = left + rng.randrange(0, 200)
        want = reduce(and_, range(left, right + 1))
        assert range_bitwise_and(left, right) == want
        assert range_bitwise_and_kernighan(left, right) == want
    assert range_bitwise_and(0, 0) == 0
    assert range_bitwise_and(1, INT_MAX) == 0  # the range is never iterated
    assert range_bitwise_and_kernighan(2**30, INT_MAX) == 2**30


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
