"""XOR tricks — single number I/II/III, missing number, find the difference.

Signs: "every element appears twice except one", "appears three times except
       one", "find the missing / extra one", O(1) extra space demanded, XOR
       of a range 0..n.
Approach: XOR is addition mod 2 per bit: a ^ a = 0, a ^ 0 = a, order does
          not matter. So XOR-ing everything cancels the pairs.
  - Single number I: XOR all.
  - Missing number in 0..n: XOR indices 0..n with the values; the present
    numbers cancel. Find the difference (s vs s + one char) is the same.
  - Single number III (two singles a, b): x = a ^ b != 0. Its lowest set bit
    is a bit where a and b differ, so split the array on that bit and XOR
    each half.
  - Single number II (others thrice): count each bit mod 3. Or keep that
    count in two bit-planes `ones`, `twos` (a mod-3 counter per bit):
        ones = (ones ^ x) & ~twos
        twos = (twos ^ x) & ~ones
    After all input, `ones` holds the bits whose count is 1 mod 3.
  - XOR of 0..n has period 4: [n, 1, n + 1, 0][n % 4].
Complexity: O(n) time, O(1) space for all of them (bit counting O(32 n)).
Gotchas:
  - Single number II with negatives: bit counting over 32 bits produces the
    unsigned pattern. Convert bit 31 back (x - 2^32). The ones/twos version
    works on Python ints directly, negatives included.
  - Single III: x & -x on the XOR, not on an element.
  - XOR swap breaks when both names alias the same slot (a[i] ^= a[i] -> 0).
    Python's a, b = b, a is the real answer; the trick is interview trivia.
  - Missing number via sum n(n+1)/2 - sum(a) also works; in fixed-width
    languages the XOR version cannot overflow.

Run the tests at the bottom with:  python3 bit_manipulation/xor_tricks.py
"""

import random
from collections import Counter
from functools import reduce
from operator import xor


# ---------------------------------------------------------------- implementation


def single_number(nums):
    """Every value appears twice except one (LeetCode 136)."""
    out = 0
    for x in nums:
        out ^= x
    return out


def single_number_ii_bits(nums):
    """Every value appears three times except one (LeetCode 137): per-bit mod 3."""
    out = 0
    for i in range(32):
        if sum((x >> i) & 1 for x in nums) % 3:
            out |= 1 << i
    return out - (1 << 32) if out >> 31 else out  # bit 31 is the sign


def single_number_ii_state(nums):
    """Same, with a two-bit mod-3 counter per bit position: 00 -> 01 -> 10 -> 00."""
    ones = twos = 0
    for x in nums:
        ones = (ones ^ x) & ~twos
        twos = (twos ^ x) & ~ones
    return ones


def single_number_iii(nums):
    """Two values appear once, the rest twice (LeetCode 260). Returns (smaller, larger)."""
    both = reduce(xor, nums, 0)
    diff = both & -both  # a bit where the two singles differ
    a = 0
    for x in nums:
        if x & diff:
            a ^= x
    b = both ^ a
    return (a, b) if a < b else (b, a)


def missing_number(nums):
    """nums holds n distinct values from 0..n; return the absent one (LeetCode 268)."""
    out = len(nums)
    for i, x in enumerate(nums):
        out ^= i ^ x
    return out


def find_the_difference(s, t):
    """t is s shuffled plus one extra letter (LeetCode 389)."""
    out = 0
    for ch in s + t:
        out ^= ord(ch)
    return chr(out)


def xor_swap(a, i, j):
    """Swap a[i], a[j] with no temp. Guard i == j or the slot becomes 0."""
    if i != j:
        a[i] ^= a[j]
        a[j] ^= a[i]
        a[i] ^= a[j]


def xor_upto(n):
    """0 ^ 1 ^ ... ^ n for n >= 0, in O(1)."""
    return (n, 1, n + 1, 0)[n % 4]


def xor_range(lo, hi):
    """lo ^ (lo + 1) ^ ... ^ hi for 0 <= lo <= hi: prefix XOR cancels the front."""
    return xor_upto(hi) ^ xor_upto(lo - 1) if lo else xor_upto(hi)


# ------------------------------------------------------------------------ tests


def _with_repeats(rng, k, singles, lo=-(2**31), hi=2**31 - 1):
    """Distinct values, each repeated k times, plus `singles` appearing once."""
    pool = rng.sample(range(lo, hi), rng.randint(0, 30) + len(singles))
    pool = [v for v in pool if v not in singles][:30]
    nums = [v for v in pool for _ in range(k)] + list(singles)
    rng.shuffle(nums)
    return nums


def _once(nums):
    return sorted(v for v, c in Counter(nums).items() if c == 1)


def test_single_number_random_including_negatives():
    rng = random.Random(10)
    for _ in range(500):
        s = rng.randint(-(2**31), 2**31 - 1)
        nums = _with_repeats(rng, 2, [s])
        assert single_number(nums) == _once(nums)[0] == s


def test_single_number_ii_both_ways():
    rng = random.Random(11)
    edges = [0, -1, 2**31 - 1, -(2**31)]
    for trial in range(500):
        s = edges[trial] if trial < len(edges) else rng.randint(-(2**31), 2**31 - 1)
        nums = _with_repeats(rng, 3, [s])
        assert single_number_ii_bits(nums) == s
        assert single_number_ii_state(nums) == s


def test_ones_twos_state_machine_counts_mod_3():
    # Feed one bit k times: (twos, ones) must read k mod 3 in binary.
    ones = twos = 0
    for k in range(1, 10):
        ones = (ones ^ 1) & ~twos
        twos = (twos ^ 1) & ~ones
        assert (twos << 1 | ones) == k % 3


def test_single_number_iii_random():
    rng = random.Random(12)
    for _ in range(500):
        a, b = rng.sample(range(-(2**31), 2**31), 2)
        nums = _with_repeats(rng, 2, [a, b])
        assert single_number_iii(nums) == tuple(_once(nums)) == tuple(sorted((a, b)))


def test_missing_number_exhaustive_small():
    rng = random.Random(13)
    for n in range(0, 40):
        for gone in range(n + 1):
            nums = [v for v in range(n + 1) if v != gone]
            rng.shuffle(nums)
            assert missing_number(nums) == gone
            assert n * (n + 1) // 2 - sum(nums) == gone  # second method agrees


def test_find_the_difference_random():
    rng = random.Random(14)
    letters = "abcdefghijklmnopqrstuvwxyz"
    for _ in range(500):
        s = "".join(rng.choice(letters) for _ in range(rng.randint(0, 20)))
        extra = rng.choice(letters)
        t = list(s + extra)
        rng.shuffle(t)
        t = "".join(t)
        assert find_the_difference(s, t) == extra
        assert (Counter(t) - Counter(s)).most_common(1)[0][0] == extra


def test_xor_swap_and_alias_trap():
    rng = random.Random(15)
    for _ in range(300):
        a = [rng.randint(-1000, 1000) for _ in range(5)]
        i, j = rng.randrange(5), rng.randrange(5)
        want = a[:]
        want[i], want[j] = want[j], want[i]
        xor_swap(a, i, j)
        assert a == want
    b = [7]
    b[0] ^= b[0]  # unguarded self-swap first step
    assert b == [0]


def test_xor_upto_and_range_against_reduce():
    for n in range(0, 600):
        assert xor_upto(n) == reduce(xor, range(n + 1), 0)
    rng = random.Random(16)
    for _ in range(2000):
        lo = rng.randrange(0, 10**6)
        hi = lo + rng.randrange(0, 300)
        assert xor_range(lo, hi) == reduce(xor, range(lo, hi + 1), 0)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
