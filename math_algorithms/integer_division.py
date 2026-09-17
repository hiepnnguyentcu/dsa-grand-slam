"""Integer division and rounding — floor, ceil, truncate, round, on every sign.

Signs: negative operands, "ceil(a / b)" (pages, trips, eating speed), porting
       C/Java/Go logic (they truncate), "divide without * / %", any time the
       answer depends on which way a division rounds.
Approach: Python's // is *floor* division (towards -infinity) and % takes the
          sign of the divisor, so a == b * (a // b) + a % b always holds.
          Everything else is derived from floor:
  - ceil(a / b)  = -((-a) // b)
  - trunc(a / b) = floor for same signs, ceil for mixed signs
  - C-style remainder = a - b * trunc(a / b), which takes the sign of a
Complexity: O(1) (O(log^2) for the shift-subtract divider).
Gotchas:
  - -7 // 2 == -4 and -7 % 2 == 1 in Python; C gives -3 and -1.
  - int(a / b) goes through a float: wrong beyond 2^53, and wrong in the last
    digit well before overflow shows up.
  - (a + b - 1) // b is ceil only for b > 0 in Python (and additionally only
    for a >= 0 in C, where / truncates). -(-a // b) has no such caveat.
  - round() in Python is banker's rounding (round(2.5) == 2). For "round half
    away from zero" on integers, do it by hand.
  - The one 32-bit overflow case in division is INT_MIN / -1.

Run the tests at the bottom with:  python3 math_algorithms/integer_division.py
"""

INT_MIN, INT_MAX = -(2**31), 2**31 - 1


# ---------------------------------------------------------------- implementation


def floor_div(a, b):
    return a // b


