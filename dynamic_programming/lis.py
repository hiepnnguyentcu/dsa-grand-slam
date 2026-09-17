"""Longest increasing subsequence — O(n^2), O(n log n), counting, 2D chains.

Signs: longest chain in increasing order, nested envelopes / boxes / dolls,
       minimum deletions to make an array sorted (n - LIS), patience sorting,
       longest arithmetic subsequence.
Approach:
  - O(n^2): dp[i] = 1 + max(dp[j]) over j < i with a[j] < a[i]. Slow but it
    carries extra info easily (counts, predecessors, differences).
  - O(n log n): tails[k] = the smallest tail of any increasing subsequence of
    length k + 1. tails is sorted, so each x binary-searches for the first tail
    >= x and replaces it (a smaller tail can only help later) or appends.
  - 2D chains: sort by width ascending, height *descending*, then LIS on height.
    The descending tie-break stops two envelopes of equal width from chaining.
Complexity: O(n log n) time, O(n) space for the patience version.
Gotchas:
  - tails is not an actual subsequence — it mixes elements from different
    chains. Keep parent pointers (lis_sequence) to recover a real one.
  - bisect_left gives strictly increasing; bisect_right gives non-decreasing.
  - Counting needs the O(n^2) table; tails forgets how many ways it got there.

Run the tests at the bottom with:  python3 dynamic_programming/lis.py
"""

import random
from bisect import bisect_left, bisect_right
from itertools import combinations


# ---------------------------------------------------------------- implementation


def lis_quadratic(a):
    dp = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp, default=0)


def lis_length(a, strict=True):
    """Patience sorting. strict=False allows equal neighbours."""
    find = bisect_left if strict else bisect_right
    tails = []
    for x in a:
        i = find(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def lis_sequence(a):
    """One actual longest strictly increasing subsequence, in O(n log n).

    Store indices in tails instead of values, and for every element remember
    the index that sat one slot to its left when it was placed — that is the
    element it extends. Walking those links back from the last tail yields a
    valid chain even though tails itself is not one.
    """
    tails, parent = [], [-1] * len(a)  # tails holds indices into a
    for i, x in enumerate(a):
        k = bisect_left(tails, x, key=lambda t: a[t])  # key= needs Python 3.10+
        if k:
            parent[i] = tails[k - 1]
        if k == len(tails):
            tails.append(i)
        else:
            tails[k] = i
    out, i = [], tails[-1] if tails else -1
    while i != -1:
        out.append(a[i])
        i = parent[i]
    return out[::-1]


def max_nested_envelopes(env):
    """Longest chain of (w, h) with both strictly increasing."""
    env = sorted(env, key=lambda e: (e[0], -e[1]))  # don't mutate the caller's list
    return lis_length([h for _, h in env])


def count_lis(a):
    """Number of longest strictly increasing subsequences (by index set).

    [] has exactly one longest subsequence, the empty one, so it returns 1.
    """
    n = len(a)
    if not n:
        return 1
    length, count = [1] * n, [1] * n
    for i in range(n):
        for j in range(i):
            if a[j] < a[i]:
                if length[j] + 1 > length[i]:
                    length[i], count[i] = length[j] + 1, count[j]
                elif length[j] + 1 == length[i]:
                    count[i] += count[j]
    L = max(length)
    return sum(c for l, c in zip(length, count) if l == L)


def longest_arith_subseq(a):
    """Longest subsequence with a constant difference between neighbours.

    dp[i][d] = length of the longest such subsequence ending at i with step d.
    A pair (j, i) is itself length 2, hence the default of 1 before adding 1.
    """
    if not a:
        return 0
    dp = [{} for _ in a]
    best = 1
    for i in range(len(a)):
        for j in range(i):
            d = a[i] - a[j]
            dp[i][d] = dp[j].get(d, 1) + 1
            best = max(best, dp[i][d])
    return best


# ------------------------------------------------------------------------ tests


def all_subseqs(a):
    for k in range(len(a) + 1):
        yield from combinations(a, k)


def increasing(s, strict=True):
    return all(x < y if strict else x <= y for x, y in zip(s, s[1:]))


def test_classic():
    a = [10, 9, 2, 5, 3, 7, 101, 18]
    assert lis_length(a) == lis_quadratic(a) == 4
    assert lis_length([7, 7, 7]) == 1
    assert lis_length([7, 7, 7], strict=False) == 3
    assert lis_length([]) == lis_quadratic([]) == 0
    assert count_lis([1, 3, 5, 4, 7]) == 2
    assert count_lis([2, 2, 2, 2, 2]) == 5
    assert count_lis([]) == 1
    assert longest_arith_subseq([9, 4, 7, 2, 10]) == 3
    assert longest_arith_subseq([20, 1, 15, 3, 10, 5, 8]) == 4


def test_matches_brute_force():
    random.seed(20)
    for _ in range(300):
        a = [random.randint(0, 6) for _ in range(random.randint(0, 10))]
        subs = list(all_subseqs(a))
        strict = max(len(s) for s in subs if increasing(s))
        loose = max(len(s) for s in subs if increasing(s, strict=False))
        assert lis_quadratic(a) == lis_length(a) == strict
        assert lis_length(a, strict=False) == loose

        seq = lis_sequence(a)
        assert len(seq) == strict and increasing(seq)
        it = iter(a)
        assert all(x in it for x in seq)  # really a subsequence of a

        # count by index sets, which is what combinations over indices gives
        idx_sets = [
            c for k in range(len(a) + 1) for c in combinations(range(len(a)), k)
            if len(c) == strict and increasing([a[i] for i in c])
        ]
        assert count_lis(a) == len(idx_sets)

        arith = max(
            (len(s) for s in subs if len({y - x for x, y in zip(s, s[1:])}) <= 1),
            default=0,
        )
        assert longest_arith_subseq(a) == arith


def test_tails_is_not_a_subsequence():
    # The trap: tails has the right *length* but holds values that never
    # appeared together in that order.
    a = [3, 4, 5, 1]
    tails = []
    for x in a:
        i = bisect_left(tails, x)
        tails[i:i + 1] = [x]
    assert tails == [1, 4, 5]  # 1 comes *after* 4 and 5 in a
    assert lis_sequence(a) == [3, 4, 5]


def test_envelopes():
    env = [[5, 4], [6, 4], [6, 7], [2, 3]]
    before = [e[:] for e in env]
    assert max_nested_envelopes(env) == 3
    assert env == before  # input left alone
    assert max_nested_envelopes([[1, 1], [1, 1], [1, 1]]) == 1


def test_envelope_tie_break_is_the_trap():
    # Sorting heights ascending within equal width lets [1,1] -> [1,2] chain.
    env = [(1, 1), (1, 2), (1, 3)]
    wrong = lis_length([h for _, h in sorted(env)])
    assert wrong == 3
    assert max_nested_envelopes(env) == 1


def test_envelopes_match_brute_force():
    random.seed(21)
    for _ in range(200):
        env = [(random.randint(1, 5), random.randint(1, 5)) for _ in range(random.randint(0, 8))]
        best = 0
        for k in range(len(env) + 1):
            for c in combinations(sorted(env), k):
                if all(p[0] < q[0] and p[1] < q[1] for p, q in zip(c, c[1:])):
                    best = max(best, k)
        assert max_nested_envelopes(env) == best


def test_big_input_is_fast():
    random.seed(22)
    a = [random.randrange(10**9) for _ in range(100_000)]
    n = lis_length(a)
    assert 500 < n < 1000  # ~2*sqrt(n) for a random permutation
    assert len(lis_sequence(a)) == n


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
