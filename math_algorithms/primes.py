"""Prime factorization and divisors by trial division.

Signs: factorise one (or a few) numbers up to ~10^12, count or list divisors,
       number of distinct prime factors, "is n ugly / 7-smooth", sum of
       divisors, perfect numbers.
Approach: divide out 2, then odd d while d * d <= n. Anything left above 1 has
          no factor <= its square root, so it is prime. Divisors pair up as
          (d, n // d) with d <= sqrt(n), so only the small half is searched.
Complexity: O(sqrt(n)) per number. For many numbers <= N use the SPF sieve.
Gotchas:
  - The leftover n > 1 after the loop is a prime factor — forgetting it drops
    the largest prime (e.g. factorize(14) loses 7).
  - Perfect squares: d == n // d must be emitted once, not twice.
  - Compare d * d <= n, not d <= sqrt(n); floats round.
  - Divisor count and sum follow from the exponents: prod(e + 1) and
    prod((p^(e+1) - 1) / (p - 1)) — no enumeration needed.

Run the tests at the bottom with:  python3 math_algorithms/primes.py
"""


# ---------------------------------------------------------------- implementation


def is_prime(n):
    """Trial division by 2, 3 and then 6k +/- 1."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0:
            return False
        d += 6
    return True


def factorize(n):
    """{prime: exponent} for n >= 1 (empty dict for 1)."""
    f, d = {}, 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def divisors(n):
    """All positive divisors of n >= 1, ascending."""
    small, large = [], []
    d = 1
    while d * d <= n:
        if n % d == 0:
            small.append(d)
            if d != n // d:
                large.append(n // d)
        d += 1
    return small + large[::-1]


def divisor_count(n):
    count = 1
    for e in factorize(n).values():
        count *= e + 1
    return count


def divisor_sum(n):
    total = 1
    for p, e in factorize(n).items():
        total *= (p ** (e + 1) - 1) // (p - 1)
    return total


def is_smooth(n, primes=(2, 3, 5)):
    """True iff n >= 1 has no prime factors outside `primes` ("ugly number")."""
    if n < 1:
        return False
    for p in primes:
        while n % p == 0:
            n //= p
    return n == 1


# ------------------------------------------------------------------------ tests


def _naive_is_prime(n):
    return n >= 2 and all(n % d for d in range(2, n))


def test_is_prime_against_naive():
    for n in range(-5, 3000):
        assert is_prime(n) == _naive_is_prime(n), n


def test_is_prime_against_sieve_and_big_values():
    from sieve import prime_table

    table = prime_table(200_000)
    for n in range(200_001):
        assert is_prime(n) == bool(table[n])
    assert is_prime(10**9 + 7)
    assert is_prime(998_244_353)
    assert not is_prime(10**9 + 11)  # digit sum 3, so divisible by 3
    assert is_prime(2**31 - 1)  # Mersenne prime
    assert not is_prime(25) and not is_prime(49)  # squares of 6k +/- 1 primes
    assert not is_prime((10**6 + 3) * (10**6 + 33))  # product of two primes
    assert is_prime(10**6 + 3) and is_prime(10**6 + 33)


def test_factorize_rebuilds_n_with_prime_factors():
    import random

    rng = random.Random(12)
    cases = list(range(1, 2000)) + [2**40, 3**25, 999_999_999_989, 600851475143]
    cases += [rng.randint(1, 10**12) for _ in range(200)]
    for n in cases:
        prod = 1
        for p, e in factorize(n).items():
            assert e >= 1 and is_prime(p)
            prod *= p**e
        assert prod == n
    assert factorize(1) == {}
    assert factorize(14) == {2: 1, 7: 1}  # leftover prime must be kept
    assert factorize(600851475143) == {71: 1, 839: 1, 1471: 1, 6857: 1}


def test_divisors_against_brute_force():
    for n in range(1, 3000):
        assert divisors(n) == [d for d in range(1, n + 1) if n % d == 0]
    assert divisors(36) == [1, 2, 3, 4, 6, 9, 12, 18, 36]  # 6 appears once


def test_divisor_count_and_sum():
    import random

    rng = random.Random(13)
    for n in list(range(1, 1500)) + [rng.randint(1, 10**9) for _ in range(40)]:
        ds = divisors(n)
        assert divisor_count(n) == len(ds)
        assert divisor_sum(n) == sum(ds)
    perfect = [n for n in range(2, 10_000) if divisor_sum(n) - n == n]
    assert perfect == [6, 28, 496, 8128]


def test_is_smooth():
    ugly = [n for n in range(1, 61) if is_smooth(n)]
    assert ugly == [n for n in range(1, 61) if set(factorize(n)) <= {2, 3, 5}]
    assert ugly[:10] == [1, 2, 3, 4, 5, 6, 8, 9, 10, 12]
    assert not is_smooth(0) and not is_smooth(-8)
    assert is_smooth(49, primes=(7,)) and not is_smooth(14, primes=(7,))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
