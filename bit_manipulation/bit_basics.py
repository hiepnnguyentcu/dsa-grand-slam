"""Bit basics — single-bit ops, lowest set bit, powers of two, popcount, 32-bit.

Signs: "without converting to string", flags packed in an int, "is n a power
       of two / four", count 1 bits, porting C/Java code that relies on 32-bit
       overflow or unsigned shifts.
Approach: every idiom is one of four masks.
  - get   x >> i & 1      set   x | 1 << i
    clear x & ~(1 << i)   flip  x ^ 1 << i
  - x & (x - 1) clears the lowest set bit (the borrow flips it and every 0
    below it). x & -x isolates it (-x == ~x + 1 in two's complement).
  - Power of two: x > 0 and x & (x - 1) == 0. Power of four: also the one bit
    sits at an even index (x & 0x55555555), or equivalently x % 3 == 1.
  - Popcount: Kernighan loops x &= x - 1 once per set bit; Python 3.10+ has
    int.bit_count().
  - Python ints are unbounded: a negative number has infinitely many leading
    1s. Emulate 32 bits by masking with 0xFFFFFFFF (gives the unsigned view)
    and converting back with "if x >= 2^31: x -= 2^32".
Complexity: O(1) per idiom; Kernighan O(set bits); bit_count O(1) practically.
Gotchas:
  - Precedence: + - bind tighter than << >>, which bind tighter than &, ^, |.
    `1 << i - 1` is 1 << (i - 1). Comparisons bind loosest, so `x & 1 == 0`
    is (x & 1) == 0 in Python (it is NOT in C/Java). Bracket anyway.
  - ~x == -x - 1, never "flip within n bits". In n bits use x ^ ((1 << n) - 1).
  - bin(-5) is '-0b101', not two's complement. bin(-5).count("1") is the
    count of |x|. Mask first for the 32-bit pattern.
  - x >> k on a negative Python int is arithmetic (floor division by 2^k).
    Java's >>> (logical shift) is (x & 0xFFFFFFFF) >> k.
  - x & (x - 1) == 0 is also true for x == 0: guard x > 0.

Run the tests at the bottom with:  python3 bit_manipulation/bit_basics.py
"""

import random

MASK32 = 0xFFFFFFFF
INT_MIN, INT_MAX = -(2**31), 2**31 - 1


# ---------------------------------------------------------------- implementation


def get_bit(x, i):
    return (x >> i) & 1


def set_bit(x, i):
    return x | (1 << i)


def clear_bit(x, i):
    return x & ~(1 << i)


def toggle_bit(x, i):
    return x ^ (1 << i)


def clear_lowest(x):
    """Drop the lowest set bit: 0b10110 -> 0b10100."""
    return x & (x - 1)


def lowest_bit(x):
    """Keep only the lowest set bit: 0b10110 -> 0b10 (Fenwick's lowbit)."""
    return x & -x


def clear_bits_from(x, i):
    """Clear bits i and above (keep the low i bits)."""
    return x & ((1 << i) - 1)


def is_power_of_two(x):
    return x > 0 and x & (x - 1) == 0


def is_power_of_four(x):
    """One set bit at an even index. 4^k = (3 + 1)^k leaves remainder 1 mod 3."""
    return x > 0 and x & (x - 1) == 0 and x % 3 == 1


def is_power_of_four_32(x):
    """Same, for 32-bit inputs, with the even-position mask 0x55555555."""
    return x > 0 and x & (x - 1) == 0 and x & 0x55555555 != 0


def popcount_kernighan(x):
    """Number of set bits in x >= 0; one iteration per set bit."""
    count = 0
    while x:
        x &= x - 1
        count += 1
    return count


def popcount_32(x):
    """Set bits in the 32-bit two's-complement pattern of x (x may be negative)."""
    return (x & MASK32).bit_count()


def to_unsigned32(x):
    """Signed 32-bit value -> the same bits read as unsigned (0..2^32-1)."""
    return x & MASK32


def to_signed32(x):
    """Low 32 bits of x read as a signed two's-complement int."""
    x &= MASK32
    return x - (1 << 32) if x >> 31 else x


def logical_shift_right32(x, k):
    """Java's x >>> k on a 32-bit int."""
    return (x & MASK32) >> k


