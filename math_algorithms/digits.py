"""Digit manipulation and fixed-width overflow checks.

Signs: reverse an integer, palindrome number "without converting to a
       string", digit sum / digital root, happy numbers, "assume a 32-bit
       environment", string-to-integer (atoi) with clamping.
Approach: n % 10 is the last digit, n // 10 drops it; r = r * 10 + d appends
          a digit on the right. For fixed-width targets, test the bound
          *before* the multiply-add, because in C the overflow has already
          happened by the time you could look at the result.
Complexity: O(number of digits).
Gotchas:
  - Peel digits from abs(x): in Python -123 % 10 == 7, not 3.
  - Palindrome by reversing half: stop when the reversed half catches up; the
    middle digit of an odd length is dropped with half // 10. Numbers ending
    in 0 (other than 0) can never be palindromes and break the half trick.
  - 32-bit range is asymmetric: -2^31 .. 2^31 - 1.
  - Python never overflows, so the fixed-width versions below only earn their
    keep as a model for C/Java/Go — test them against a big-int clamp.

Run the tests at the bottom with:  python3 math_algorithms/digits.py
"""

INT_MIN, INT_MAX = -(2**31), 2**31 - 1


# ---------------------------------------------------------------- implementation


def reverse_int(x):
    """Reverse the decimal digits of x keeping the sign; 0 if outside 32 bits."""
    sign, x, r = (-1 if x < 0 else 1), abs(x), 0
    while x:
        x, d = divmod(x, 10)
        r = r * 10 + d
    r *= sign
    return r if INT_MIN <= r <= INT_MAX else 0


def reverse_int_32(x):
    """Same result, written as if r could never exceed 32 bits.

    Only non-negative magnitudes are built, against the limit for the sign.
    Before r * 10 + d, check r > (limit - d) // 10; that rearranges
    r * 10 + d > limit without computing the overflowing value.
    """
    neg = x < 0
    limit = -INT_MIN if neg else INT_MAX
    x, r = abs(x), 0
    while x:
        d = x % 10
        x //= 10
        if r > (limit - d) // 10:
            return 0
        r = r * 10 + d
    return -r if neg else r


def is_pal_number(x):
    """Palindrome check on digits only, reversing just the lower half."""
    if x < 0 or (x % 10 == 0 and x):
        return False
    half = 0
    while x > half:
        x, d = divmod(x, 10)
        half = half * 10 + d
    return x == half or x == half // 10  # even length, or odd with a middle digit


def digit_sum(x):
    x, s = abs(x), 0
    while x:
        x, d = divmod(x, 10)
        s += d
    return s


def digital_root(x):
    """Repeated digit sum of x >= 0 in O(1): n == digit_sum(n) (mod 9)."""
    return 0 if x == 0 else 1 + (x - 1) % 9


def is_happy(n):
    """Repeatedly replace n by the sum of squared digits; happy if it reaches 1.

    The sequence is bounded (a 4+ digit number always shrinks), so it must
    cycle. Floyd's tortoise and hare finds the cycle without a set.
    """
    def step(v):
        s = 0
        while v:
            v, d = divmod(v, 10)
            s += d * d
        return s

    slow, fast = n, step(n)
    while fast != 1 and slow != fast:
        slow, fast = step(slow), step(step(fast))
    return fast == 1


def my_atoi(s):
    """LeetCode 8: skip spaces, optional sign, digits until a non-digit, clamp to 32 bits."""
    i, n = 0, len(s)
    while i < n and s[i] == " ":
        i += 1
    neg = False
    if i < n and s[i] in "+-":
        neg = s[i] == "-"
        i += 1
    limit = -INT_MIN if neg else INT_MAX
    r = 0
    while i < n and "0" <= s[i] <= "9":
        d = ord(s[i]) - 48
        if r > (limit - d) // 10:  # same pre-check as reverse_int_32
            return INT_MIN if neg else INT_MAX
        r = r * 10 + d
        i += 1
    return -r if neg else r


# ------------------------------------------------------------------------ tests