def ceil_div(a, b):
    return -(-a // b)


def ceil_div_positive(a, b):
    """The common idiom — valid for b > 0 (and, in truncating languages, a >= 0)."""
    return (a + b - 1) // b


def trunc_div(a, b):
    """Rounds towards zero, like C / Java / Go."""
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def trunc_mod(a, b):
    """C-style remainder: a == b * trunc_div(a, b) + trunc_mod(a, b); sign of a."""
    return a - b * trunc_div(a, b)


def round_div(a, b):
    """a / b rounded to the nearest integer, ties away from zero."""
    q, r = divmod(abs(a), abs(b))
    if 2 * r >= abs(b):
        q += 1
    return q if (a < 0) == (b < 0) else -q


def divide_32bit(dividend, divisor):
    """LeetCode 29: truncating division without * / %, clamped to 32 bits.

    Work on magnitudes. Repeatedly subtract the largest divisor * 2^k that
    still fits; each subtraction contributes 2^k to the quotient — long
    division in base 2.
    """
    if divisor == 0:
        raise ZeroDivisionError
    if dividend == INT_MIN and divisor == -1:
        return INT_MAX  # the only overflowing case
    negative = (dividend < 0) != (divisor < 0)
    a, b = abs(dividend), abs(divisor)
    q = 0
    while a >= b:
        shift = 0
        while a >= (b << (shift + 1)):
            shift += 1
        a -= b << shift
        q += 1 << shift
    return -q if negative else q


# ------------------------------------------------------------------------ tests


def _cases():
    import random

    rng = random.Random(24)
    small = [(a, b) for a in range(-12, 13) for b in range(-5, 6) if b]
    big = []
    for _ in range(3000):
        a = rng.randint(-(10**40), 10**40)
        b = rng.choice([rng.randint(-(10**20), 10**20), rng.randint(-9, 9)]) or 1
        big.append((a, b))
    return small + big


def test_python_floor_semantics():
    assert -7 // 2 == -4 and -7 % 2 == 1
    assert 7 // -2 == -4 and 7 % -2 == -1
    assert -7 // -2 == 3 and -7 % -2 == -1
    for a, b in _cases():
        assert a == b * floor_div(a, b) + a % b
        assert a % b == 0 or (a % b > 0) == (b > 0)  # % follows the divisor


def test_against_exact_fractions():
    import math
    from fractions import Fraction

    for a, b in _cases():
        f = Fraction(a, b)
        assert floor_div(a, b) == math.floor(f)
        assert ceil_div(a, b) == math.ceil(f)
        assert trunc_div(a, b) == math.trunc(f)
        # round half away from zero, built from exact comparisons
        lo = math.floor(abs(f))
        nearest = lo + (abs(f) - lo >= Fraction(1, 2))
        assert round_div(a, b) == (nearest if f >= 0 else -nearest)


def test_all_sign_combinations_by_hand():
    #            a,  b, floor, ceil, trunc, c_mod, round
    table = [(7, 2, 3, 4, 3, 1, 4),
             (-7, 2, -4, -3, -3, -1, -4),
             (7, -2, -4, -3, -3, 1, -4),
             (-7, -2, 3, 4, 3, -1, 4),
             (6, 3, 2, 2, 2, 0, 2),
             (-6, 3, -2, -2, -2, 0, -2),
             (0, -5, 0, 0, 0, 0, 0),
             (1, 3, 0, 1, 0, 1, 0),
             (-1, 3, -1, 0, 0, -1, 0),
             (5, 4, 1, 2, 1, 1, 1),
             (-5, 4, -2, -1, -1, -1, -1)]
    for a, b, fl, ce, tr, cm, ro in table:
        assert (floor_div(a, b), ceil_div(a, b), trunc_div(a, b),
                trunc_mod(a, b), round_div(a, b)) == (fl, ce, tr, cm, ro), (a, b)


def test_trunc_mod_matches_c_identity():
    import math

    for a, b in _cases():
        r = trunc_mod(a, b)
        assert a == b * trunc_div(a, b) + r
        assert abs(r) < abs(b)
        assert r == 0 or (r > 0) == (a > 0)  # sign of the dividend
        if abs(a) < 2**52 and abs(b) < 2**52:  # fmod is exact on exact floats
            assert r == int(math.fmod(a, b))


def test_float_truncation_breaks_on_big_values():
    a, b = 10**18 + 1, 3  # exact quotient 333333333333333333
    assert trunc_div(a, b) == 333_333_333_333_333_333
    assert int(a / b) != trunc_div(a, b)


def test_ceil_idiom_needs_positive_divisor():
    for a in range(-50, 50):
        for b in range(1, 10):
            assert ceil_div_positive(a, b) == ceil_div(a, b)
    # negative divisor: ceil(7 / -2) = ceil(-3.5) = -3, the idiom gives -2
    assert ceil_div(7, -2) == -3
    assert ceil_div_positive(7, -2) == -2
    # in C the idiom also fails for a < 0, because / truncates:
    # (-4 + 3 - 1) / 3 is -2 / 3, which C truncates to 0; ceil(-4 / 3) is -1
    assert trunc_div(-4 + 3 - 1, 3) == 0
    assert ceil_div(-4, 3) == ceil_div_positive(-4, 3) == -1


def test_python_round_is_bankers():
    assert round(2.5) == 2 and round(3.5) == 4
    assert round_div(5, 2) == 3 and round_div(7, 2) == 4 and round_div(-5, 2) == -3


def test_divide_32bit():
    import random

    rng = random.Random(25)
    cases = [(INT_MIN, -1), (INT_MIN, 1), (INT_MAX, 1), (INT_MIN, INT_MIN),
             (0, 5), (7, -3), (-7, 3), (1, INT_MIN), (INT_MIN, 2)]
    cases += [(rng.randint(INT_MIN, INT_MAX), rng.randint(INT_MIN, INT_MAX) or 1)
              for _ in range(3000)]
    cases += [(rng.randint(INT_MIN, INT_MAX), rng.randint(-10, 10) or 1) for _ in range(3000)]
    for a, b in cases:
        expected = max(INT_MIN, min(INT_MAX, trunc_div(a, b)))
        assert divide_32bit(a, b) == expected, (a, b)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