def highest_bit(x):
    """Value of the highest set bit of x > 0 (0b10110 -> 0b10000)."""
    return 1 << (x.bit_length() - 1)


def next_power_of_two(x):
    """Smallest power of two >= x, for x >= 1."""
    return 1 << (x - 1).bit_length()


# ------------------------------------------------------------------------ tests


def test_single_bit_ops_match_string_view():
    rng = random.Random(1)
    for _ in range(2000):
        x, i = rng.randrange(1 << 40), rng.randrange(45)
        s = list(format(x, "045b")[::-1])  # s[i] is bit i
        assert get_bit(x, i) == int(s[i])
        for fn, ch in ((set_bit, "1"), (clear_bit, "0")):
            t = s[:]
            t[i] = ch
            assert fn(x, i) == int("".join(t[::-1]), 2)
        t = s[:]
        t[i] = "1" if s[i] == "0" else "0"
        assert toggle_bit(x, i) == int("".join(t[::-1]), 2)


def test_lowest_bit_idioms_exhaustive():
    for x in range(1, 1 << 12):
        low = next(i for i in range(13) if x >> i & 1)
        assert lowest_bit(x) == 1 << low
        assert clear_lowest(x) == x - (1 << low)
        assert highest_bit(x) == 1 << (len(bin(x)) - 3)
        assert clear_bits_from(x, 5) == x % 32


def test_lowest_bit_works_on_negatives():
    # -x is ~x + 1, so x & -x still isolates the lowest set bit.
    for x in range(-500, 0):
        assert lowest_bit(x) == lowest_bit(-x)


def test_powers_against_sets():
    twos = {1 << k for k in range(70)}
    fours = {4**k for k in range(35)}
    for x in list(range(-20, 5000)) + list(twos) + [t + 1 for t in twos]:
        assert is_power_of_two(x) == (x in twos), x
        assert is_power_of_four(x) == (x in fours), x
        if x < 2**32:
            assert is_power_of_four_32(x) == (x in fours), x
    assert not is_power_of_two(0)  # the x > 0 guard matters


def test_next_power_of_two():
    for x in range(1, 3000):
        p = 1
        while p < x:
            p *= 2
        assert next_power_of_two(x) == p


def test_popcount_three_ways():
    rng = random.Random(2)
    for _ in range(3000):
        x = rng.randrange(1 << rng.randrange(1, 80))
        assert popcount_kernighan(x) == x.bit_count() == bin(x).count("1")


def test_popcount_32_of_negatives():
    assert popcount_32(-1) == 32
    assert popcount_32(INT_MIN) == 1
    assert popcount_32(-2) == 31
    assert bin(-1).count("1") == 1  # the trap: bin shows sign + magnitude


def test_signed_unsigned_round_trip():
    rng = random.Random(3)
    edges = [0, 1, -1, INT_MAX, INT_MIN, INT_MAX - 1, INT_MIN + 1]
    for x in edges + [rng.randint(INT_MIN, INT_MAX) for _ in range(5000)]:
        u = to_unsigned32(x)
        assert 0 <= u <= MASK32
        assert u == (x if x >= 0 else x + 2**32)
        assert to_signed32(u) == x
    # Overflow wraps exactly like C int32.
    assert to_signed32(INT_MAX + 1) == INT_MIN
    assert to_signed32(INT_MIN - 1) == INT_MAX
    assert to_signed32(2**32 + 5) == 5


def test_logical_vs_arithmetic_shift():
    assert -8 >> 1 == -4  # Python: arithmetic
    assert logical_shift_right32(-8, 1) == 0x7FFFFFFC  # Java's >>>
    rng = random.Random(4)
    for _ in range(2000):
        x, k = rng.randint(INT_MIN, INT_MAX), rng.randrange(32)
        assert x >> k == x // (2**k)
        assert logical_shift_right32(x, k) == to_unsigned32(x) // (2**k)


def test_not_is_minus_x_minus_one():
    for x in range(-100, 100):
        assert ~x == -x - 1
    assert 0b1010 ^ 0b1111 == 0b0101  # complement within 4 bits


def test_precedence_traps():
    i = 3
    assert 1 << i - 1 == 4  # 1 << (i - 1), not (1 << i) - 1
    assert (6 & 1 == 0) is True  # (6 & 1) == 0 in Python; 6 & (1 == 0) in C
    assert 2 + 1 << 2 == 12


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