def _reverse_via_string(x):
    r = int(str(abs(x))[::-1]) * (-1 if x < 0 else 1)
    return r if INT_MIN <= r <= INT_MAX else 0


def _values():
    import random

    rng = random.Random(43)
    vals = list(range(-1200, 1200))
    vals += [INT_MIN, INT_MAX, INT_MIN + 1, INT_MAX - 1, 1_463_847_412, -1_463_847_412,
             1_463_847_413, 1_463_847_422, 2_147_483_641, -2_147_483_641, 1_000_000_003,
             8_463_847_412, -8_463_847_412, 7_463_847_412, -9_463_847_412]
    vals += [rng.randint(INT_MIN, INT_MAX) for _ in range(20_000)]
    vals += [rng.randint(-(10**12), 10**12) for _ in range(2000)]
    return vals


def test_reverse_int_against_string_reversal():
    for x in _values():
        assert reverse_int(x) == _reverse_via_string(x), x
        assert reverse_int_32(x) == _reverse_via_string(x), x


def test_reverse_boundaries():
    assert reverse_int(123) == 321
    assert reverse_int(-123) == -321
    assert reverse_int(120) == 21
    assert reverse_int(0) == 0
    assert reverse_int(1_534_236_469) == 0  # 9_646_324_351 overflows
    # 2_147_483_647 exactly: reachable only from 7_463_847_412, itself > 32 bits,
    # but the function takes any int, so the edge is still testable
    assert reverse_int_32(7_463_847_412) == INT_MAX
    assert reverse_int_32(-8_463_847_412) == INT_MIN  # |INT_MIN| fits on the negative side
    assert reverse_int_32(8_463_847_412) == 0  # 2_147_483_648 does not fit as a positive
    assert reverse_int_32(-9_463_847_412) == 0


def test_palindrome_against_string():
    for x in _values():
        assert is_pal_number(x) == (x >= 0 and str(x) == str(x)[::-1]), x
    for x in (0, 7, 11, 121, 1221, 12321, 1_000_000_001):
        assert is_pal_number(x)
    for x in (-121, 10, 100, 1210, 123):
        assert not is_pal_number(x)


def test_digit_sum_and_root():
    for x in _values():
        assert digit_sum(x) == sum(map(int, str(abs(x))))
        if x >= 0:
            r = x
            while r >= 10:
                r = digit_sum(r)
            assert digital_root(x) == r


def test_is_happy_against_set_based_detection():
    def brute(n):
        seen = set()
        while n != 1 and n not in seen:
            seen.add(n)
            n = sum(int(c) ** 2 for c in str(n))
        return n == 1

    for n in list(range(1, 5000)) + [10**18, 2**31 - 1]:
        assert is_happy(n) == brute(n), n
    assert [n for n in range(1, 50) if is_happy(n)] == [1, 7, 10, 13, 19, 23, 28, 31, 32, 44, 49]


def test_atoi_examples():
    cases = {"42": 42, "   -42": -42, "4193 with words": 4193, "words 987": 0,
             "-91283472332": INT_MIN, "91283472332": INT_MAX, "+1": 1, "+-12": 0,
             "": 0, "   ": 0, "-": 0, "00000-42a1234": 0, "  0000000000012345678": 12345678,
             "2147483647": INT_MAX, "2147483648": INT_MAX, "-2147483648": INT_MIN,
             "-2147483649": INT_MIN, "-2147483647": -2147483647, " 1 2": 1, "3.14": 3}
    for s, expected in cases.items():
        assert my_atoi(s) == expected, s


def test_atoi_against_regex_and_clamp():
    import random
    import re

    rng = random.Random(44)
    alphabet = " +-0123456789a."
    for _ in range(20_000):
        s = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 14)))
        if rng.random() < 0.3:
            s = " " * rng.randint(0, 2) + rng.choice(["", "-", "+"]) + str(rng.randint(0, 10**12))
        m = re.match(r" *([+-]?)(\d+)", s)
        expected = 0
        if m:
            expected = int(m.group(1) + m.group(2))
            expected = max(INT_MIN, min(INT_MAX, expected))
        assert my_atoi(s) == expected, s


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
