"""DP optimisation with a monotonic deque — max over a sliding window of dp.

Signs: dp[i] = a[i] + max(dp[j]) for j in a sliding range [i - k, i - 1]
       (jump game VI, constrained subsequence sum). The naive inner loop makes
       it O(n * k), which times out when both are 10^5.
Approach: keep a deque of indices whose dp values are strictly decreasing
          from front to back. The front is the window maximum. Before using
          it, drop indices that slid out of the window; after computing dp[i],
          pop every back index with dp <= dp[i] — they are older *and* no
          better, so they can never be the maximum again.
Complexity: O(n) — each index is pushed and popped at most once.
Gotchas:
  - Evict from the front by *index* (out of window), from the back by *value*.
  - Constrained subsequence sum may start fresh at i, so it takes
    max(0, window max): a negative prefix is never worth extending.
  - The same trick works for min (keep values increasing) and for any
    transition of the form dp[i] = f(i) + best(dp[j]) over a moving range.

Run the tests at the bottom with:  python3 dynamic_programming/deque_optimization.py
"""

import random
from collections import deque
from itertools import combinations


# ---------------------------------------------------------------- implementation


def max_score_jump_k(a, k):
    """Start on a[0], jump 1..k forward each move, end on a[-1]; max total."""
    dp = [0] * len(a)
    dp[0] = a[0]
    dq = deque([0])
    for i in range(1, len(a)):
        while dq[0] < i - k:
            dq.popleft()
        dp[i] = a[i] + dp[dq[0]]
        while dq and dp[dq[-1]] <= dp[i]:
            dq.pop()
        dq.append(i)
    return dp[-1]


def max_score_jump_k_naive(a, k):
    dp = [0] * len(a)
    dp[0] = a[0]
    for i in range(1, len(a)):
        dp[i] = a[i] + max(dp[max(0, i - k):i])
    return dp[-1]


def constrained_subsequence_sum(a, k):
    """Max sum of a non-empty subsequence whose consecutive indices differ by <= k."""
    dp = [0] * len(a)
    dq = deque()
    for i, x in enumerate(a):
        while dq and dq[0] < i - k:
            dq.popleft()
        dp[i] = x + max(0, dp[dq[0]] if dq else 0)
        while dq and dp[dq[-1]] <= dp[i]:
            dq.pop()
        dq.append(i)
    return max(dp)


# ------------------------------------------------------------------------ tests


def test_classic():
    assert max_score_jump_k([1, -1, -2, 4, -7, 3], 2) == 7
    assert max_score_jump_k([10, -5, -2, 4, 0, 3], 3) == 17
    assert max_score_jump_k([1, -5, -20, 4, -1, 3, -6, -3], 2) == 0
    assert max_score_jump_k([5], 3) == 5
    assert constrained_subsequence_sum([10, 2, -10, 5, 20], 2) == 37
    assert constrained_subsequence_sum([-1, -2, -3], 1) == -1
    assert constrained_subsequence_sum([10, -2, -10, -5, 20], 2) == 23


def test_jump_matches_naive_and_brute_force():
    random.seed(150)
    for _ in range(300):
        n, k = random.randint(1, 10), random.randint(1, 4)
        a = [random.randint(-10, 10) for _ in range(n)]
        # brute force: every set of landing spots that includes both ends
        paths = [(0,)] if n == 1 else [
            (0,) + mid + (n - 1,)
            for m in range(n - 1)
            for mid in combinations(range(1, n - 1), m)
        ]
        best = max(
            sum(a[i] for i in path)
            for path in paths
            if all(q - p <= k for p, q in zip(path, path[1:]))
        )
        assert max_score_jump_k(a, k) == max_score_jump_k_naive(a, k) == best


def test_constrained_sum_matches_brute_force():
    random.seed(151)
    for _ in range(300):
        n, k = random.randint(1, 10), random.randint(1, 4)
        a = [random.randint(-10, 10) for _ in range(n)]
        best = max(
            sum(a[i] for i in idx)
            for m in range(1, n + 1)
            for idx in combinations(range(n), m)
            if all(q - p <= k for p, q in zip(idx, idx[1:]))
        )
        assert constrained_subsequence_sum(a, k) == best


def test_large_window_is_linear():
    random.seed(152)
    n, k = 200_000, 100_000
    a = [random.randint(-10**4, 10**4) for _ in range(n)]
    # the naive version would scan ~1.5 * 10^10 window cells here
    assert max_score_jump_k(a, k) == a[0] + a[-1] + sum(x for x in a[1:-1] if x > 0)


def test_ties_keep_the_newer_index():
    # Popping on <= keeps the deque strictly decreasing, so a tie resolves to
    # the newer index, which stays in the window longer. The -100s force a
    # jump that only the last 5 can make.
    a = [0, 5, 5, 5, -100, -100, 1]
    assert max_score_jump_k(a, 3) == max_score_jump_k_naive(a, 3)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
