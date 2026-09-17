"""Linear DP — take/skip (house robber), stair climbing, delete-and-earn.

Signs: a sequence where picking an element forbids its neighbours, stairs with
       1 or 2 steps, minimum cost to reach the end, "you cannot pick adjacent".
Approach: dp[i] depends on a constant number of earlier states, so keep only
          those as rolling variables. Take/skip is
              dp[i] = max(dp[i - 1], dp[i - 2] + a[i])
          — either a[i] is skipped (best so far stands) or taken (then a[i - 1]
          was not, so extend the best that ends two back).
Complexity: O(n) time, O(1) space.
Gotchas:
  - Circular arrays: the first and last elements are neighbours. Solve the line
    twice, once without the first and once without the last; one of the two
    must be the optimum since no answer can contain both.
  - Delete-and-earn looks different but is the same recurrence over *values*:
    bucket equal values together, then adjacent values are adjacent houses.
    A gap between values breaks the conflict, so the take can build on the
    best of both previous states.

Run the tests at the bottom with:  python3 dynamic_programming/linear_dp.py
"""

import random
from collections import Counter
from itertools import combinations, product


# ---------------------------------------------------------------- implementation


def rob_line(a):
    """Max sum of non-adjacent elements (the empty pick is allowed, so >= 0)."""
    prev2 = prev1 = 0  # best up to i - 2, best up to i - 1
    for x in a:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1


def rob_circle(a):
    """rob_line where a[0] and a[-1] are also neighbours."""
    if len(a) == 1:  # both slices below would be empty and lose the lone house
        return max(a[0], 0)
    return max(rob_line(a[1:]), rob_line(a[:-1]))


def climb_ways(n, steps=(1, 2)):
    """Ordered ways to climb n stairs taking any of `steps` at a time.

    dp[i] sums over the *last* step taken, so different orders count
    separately — this is the permutation-counting loop from knapsack.py with
    the capacity outermost.
    """
    dp = [1] + [0] * n
    for i in range(1, n + 1):
        dp[i] = sum(dp[i - s] for s in steps if i >= s)
    return dp[n]


def min_cost_climb(cost):
    """Min cost to get past the last stair, starting on stair 0 or 1.

    Paying cost[i] lets you step 1 or 2 further; "past the end" is index n.
    """
    a = b = 0  # cheapest arrival at i - 2, at i - 1
    for i in range(2, len(cost) + 1):
        a, b = b, min(b + cost[i - 1], a + cost[i - 2])
    return b


def delete_and_earn(nums):
    """Take value v to earn v (every copy of it), but all v-1 and v+1 vanish.

    take/skip = best total over the values seen so far, with / without the
    current value taken.
    """
    pts = Counter(nums)
    prev_v, take, skip = None, 0, 0
    for v in sorted(pts):
        gain = v * pts[v]
        best = max(take, skip)
        if prev_v is not None and v == prev_v + 1:
            take = skip + gain  # neighbour of prev: only the skip branch is safe
        else:
            take = best + gain  # gap: no conflict with anything before
        skip = best
        prev_v = v
    return max(take, skip)


# ------------------------------------------------------------------------ tests

def brute_rob(a, circular=False):
    n, best = len(a), 0
    for mask in range(1 << n):
        idx = [i for i in range(n) if mask >> i & 1]
        if any(j - i == 1 for i, j in zip(idx, idx[1:])):
            continue
        if circular and n > 1 and idx and idx[0] == 0 and idx[-1] == n - 1:
            continue
        best = max(best, sum(a[i] for i in idx))
    return best


def test_rob_classic():
    assert rob_line([1, 2, 3, 1]) == 4
    assert rob_line([2, 7, 9, 3, 1]) == 12
    assert rob_circle([2, 3, 2]) == 3
    assert rob_circle([1, 2, 3, 1]) == 4


def test_rob_matches_brute_force():
    random.seed(1)
    for _ in range(300):
        a = [random.randint(0, 20) for _ in range(random.randint(0, 10))]
        assert rob_line(a) == brute_rob(a)
        if a:
            assert rob_circle(a) == brute_rob(a, circular=True)


def test_rob_circle_single_and_pair():
    assert rob_circle([5]) == 5
    assert rob_circle([5, 9]) == 9  # the two houses are adjacent both ways


def test_rob_line_on_circle_is_the_trap():
    # Treating the circle as a line takes both ends, which touch.
    a = [5, 1, 1, 5]
    assert rob_line(a) == 10
    assert rob_circle(a) == 6


def test_climb_ways_is_fibonacci():
    fib = [1, 1]
    for _ in range(30):
        fib.append(fib[-1] + fib[-2])
    for n in range(31):
        assert climb_ways(n) == fib[n]


def test_climb_ways_counts_orders():
    for n in range(9):
        steps = (1, 3, 4)
        brute = sum(
            1
            for k in range(n + 1)
            for seq in product(steps, repeat=k)
            if sum(seq) == n
        )
        assert climb_ways(n, steps) == brute


def test_min_cost_climb():
    assert min_cost_climb([10, 15, 20]) == 15
    assert min_cost_climb([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]) == 6
    assert min_cost_climb([7, 3]) == 3  # leaving any stair costs, even the last


def test_min_cost_climb_matches_brute_force():
    def brute(cost, i):  # standing on i, cost to get past the end
        if i >= len(cost):
            return 0
        return cost[i] + min(brute(cost, i + 1), brute(cost, i + 2))

    random.seed(3)
    for _ in range(200):
        cost = [random.randint(0, 9) for _ in range(random.randint(2, 10))]
        assert min_cost_climb(cost) == min(brute(cost, 0), brute(cost, 1))


def test_delete_and_earn_classic():
    assert delete_and_earn([3, 4, 2]) == 6
    assert delete_and_earn([2, 2, 3, 3, 3, 4]) == 9
    assert delete_and_earn([]) == 0


def test_delete_and_earn_matches_brute_force():
    random.seed(2)
    for _ in range(300):
        nums = [random.randint(1, 8) for _ in range(random.randint(0, 9))]
        vals = sorted(set(nums))
        best = 0
        for k in range(len(vals) + 1):
            for chosen in combinations(vals, k):
                if all(b - a > 1 for a, b in zip(chosen, chosen[1:])):
                    best = max(best, sum(v * nums.count(v) for v in chosen))
        assert delete_and_earn(nums) == best


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
