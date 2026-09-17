"""Interval DP — burst balloons, cutting a stick, matrix chain, merging stones.

Signs: operate on a contiguous segment and split it; the answer for the whole
       array depends on answers for every sub-range; "order of operations"
       matters (burst, merge, cut, multiply).
Approach: dp[l][r] = best for the segment [l, r]. Iterate by increasing length
          so every shorter segment is ready, and try every split point k.
          "Last action" trick: instead of asking what happens *first* (which
          changes the neighbours of everything else), ask which element is
          processed *last*. Its left and right parts are then independent,
          because it still stands between them the whole time.
Complexity: O(n^3) time, O(n^2) space.
Gotchas:
  - Burst balloons "first burst" does not decompose: after popping k, k-1 and
    k+1 become neighbours and the halves interact. Choose the last one.
  - Pad with sentinels (1s for balloons, 0 and n for the stick) so the
    boundaries need no special case — then the answer is dp[0][last].
  - Iterating l from 0 upward with r fixed reads dp[k][r] before it exists;
    loop by length (or l downward).

Run the tests at the bottom with:  python3 dynamic_programming/interval_dp.py
"""

import random
from functools import cache
from itertools import permutations


INF = float("inf")


# ---------------------------------------------------------------- implementation


def burst_balloons(nums):
    """Max coins; bursting i pays left * nums[i] * right of its live neighbours."""
    a = [1] + nums + [1]
    n = len(a)
    dp = [[0] * n for _ in range(n)]  # dp[l][r]: open interval (l, r)
    for length in range(2, n):
        for l in range(n - length):
            r = l + length
            for k in range(l + 1, r):  # k is burst last inside (l, r)
                dp[l][r] = max(dp[l][r], dp[l][k] + dp[k][r] + a[l] * a[k] * a[r])
    return dp[0][n - 1]


def min_cut_cost(n, cuts):
    """Min total cost to make all cuts; each cut costs the current piece length."""
    c = [0] + sorted(cuts) + [n]
    m = len(c)
    dp = [[0] * m for _ in range(m)]
    for length in range(2, m):
        for l in range(m - length):
            r = l + length
            dp[l][r] = min(dp[l][k] + dp[k][r] for k in range(l + 1, r)) + c[r] - c[l]
    return dp[0][m - 1]


def matrix_chain(dims):
    """Fewest scalar multiplications for A1..An where Ai is dims[i-1] x dims[i]."""
    n = len(dims) - 1
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = min(
                dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                for k in range(i, j)
            )
    return dp[0][n - 1] if n else 0


def merge_stones(piles, K):
    """Min cost to merge all piles into one, merging K adjacent piles at a time.

    dp[i][j] = min cost to reduce piles[i..j] to as few piles as possible
    ((len - 1) % (K - 1) + 1 of them). Split so the left part collapses to one
    pile: that only happens at every (K - 1)-th position, hence the step. When
    the segment can become a single pile, pay its total once more.
    """
    n = len(piles)
    if (n - 1) % (K - 1):
        return -1
    pre = [0]
    for x in piles:
        pre.append(pre[-1] + x)
    dp = [[0] * n for _ in range(n)]
    for length in range(K, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = min(dp[i][m] + dp[m + 1][j] for m in range(i, j, K - 1))
            if (length - 1) % (K - 1) == 0:
                dp[i][j] += pre[j + 1] - pre[i]
    return dp[0][n - 1]


# ------------------------------------------------------------------------ tests


def brute_balloons(nums):
    best = 0
    for order in permutations(range(len(nums))):
        live, total = list(range(len(nums))), 0
        for i in order:
            p = live.index(i)
            left = nums[live[p - 1]] if p > 0 else 1
            right = nums[live[p + 1]] if p + 1 < len(live) else 1
            total += left * nums[i] * right
            live.pop(p)
        best = max(best, total)
    return best


def brute_cuts(n, cuts):
    best = INF
    for order in permutations(cuts):
        pieces, total = [(0, n)], 0
        for x in order:
            for idx, (a, b) in enumerate(pieces):
                if a < x < b:
                    total += b - a
                    pieces[idx:idx + 1] = [(a, x), (x, b)]
                    break
        best = min(best, total)
    return best


@cache
def brute_matrix(dims):
    """Recursion on every top-level split — the definition, unoptimised."""
    if len(dims) <= 2:
        return 0
    return min(brute_matrix(dims[:k + 1]) + brute_matrix(dims[k:]) + dims[0] * dims[k] * dims[-1]
               for k in range(1, len(dims) - 1))


def brute_merge(piles, K):
    """Try every merge sequence."""
    @cache
    def go(state):
        if len(state) == 1:
            return 0
        best = INF
        for i in range(len(state) - K + 1):
            s = sum(state[i:i + K])
            best = min(best, s + go(state[:i] + (s,) + state[i + K:]))
        return best

    res = go(tuple(piles))
    return -1 if res == INF else res


def test_classic():
    assert burst_balloons([3, 1, 5, 8]) == 167
    assert burst_balloons([1, 5]) == 10
    assert burst_balloons([]) == 0
    assert min_cut_cost(7, [1, 3, 4, 5]) == 16
    assert min_cut_cost(9, [5, 6, 1, 4, 2]) == 22
    assert min_cut_cost(5, []) == 0
    assert matrix_chain([10, 30, 5, 60]) == 4500
    assert matrix_chain([5]) == 0
    assert merge_stones([3, 2, 4, 1], 2) == 20
    assert merge_stones([3, 2, 4, 1], 3) == -1
    assert merge_stones([3, 5, 1, 2, 6], 3) == 25


def test_balloons_match_brute_force():
    random.seed(80)
    for _ in range(150):
        nums = [random.randint(0, 9) for _ in range(random.randint(0, 6))]
        assert burst_balloons(nums) == brute_balloons(nums)


def test_first_burst_split_is_the_trap():
    # "Burst k first, then solve each side on its own" charges k its current
    # neighbours, but then each side still pays as if k were next to it. The
    # sides are not independent, and the result is wrong in both directions.
    def wrong(nums):
        a = [1] + nums + [1]

        @cache
        def f(l, r):
            if l > r:
                return 0
            return max(a[k - 1] * a[k] * a[k + 1] + f(l, k - 1) + f(k + 1, r)
                       for k in range(l, r + 1))

        return f(1, len(nums))

    assert wrong([3, 1, 5, 8]) == 98 < burst_balloons([3, 1, 5, 8]) == 167
    assert wrong([2, 2]) == 8 > burst_balloons([2, 2]) == brute_balloons([2, 2]) == 6


def test_cuts_match_brute_force():
    random.seed(81)
    for _ in range(150):
        n = random.randint(2, 20)
        cuts = random.sample(range(1, n), random.randint(0, min(5, n - 1)))
        assert min_cut_cost(n, cuts) == brute_cuts(n, cuts)


def test_matrix_chain_matches_brute_force():
    random.seed(82)
    for _ in range(150):
        dims = tuple(random.randint(1, 20) for _ in range(random.randint(2, 8)))
        assert matrix_chain(list(dims)) == brute_matrix(dims)


def test_merge_stones_matches_brute_force():
    random.seed(83)
    for _ in range(200):
        piles = [random.randint(1, 9) for _ in range(random.randint(1, 7))]
        K = random.randint(2, 4)
        assert merge_stones(piles, K) == brute_merge(piles, K), (piles, K)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
