"""GCD / LCM — Euclid, its extended form, and the array versions.

Signs: simplify a fraction, normalise a slope or ratio, "divides evenly",
       common period of repeating events, the gcd of a whole array, "can we
       measure exactly z litres with jugs x and y".
Approach: Euclid — gcd(a, b) == gcd(b, a % b), because anything dividing a and
          b also divides a - q*b. The extended form also returns x, y with
          a*x + b*y == gcd, which is what modular inverses and "is z
          reachable" problems need. lcm(a, b) = a // gcd(a, b) * b.
Complexity: O(log min(a, b)) — the remainders shrink at least as fast as the
            Fibonacci numbers do backwards.
Gotchas:
  - Divide before multiplying in lcm; a * b // gcd builds a needlessly large
    intermediate (and overflows in fixed-width languages).
  - gcd(0, 0) is 0 by convention, gcd(a, 0) is |a|. lcm with a 0 is 0.
  - Normalise signs: gcd is non-negative, whatever the inputs.
  - An array gcd can stop early once it hits 1.

Run the tests at the bottom with:  python3 math_algorithms/gcd_lcm.py
"""


# ---------------------------------------------------------------- implementation


def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    if a == 0 or b == 0:
        return 0
    return abs(a // gcd(a, b) * b)


def gcd_recursive(a, b):
    return abs(a) if b == 0 else gcd_recursive(b, a % b)


def extended_gcd(a, b):
    """(g, x, y) with a*x + b*y == g == gcd(a, b), g >= 0.

    Iterative: keep two rows (r, s, t) with a*s + b*t == r and run Euclid on
    the r column; the coefficients ride along for free.
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    if old_r < 0:
        old_r, old_s, old_t = -old_r, -old_s, -old_t
    return old_r, old_s, old_t


def array_gcd(nums):
    g = 0  # gcd identity
    for x in nums:
        g = gcd(g, x)
        if g == 1:
            break
    return g


def array_lcm(nums):
    l = 1  # lcm identity
    for x in nums:
        l = lcm(l, x)
    return l


def reduce_fraction(num, den):
    """num/den in lowest terms with a positive denominator."""
    if den == 0:
        raise ZeroDivisionError("zero denominator")
    g = gcd(num, den)
    num, den = num // g, den // g
    if den < 0:
        num, den = -num, -den
    return num, den


def can_measure(x, y, z):
    """Water jug: can jugs of capacity x and y hold exactly z litres in total?

    Bezout: the reachable amounts are exactly the multiples of gcd(x, y) that
    fit in both jugs combined.
    """
    if z > x + y:
        return False
    if z == 0:
        return True
    g = gcd(x, y)
    return g != 0 and z % g == 0


# ------------------------------------------------------------------------ tests


def test_gcd_matches_stdlib():
    import math
    import random

    rng = random.Random(7)
    cases = [(0, 0), (0, 5), (5, 0), (-4, 6), (4, -6), (-4, -6), (1, 1), (17, 17)]
    for _ in range(3000):
        cases.append((rng.randint(-(10**40), 10**40), rng.randint(-(10**40), 10**40)))
        cases.append((rng.randint(-100, 100), rng.randint(-100, 100)))
    for a, b in cases:
        assert gcd(a, b) == math.gcd(a, b)
        assert gcd_recursive(a, b) == math.gcd(a, b)


def test_gcd_of_consecutive_fibonacci_is_one():
    # worst case for Euclid: every quotient is 1
    a, b = 1, 1
    for _ in range(300):
        a, b = b, a + b
    assert gcd(a, b) == 1


def test_lcm_matches_stdlib():
    import math
    import random

    rng = random.Random(8)
    for _ in range(3000):
        a, b = rng.randint(-(10**15), 10**15), rng.randint(-(10**15), 10**15)
        assert lcm(a, b) == math.lcm(a, b)
    assert lcm(0, 7) == lcm(7, 0) == lcm(0, 0) == 0
    assert lcm(4, 6) == 12


def test_extended_gcd_bezout_identity():
    import math
    import random

    rng = random.Random(9)
    cases = [(0, 0), (0, 9), (9, 0), (-9, 0), (240, 46), (-240, 46)]
    cases += [(rng.randint(-(10**30), 10**30), rng.randint(-(10**30), 10**30)) for _ in range(2000)]
    for a, b in cases:
        g, x, y = extended_gcd(a, b)
        assert g == math.gcd(a, b)
        assert a * x + b * y == g


def test_array_gcd_and_lcm():
    import math
    import random

    rng = random.Random(10)
    for _ in range(500):
        nums = [rng.randint(-1000, 1000) for _ in range(rng.randint(0, 8))]
        assert array_gcd(nums) == math.gcd(*nums)
        assert array_lcm(nums) == math.lcm(*nums)
    assert array_gcd([]) == 0 and array_lcm([]) == 1
    assert array_gcd([12, 18, 24]) == 6
    assert array_lcm([2, 3, 4]) == 12


def test_reduce_fraction():
    import random
    from fractions import Fraction

    rng = random.Random(11)
    for _ in range(2000):
        n, d = rng.randint(-500, 500), rng.choice([i for i in range(-500, 501) if i])
        f = Fraction(n, d)
        assert reduce_fraction(n, d) == (f.numerator, f.denominator)
    assert reduce_fraction(0, -5) == (0, 1)
    try:
        reduce_fraction(1, 0)
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError("expected ZeroDivisionError")


def test_can_measure_against_bfs():
    from collections import deque

    def brute(x, y, z):
        seen, q = {(0, 0)}, deque([(0, 0)])
        while q:
            a, b = q.popleft()
            if a + b == z:
                return True
            pour_ab = min(a, y - b)
            pour_ba = min(b, x - a)
            for s in ((x, b), (a, y), (0, b), (a, 0),
                      (a - pour_ab, b + pour_ab), (a + pour_ba, b - pour_ba)):
                if s not in seen:
                    seen.add(s)
                    q.append(s)
        return False

    for x in range(0, 9):
        for y in range(0, 9):
            for z in range(0, 20):
                assert can_measure(x, y, z) == brute(x, y, z), (x, y, z)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
