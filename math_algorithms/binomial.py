"""Binomial coefficients — Pascal's triangle and precomputed factorials.

Signs: "choose k of n", count lattice paths, combinations modulo a prime,
       Pascal's triangle rows, many C(n, k) queries.
Approach:
  - Small n, or a non-prime modulus: Pascal DP,
    C(n, k) = C(n-1, k-1) + C(n-1, k) — only additions, so any modulus works.
  - Large n under a prime modulus: precompute n! and (n!)^-1 once; then
    C(n, k) = n! / (k! (n-k)!) is three table lookups.
  - Exact big values: multiply-then-divide, C(n, k) = C(n, k-1) * (n-k+1) / k;
    each partial product is itself a binomial, so the division is exact.
Complexity: Pascal O(n^2). Factorial tables O(N) build, O(1) per query.
Gotchas:
  - Build inverse factorials backwards from one Fermat inverse:
    inv_fact[i-1] = inv_fact[i] * i. N separate inverses cost O(N log p).
  - k < 0 or k > n must return 0, not index out of range (or wrap around to
    the end of the list, which Python does silently for negative k).
  - The factorial trick needs n < p: n! is 0 mod p once n >= p.
  - Use symmetry k = min(k, n - k) in the exact loop.

Run the tests at the bottom with:  python3 math_algorithms/binomial.py
"""

from fast_power import pow_mod

MOD = 10**9 + 7


# ---------------------------------------------------------------- implementation


def make_ncr(N, mod=MOD):
    """Returns ncr(n, k) = C(n, k) % mod for 0 <= n <= N. mod must be a prime > N."""
    fact = [1] * (N + 1)
    for i in range(1, N + 1):
        fact[i] = fact[i - 1] * i % mod
    inv_fact = [1] * (N + 1)
    inv_fact[N] = pow_mod(fact[N], mod - 2, mod)
    for i in range(N, 0, -1):
        inv_fact[i - 1] = inv_fact[i] * i % mod

    def ncr(n, k):
        if k < 0 or k > n:
            return 0
        return fact[n] * inv_fact[k] % mod * inv_fact[n - k] % mod

    return ncr


def pascal(n):
    """The first n rows of Pascal's triangle (row i has i + 1 entries)."""
    if n <= 0:
        return []
    rows = [[1]]
    for _ in range(n - 1):
        prev = rows[-1]
        rows.append([1] + [a + b for a, b in zip(prev, prev[1:])] + [1])
    return rows


def pascal_table(N, mod=None):
    """C[n][k] for 0 <= k <= n <= N, optionally mod anything (prime or not)."""
    C = [[0] * (N + 1) for _ in range(N + 1)]
    for n in range(N + 1):
        C[n][0] = 1
        for k in range(1, n + 1):
            v = C[n - 1][k - 1] + C[n - 1][k]
            C[n][k] = v % mod if mod else v
    return C


def pascal_row(n):
    """Row n alone in O(n) extra space, updating right-to-left so each cell
    still reads the previous row's value on its left."""
    row = [1] * (n + 1)
    for i in range(1, n):
        for k in range(i, 0, -1):
            row[k] += row[k - 1]
    return row


def comb_exact(n, k):
    """Exact C(n, k) with Python big ints."""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    c = 1
    for i in range(1, k + 1):
        c = c * (n - k + i) // i  # c is C(n-k+i, i): always an integer
    return c


# ------------------------------------------------------------------------ tests


def test_ncr_matches_stdlib():
    import math

    N = 400
    ncr = make_ncr(N)
    for n in range(N + 1):
        for k in range(-2, n + 3):
            expected = math.comb(n, k) % MOD if 0 <= k <= n else 0
            assert ncr(n, k) == expected


def test_ncr_large_n_random_queries():
    import math
    import random

    N = 200_000
    ncr = make_ncr(N)
    rng = random.Random(19)
    for _ in range(100):
        n = rng.randint(0, N)
        k = rng.randint(0, n)
        assert ncr(n, k) == math.comb(n, k) % MOD
    assert ncr(N, 0) == ncr(N, N) == 1


def test_ncr_small_prime():
    import math

    p = 13
    ncr = make_ncr(p - 1, p)
    for n in range(p):
        for k in range(n + 1):
            assert ncr(n, k) == math.comb(n, k) % p


def test_negative_k_does_not_wrap():
    ncr = make_ncr(10)
    assert ncr(5, -1) == 0  # fact list would happily index [-1]
    assert ncr(5, 6) == 0
    assert comb_exact(5, -1) == 0 and comb_exact(5, 6) == 0


def test_pascal_rows():
    import math

    rows = pascal(30)
    assert len(rows) == 30
    for n, row in enumerate(rows):
        assert row == [math.comb(n, k) for k in range(n + 1)]
        assert pascal_row(n) == row
        assert sum(row) == 2**n
    assert pascal(0) == [] and pascal(1) == [[1]]
    assert pascal(5)[-1] == [1, 4, 6, 4, 1]


def test_pascal_table_with_composite_modulus():
    import math

    # 10^9 + 7 factorial tricks cannot do mod 12 (not prime); Pascal can.
    C = pascal_table(60, 12)
    for n in range(61):
        for k in range(n + 1):
            assert C[n][k] == math.comb(n, k) % 12
    exact = pascal_table(40)
    assert exact[40][20] == math.comb(40, 20)


def test_comb_exact_big_values():
    import math
    import random

    rng = random.Random(20)
    for _ in range(300):
        n = rng.randint(0, 3000)
        k = rng.randint(-5, n + 5)
        assert comb_exact(n, k) == (math.comb(n, k) if k >= 0 else 0)
    assert comb_exact(0, 0) == 1


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
