"""Masks as sets — enumerate subsets, submasks, k-subsets (Gosper), letter masks, Gray code.

Signs: n <= 20 items and "every subset", "every subset of this subset",
       "all subsets of size k", strings compared only by which letters they
       contain, "sequence where neighbours differ by one bit".
Approach: bit i of a mask means item i is in the set.
  - union a | b, intersection a & b, difference a & ~b, complement within n
    bits FULL ^ a, membership a >> i & 1, size a.bit_count().
  - All subsets: for mask in range(1 << n).
  - All submasks of m, largest first: s = m; s = (s - 1) & m; stop after 0.
    (s - 1) clears the lowest set bit and refills the bits below it; & m
    keeps only m's bits. Over every m this totals 3^n steps, not 4^n.
  - Next mask with the same popcount (Gosper's hack):
        c = x & -x;  r = x + c;  next = (((r ^ x) >> 2) // c) | r
  - Letter mask: 26 bits, one per letter. "No common letters" is a & b == 0.
  - Gray code: g(i) = i ^ (i >> 1). Inverse: XOR all right shifts.
  - DP over subsets (TSP, assignment): dynamic_programming/bitmask_dp.py.
    Subsets by recursion vs mask: backtracking/subsets.py.
Complexity: subsets O(2^n); submasks of one m O(2^popcount(m)), all m O(3^n);
            Gosper O(1) per step; letter masks O(total letters + w^2).
Gotchas:
  - The submask loop must handle s == 0 explicitly (process it, then break),
    or it either skips the empty set or loops forever: (0 - 1) & m == m.
  - ~mask is negative in Python; complement within n bits is FULL ^ mask.
  - Gosper needs x > 0. Stop when next >= 1 << n.
  - Letter masks lose multiplicity: "aab" and "ab" share a mask.

Run the tests at the bottom with:  python3 bit_manipulation/bitmask_sets.py
"""

import random
from itertools import combinations


# ---------------------------------------------------------------- implementation


def all_subsets(items):
    """Every subset of items, in mask order."""
    n = len(items)
    return [[items[i] for i in range(n) if mask >> i & 1] for mask in range(1 << n)]


def submasks(m):
    """All submasks of m, from m down to 0 inclusive."""
    out = []
    s = m
    while True:
        out.append(s)
        if s == 0:
            break
        s = (s - 1) & m
    return out


def gosper_next(x):
    """Next larger integer with the same number of set bits (x > 0)."""
    c = x & -x
    r = x + c
    return (((r ^ x) >> 2) // c) | r


def k_subsets(n, k):
    """All k-bit masks below 1 << n in increasing order, via Gosper's hack."""
    if k == 0:
        return [0]
    out = []
    x = (1 << k) - 1
    while x < 1 << n:
        out.append(x)
        x = gosper_next(x)
    return out


def letter_mask(word):
    mask = 0
    for ch in word:
        mask |= 1 << (ord(ch) - ord("a"))
    return mask


def max_product(words):
    """Max len(a) * len(b) over word pairs sharing no letter (LeetCode 318).

    Keep only the longest word per mask: equal masks are interchangeable.
    """
    best_len = {}
    for w in words:
        m = letter_mask(w)
        best_len[m] = max(best_len.get(m, 0), len(w))
    items = list(best_len.items())
    best = 0
    for i, (ma, la) in enumerate(items):
        for mb, lb in items[i + 1:]:
            if ma & mb == 0:
                best = max(best, la * lb)
    return best


def gray_code(n):
    """n-bit Gray code sequence starting at 0 (LeetCode 89)."""
    return [i ^ (i >> 1) for i in range(1 << n)]


def gray_to_binary(g):
    """Inverse of i ^ (i >> 1): XOR together every right shift of g."""
    i = 0
    while g:
        i ^= g
        g >>= 1
    return i


# ------------------------------------------------------------------------ tests


def test_all_subsets_against_combinations():
    items = list("abcde")
    got = sorted(map(tuple, all_subsets(items)))
    want = sorted(c for k in range(6) for c in combinations(items, k))
    assert got == want


def test_set_ops_against_python_sets():
    rng = random.Random(40)
    n, full = 12, (1 << 12) - 1
    for _ in range(1000):
        a, b = rng.randrange(1 << n), rng.randrange(1 << n)
        sa = {i for i in range(n) if a >> i & 1}
        sb = {i for i in range(n) if b >> i & 1}
        to_set = lambda m: {i for i in range(n) if m >> i & 1}
        assert to_set(a | b) == sa | sb
        assert to_set(a & b) == sa & sb
        assert to_set(a & ~b) == sa - sb
        assert to_set(full ^ a) == set(range(n)) - sa
        assert a.bit_count() == len(sa)


def test_submasks_against_filter():
    for m in range(1 << 10):
        got = submasks(m)
        want = sorted((s for s in range(m + 1) if s & m == s), reverse=True)
        assert got == want
    assert submasks(0) == [0]


def test_submask_total_is_three_to_the_n():
    for n in range(1, 11):
        assert sum(len(submasks(m)) for m in range(1 << n)) == 3**n


def test_k_subsets_against_combinations():
    for n in range(0, 13):
        for k in range(0, n + 1):
            want = sorted(sum(1 << i for i in c) for c in combinations(range(n), k))
            assert k_subsets(n, k) == want


def test_gosper_against_scan():
    for x in range(1, 5000):
        y = x + 1
        while y.bit_count() != x.bit_count():
            y += 1
        assert gosper_next(x) == y


def test_max_product_against_brute_force():
    rng = random.Random(41)
    for _ in range(300):
        words = ["".join(rng.choice("abcdefgh") for _ in range(rng.randint(1, 6)))
                 for _ in range(rng.randint(0, 12))]
        brute = max((len(a) * len(b) for a, b in combinations(words, 2)
                     if not set(a) & set(b)), default=0)
        assert max_product(words) == brute
    assert max_product(["abcw", "baz", "foo", "bar", "xtfn", "abcdef"]) == 16


def test_gray_code_properties():
    for n in range(0, 11):
        g = gray_code(n)
        assert sorted(g) == list(range(1 << n))  # a permutation
        for a, b in zip(g, g[1:] + g[:1]):  # cyclic: last wraps to first
            if n:
                assert (a ^ b).bit_count() == 1
        assert [gray_to_binary(x) for x in g] == list(range(1 << n))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
