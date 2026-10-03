"""Counting bits — popcount for 0..n, number of 1 bits, Hamming distances.

Signs: "number of 1s in the binary of every i <= n", "Hamming weight",
       "positions where the bits differ", "sum of Hamming distances over all
       pairs", n up to 10^5 or 10^6 so per-pair work is too slow.
Approach:
  - Counting bits DP, two recurrences, each O(1) per i:
        bits[i] = bits[i >> 1] + (i & 1)     drop the last bit
        bits[i] = bits[i & (i - 1)] + 1      drop the lowest set bit
  - Hamming distance(x, y) = popcount(x ^ y).
  - Total Hamming distance over all pairs: handle each bit on its own. If c
    numbers have bit b set, that bit contributes c * (n - c) differing pairs.
    O(32 n) instead of O(n^2).
  - Number of 1 bits for a signed 32-bit input: mask to 32 bits first.
Complexity: counting bits O(n); Hamming distance O(1); total O(32 n).
Gotchas:
  - bits[i >> 1] needs i >> 1 < i, true for i >= 1: start the loop at 1.
  - Total Hamming distance counts unordered pairs; c * (n - c) already does.
    Do not double it.
  - Negative inputs to "number of 1 bits" mean the 32-bit pattern (-1 -> 32),
    not the magnitude.

Run the tests at the bottom with:  python3 bit_manipulation/counting_bits.py
"""

import random
from itertools import combinations

MASK32 = 0xFFFFFFFF


# ---------------------------------------------------------------- implementation


def count_bits_shift(n):
    """[popcount(i) for i in 0..n] via bits[i >> 1] (LeetCode 338)."""
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        bits[i] = bits[i >> 1] + (i & 1)
    return bits


def count_bits_lowest(n):
    """Same, via bits[i & (i - 1)] + 1."""
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        bits[i] = bits[i & (i - 1)] + 1
    return bits


def hamming_weight(x):
    """Set bits of x read as a 32-bit int, negatives included (LeetCode 191)."""
    x &= MASK32
    count = 0
    while x:
        x &= x - 1
        count += 1
    return count


def hamming_distance(x, y):
    """Bit positions where x and y differ (LeetCode 461)."""
    return ((x ^ y) & MASK32).bit_count()


def total_hamming_distance(nums, width=32):
    """Sum of hamming_distance over all unordered pairs (LeetCode 477)."""
    n = len(nums)
    total = 0
    for b in range(width):
        c = sum((x >> b) & 1 for x in nums)
        total += c * (n - c)
    return total


# ------------------------------------------------------------------------ tests


def test_count_bits_both_recurrences_match_bin():
    want = [bin(i).count("1") for i in range(5001)]
    assert count_bits_shift(5000) == want
    assert count_bits_lowest(5000) == want
    assert count_bits_shift(0) == [0]


def test_hamming_weight_unsigned_and_negative():
    rng = random.Random(20)
    for _ in range(3000):
        x = rng.randint(-(2**31), 2**31 - 1)
        pattern = format(x & MASK32, "032b")
        assert hamming_weight(x) == pattern.count("1")
    assert hamming_weight(-1) == 32
    assert hamming_weight(-(2**31)) == 1
    assert hamming_weight(0) == 0


def test_hamming_distance_against_strings():
    rng = random.Random(21)
    for _ in range(3000):
        x, y = rng.randrange(2**31), rng.randrange(2**31)
        a, b = format(x, "032b"), format(y, "032b")
        assert hamming_distance(x, y) == sum(p != q for p, q in zip(a, b))


def test_total_hamming_distance_against_all_pairs():
    rng = random.Random(22)
    for _ in range(200):
        nums = [rng.randrange(10**9) for _ in range(rng.randint(0, 40))]
        brute = sum(hamming_distance(a, b) for a, b in combinations(nums, 2))
        assert total_hamming_distance(nums) == brute
    assert total_hamming_distance([4, 14, 2]) == 6


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
