"""Modular arithmetic and modular inverses.

Signs: "return the answer modulo 10^9 + 7", counts too large to hold,
       combinatorics under a modulus, hashing, "divide" inside a mod.
Approach: (a + b), (a - b) and (a * b) all commute with "mod m", so reduce
          after every step and the numbers stay small. Division does *not*
          commute; instead multiply by the modular inverse, the x with
          a * x == 1 (mod m). For prime m, Fermat gives x = a^(m-2). For any
          m with gcd(a, m) == 1, extended Euclid gives it.
Complexity: O(1) per add/multiply, O(log m) per inverse.
Gotchas:
  - Never divide a reduced value: (a % m) // b is not (a // b) % m.
  - Subtraction: Python's % is already non-negative for m > 0. In C/Java
    write (a - b + m) % m.
  - The inverse exists only when gcd(a, m) == 1. Fermat's formula on a
    non-prime modulus returns garbage silently.
  - Reduce before comparing: "is the answer 0" means "is it 0 mod m".

Run the tests at the bottom with:  python3 math_algorithms/modular.py
"""

from fast_power import pow_mod
from gcd_lcm import extended_gcd

MOD = 10**9 + 7


# ---------------------------------------------------------------- implementation


def mod_add(a, b, m=MOD):
    return (a + b) % m


def mod_sub(a, b, m=MOD):
    return (a - b) % m  # Python keeps this in [0, m); C needs + m first


def mod_mul(a, b, m=MOD):
    return a * b % m


def inv_fermat(a, p=MOD):
    """a^-1 mod p for PRIME p and a not divisible by p."""
    if a % p == 0:
        raise ZeroDivisionError("0 has no inverse")
    return pow_mod(a, p - 2, p)


def inv_euclid(a, m):
    """a^-1 mod m for any m >= 1 with gcd(a, m) == 1."""
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse mod {m}")
    return x % m


def mod_div(a, b, m=MOD):
    """a / b in the field mod prime m."""
    return a * inv_fermat(b, m) % m


def inverses_upto(n, p=MOD):
    """inv[i] == i^-1 mod p for 1 <= i <= n (< p), in O(n) total.

    From p = (p // i) * i + p % i: taking both sides mod p and dividing by
    i * (p % i) gives inv[i] = -(p // i) * inv[p % i], and p % i < i is
    already known.
    """
    inv = [0, 1] + [0] * (n - 1) if n >= 1 else [0]
    for i in range(2, n + 1):
        inv[i] = (p - p // i) * inv[p % i] % p
    return inv


# ------------------------------------------------------------------------ tests


def test_operations_match_reducing_at_the_end():
    import random

    rng = random.Random(15)
    for _ in range(2000):
        m = rng.choice([MOD, 998_244_353, 2, 1, rng.randint(1, 10**12)])
        a, b = rng.randint(-(10**20), 10**20), rng.randint(-(10**20), 10**20)
        assert mod_add(a % m, b % m, m) == (a + b) % m
        assert mod_sub(a % m, b % m, m) == (a - b) % m
        assert mod_mul(a % m, b % m, m) == (a * b) % m
        assert 0 <= mod_sub(a % m, b % m, m) < m


def test_long_sum_reduced_as_it_goes():
    import random

    rng = random.Random(16)
    xs = [rng.randint(-(10**18), 10**18) for _ in range(5000)]
    total, prod = 0, 1
    for x in xs:
        total = mod_add(total, x)
        prod = mod_mul(prod, x)
    assert total == sum(xs) % MOD
    exact = 1
    for x in xs:
        exact *= x
    assert prod == exact % MOD


def test_dividing_a_reduced_number_is_wrong():
    a, b = 10**12, 4  # a is divisible by b
    wrong = (a % MOD) // b % MOD
    right = mod_div(a % MOD, b)
    assert right == (a // b) % MOD
    assert wrong != right


def test_inverses_match_builtin():
    import random

    rng = random.Random(17)
    for p in (MOD, 998_244_353, 2, 3, 13):
        for _ in range(300):
            a = rng.randint(-(10**15), 10**15)
            if a % p == 0:
                continue
            assert inv_fermat(a, p) == pow(a, -1, p)
            assert inv_euclid(a, p) == pow(a, -1, p)
            assert a * inv_fermat(a, p) % p == 1


def test_euclid_inverse_on_composite_modulus():
    import math
    import random

    rng = random.Random(18)
    for _ in range(3000):
        m = rng.randint(1, 10**9)
        a = rng.randint(-(10**12), 10**12)
        if math.gcd(a, m) == 1:
            assert inv_euclid(a, m) == pow(a, -1, m)
        else:
            try:
                inv_euclid(a, m)
            except ValueError:
                pass
            else:
                raise AssertionError((a, m))


def test_fermat_is_wrong_on_composite_modulus():
    a, m = 3, 10  # gcd 1, so the inverse exists: 3 * 7 == 21 == 1
    assert inv_euclid(a, m) == 7
    assert inv_fermat(a, m) != 7  # 3^8 % 10 == 1, not an inverse


def test_inverse_of_zero_raises():
    for fn, args in ((inv_fermat, (0, 7)), (inv_fermat, (14, 7)), (inv_euclid, (0, 7))):
        try:
            fn(*args)
        except (ZeroDivisionError, ValueError):
            pass
        else:
            raise AssertionError(args)


def test_linear_inverse_table():
    for p in (MOD, 13, 2):
        n = min(p - 1, 5000)
        inv = inverses_upto(n, p)
        assert len(inv) == n + 1
        for i in range(1, n + 1):
            assert inv[i] == pow(i, -1, p)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
