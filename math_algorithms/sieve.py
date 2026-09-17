"""Sieve of Eratosthenes — prime table, and the smallest-prime-factor sieve.

Signs: many primality checks up to N, "count primes below n", factorise lots
       of numbers <= N quickly, anything over "all primes up to 10^6/10^7".
Approach: every composite has a prime factor <= its square root, so crossing
          off the multiples of each prime p leaves only primes. Start at p*p:
          smaller multiples k*p (k < p) were already crossed off by k's own
          smallest prime. The SPF variant records *which* prime crossed each
          number off first; following spf[] down factorises any n <= N in
          O(log n).
Complexity: O(N log log N) time, O(N) space. SPF factorisation O(log n) per query.
Gotchas:
  - Loop p only up to isqrt(N). int(N ** 0.5) goes through a float and is off
    by one for large N — math.isqrt-style integer roots are exact.
  - Guard N < 2: slicing two "not prime" bytes into a shorter table silently
    grows it.
  - bytearray slice assignment is the fast path in Python; a Python-level
    inner loop is ~10x slower.

Run the tests at the bottom with:  python3 math_algorithms/sieve.py
"""


# ---------------------------------------------------------------- implementation


def isqrt(n):
    """floor(sqrt(n)) for n >= 0, exactly, via Newton's method on integers.

    Start above the root (any x0 >= sqrt(n) works) and step down; the iterate
    decreases strictly until it reaches the floor root, then would go up.
    """
    if n < 0:
        raise ValueError("square root of negative number")
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + 1) // 2)  # >= sqrt(n)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def prime_table(n):
    """is_p[i] == 1 iff i is prime, for 0 <= i <= n."""
    if n < 2:
        return bytearray(max(n + 1, 0))
    is_p = bytearray([1]) * (n + 1)
    is_p[0] = is_p[1] = 0
    for p in range(2, isqrt(n) + 1):
        if is_p[p]:
            is_p[p * p :: p] = bytes(len(range(p * p, n + 1, p)))
    return is_p


def primes_upto(n):
    """All primes <= n, ascending."""
    return [i for i, flag in enumerate(prime_table(n)) if flag]


def count_primes_below(n):
    """LeetCode 204 wording: primes strictly less than n."""
    return sum(prime_table(n - 1)) if n > 2 else 0


def spf_sieve(n):
    """spf[i] == smallest prime factor of i, for 2 <= i <= n (spf[0], spf[1] are 0, 1)."""
    spf = list(range(n + 1))
    for p in range(2, isqrt(n) + 1 if n >= 0 else 0):
        if spf[p] == p:
            for m in range(p * p, n + 1, p):
                if spf[m] == m:
                    spf[m] = p
    return spf


def factorize_with_spf(x, spf):
    """{prime: exponent} for 1 <= x < len(spf), by repeatedly dividing out spf[x]."""
    f = {}
    while x > 1:
        p = spf[x]
        while x % p == 0:
            f[p] = f.get(p, 0) + 1
            x //= p
    return f


# ------------------------------------------------------------------------ tests


def _is_prime_naive(n):
    return n >= 2 and all(n % d for d in range(2, n))


def test_isqrt_matches_stdlib():
    import math
    import random

    rng = random.Random(3)
    cases = list(range(0, 2000)) + [10**k for k in range(40)]
    for _ in range(3000):
        r = rng.getrandbits(rng.randint(1, 300))
        cases += [r, r * r, r * r - 1, r * r + 1]
    for n in cases:
        if n >= 0:
            assert isqrt(n) == math.isqrt(n)


def test_float_sqrt_is_wrong_for_big_squares():
    # the reason for isqrt: floats lose the last digits
    n = (10**17 + 3) ** 2 - 1
    assert int(n**0.5) != isqrt(n)
    assert isqrt(n) == 10**17 + 2


def test_primes_against_trial_division():
    for n in range(-3, 300):
        assert primes_upto(n) == [i for i in range(n + 1) if _is_prime_naive(i)]


def test_small_n_does_not_grow_the_table():
    assert len(prime_table(0)) == 1
    assert len(prime_table(1)) == 2
    assert len(prime_table(-5)) == 0
    assert primes_upto(2) == [2]


def test_known_prime_counts():
    # pi(10^k) is a well-known sequence: 4, 25, 168, 1229, 9592, 78498
    for k, pi in enumerate([4, 25, 168, 1229, 9592, 78498], start=1):
        assert len(primes_upto(10**k)) == pi


def test_count_primes_below_is_strict():
    assert count_primes_below(10) == 4  # 2, 3, 5, 7
    assert count_primes_below(11) == 4  # 11 itself is excluded
    assert count_primes_below(12) == 5
    for n in (0, 1, 2):
        assert count_primes_below(n) == 0
    assert count_primes_below(3) == 1


def test_spf_against_naive():
    n = 3000
    spf = spf_sieve(n)
    for i in range(2, n + 1):
        smallest = next(d for d in range(2, i + 1) if i % d == 0)
        assert spf[i] == smallest
    assert spf[0] == 0 and spf[1] == 1


def test_factorize_with_spf_rebuilds_the_number():
    import random

    n = 10**5
    spf = spf_sieve(n)
    rng = random.Random(4)
    for x in [1, 2, n, 65536, 99991] + [rng.randint(1, n) for _ in range(2000)]:
        f = factorize_with_spf(x, spf)
        prod = 1
        for p, e in f.items():
            assert _is_prime_naive(p) if p < 1000 else spf[p] == p
            prod *= p**e
        assert prod == x
    assert factorize_with_spf(360, spf) == {2: 3, 3: 2, 5: 1}


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
