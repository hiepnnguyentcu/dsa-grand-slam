"""Fast exponentiation — scalars, modular powers, and matrix powers.

Signs: x ** n with a huge n, "modulo 10^9 + 7" powers, the n-th term of a
       linear recurrence (Fibonacci, tribonacci, tilings) for n ~ 10^18.
Approach: binary exponentiation. Write n in binary; x^n is the product of
          x^(2^i) over the set bits i. Square the base once per bit and fold it
          into the result only when that bit is set. The same loop works for
          anything with an associative multiply — including matrices, which is
          how a k-term recurrence becomes an O(k^3 log n) computation.
Complexity: O(log n) multiplications (O(k^3 log n) for k x k matrices).
Gotchas:
  - Negative exponent: invert the base first. With ints that makes the result
    a float, and 0 ** -1 is a ZeroDivisionError, not infinity.
  - Reduce modulo m after *every* multiply, or intermediate values grow to
    n bits and "O(log n)" becomes a lie.
  - n = 0 must give the identity (1, or the identity matrix), even for 0 ** 0.

Run the tests at the bottom with:  python3 math_algorithms/fast_power.py
"""


# ---------------------------------------------------------------- implementation


def fast_pow(x, n):
    """x ** n for integer n, in O(log |n|) multiplies."""
    if n < 0:
        x, n = 1 / x, -n
    res = 1
    while n:
        if n & 1:
            res *= x
        x *= x
        n >>= 1
    return res


def pow_mod(x, n, m):
    """x ** n % m for n >= 0. The hand-rolled twin of built-in pow(x, n, m)."""
    if m == 1:
        return 0  # everything is 0 mod 1, including x ** 0
    res, x = 1, x % m
    while n:
        if n & 1:
            res = res * x % m
        x = x * x % m
        n >>= 1
    return res


def mat_mult(A, B, mod=None):
    """Matrix product A * B, optionally reduced mod `mod`.

    The inner sum runs over A's columns (== B's rows). Writing range(len(B))
    there happens to be the same number, but only because the shapes agree —
    len(A[0]) says what it means.
    """
    cols, inner = len(B[0]), len(A[0])
    out = []
    for row in A:
        r = []
        for j in range(cols):
            s = sum(row[k] * B[k][j] for k in range(inner))
            r.append(s % mod if mod else s)
        out.append(r)
    return out


def identity(k):
    return [[int(i == j) for j in range(k)] for i in range(k)]


def mat_pow(M, n, mod=None):
    """M ** n for a square matrix, same loop as fast_pow."""
    res = identity(len(M))
    while n:
        if n & 1:
            res = mat_mult(res, M, mod)
        M = mat_mult(M, M, mod)
        n >>= 1
    return res


def fib_mod(n, mod=10**9 + 7):
    """F(n) mod `mod`, with F(0) = 0, F(1) = 1.

    [[1, 1], [1, 0]] ** n == [[F(n+1), F(n)], [F(n), F(n-1)]], so F(n) is the
    top-right entry.
    """
    return mat_pow([[1, 1], [1, 0]], n, mod)[0][1]


def linear_recurrence(coeffs, initial, n, mod=None):
    """n-th term (0-indexed) of a(i) = coeffs[0]*a(i-1) + ... + coeffs[k-1]*a(i-k).

    `initial` holds a(0)..a(k-1). The companion matrix shifts the window
    [a(i), a(i-1), ..., a(i-k+1)] forward one step; raise it to n-k+1 and apply
    it to the last known window.
    """
    k = len(coeffs)
    if n < k:
        return initial[n] % mod if mod else initial[n]
    T = [list(coeffs)] + [[int(j == i) for j in range(k)] for i in range(k - 1)]
    P = mat_pow(T, n - k + 1, mod)
    window = initial[::-1]  # a(k-1), ..., a(0)
    s = sum(P[0][j] * window[j] for j in range(k))
    return s % mod if mod else s


# ------------------------------------------------------------------------ tests


def test_fast_pow_matches_builtin():
    import random

    rng = random.Random(23)
    for _ in range(500):
        x, n = rng.randint(-50, 50), rng.randint(0, 200)
        assert fast_pow(x, n) == x**n
    assert fast_pow(0, 0) == 1
    assert fast_pow(7, 0) == 1
    assert fast_pow(-2, 63) == -(2**63)


def test_fast_pow_negative_exponent():
    assert fast_pow(2, -3) == 0.125
    assert abs(fast_pow(1.5, -7) - 1.5**-7) < 1e-12
    try:
        fast_pow(0, -1)
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError("0 ** -1 should raise")


def test_pow_mod_matches_builtin():
    import random

    rng = random.Random(1)
    for _ in range(2000):
        x = rng.randint(-(10**30), 10**30)
        n = rng.choice([0, 1, 2, rng.randint(0, 10**18), rng.getrandbits(200)])
        m = rng.choice([1, 2, 7, 10**9 + 7, rng.randint(1, 10**20)])
        assert pow_mod(x, n, m) == pow(x, n, m)


def test_pow_mod_mod_one_is_zero():
    assert pow_mod(5, 0, 1) == pow(5, 0, 1) == 0


def test_fermat_little_theorem():
    # a^(p-1) == 1 mod p for prime p and a not divisible by p
    p = 998_244_353
    for a in (2, 3, 12345, p - 1):
        assert pow_mod(a, p - 1, p) == 1


def test_mat_mult_non_square():
    A = [[1, 2, 3], [4, 5, 6]]  # 2 x 3
    B = [[7, 8], [9, 10], [11, 12]]  # 3 x 2
    assert mat_mult(A, B) == [[58, 64], [139, 154]]
    assert mat_mult(B, A) == [[39, 54, 69], [49, 68, 87], [59, 82, 105]]


def test_mat_pow_matches_repeated_multiplication():
    import random

    rng = random.Random(5)
    for _ in range(50):
        k = rng.randint(1, 4)
        M = [[rng.randint(-5, 5) for _ in range(k)] for _ in range(k)]
        n = rng.randint(0, 12)
        slow = identity(k)
        for _ in range(n):
            slow = mat_mult(slow, M)
        assert mat_pow(M, n) == slow
        assert mat_pow(M, n, 97) == [[v % 97 for v in row] for row in slow]


def test_fib_mod_against_iteration():
    a, b = 0, 1
    for n in range(300):
        assert fib_mod(n, None) == a  # mod=None: exact big ints
        assert fib_mod(n) == a % (10**9 + 7)
        a, b = b, a + b


def test_fib_huge_n_uses_pisano_period():
    # Fibonacci mod 10 repeats every 60 terms (the Pisano period).
    n = 10**18 + 7
    assert fib_mod(n, 10) == fib_mod(n % 60, 10)


def test_linear_recurrence():
    # Fibonacci as a recurrence
    for n in range(40):
        assert linear_recurrence([1, 1], [0, 1], n) == fib_mod(n, None)
    # tribonacci T(0)=0, T(1)=1, T(2)=1 against a direct loop
    t = [0, 1, 1]
    while len(t) < 60:
        t.append(t[-1] + t[-2] + t[-3])
    for n in range(60):
        assert linear_recurrence([1, 1, 1], [0, 1, 1], n) == t[n]
        assert linear_recurrence([1, 1, 1], [0, 1, 1], n, 1000) == t[n] % 1000
    # a(i) = 2a(i-1) - a(i-2) with a(0)=3, a(1)=5 is the line 3 + 2i
    for n in range(30):
        assert linear_recurrence([2, -1], [3, 5], n) == 3 + 2 * n


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
