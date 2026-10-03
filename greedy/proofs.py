"""Proving greedy — exchange argument, stays ahead, and when greedy fails.

Signs: "minimise total waiting / completion time", "fewest coins", "best value
       under a weight limit", any problem where one local rule (smallest first,
       best ratio first, largest first) looks obviously right.
Approach: a greedy is only correct with a proof. Two templates cover nearly
          every interview greedy:
  - Exchange argument: take any optimal solution that differs from greedy.
    Find the first place they differ and swap the optimal's choice for the
    greedy one. Show the swap never makes it worse. Repeat until optimal ==
    greedy. (Shortest job first: swapping an adjacent long-before-short pair
    lowers the total.)
  - Greedy stays ahead: after every step, greedy's partial answer is at least
    as good as any other algorithm's after the same number of steps. (Jump
    game II: after k jumps greedy's reach is the furthest reachable.)
  If you cannot sketch either in a minute, find a counterexample by brute force
  on tiny inputs and switch to DP (dynamic_programming/knapsack.py).
Complexity: shortest-job-first and fractional knapsack O(n log n); greedy coins
            O(len(coins) + count); canonical check O(len(coins) * bound).
Gotchas:
  - Coin change: largest-coin-first is right for "canonical" systems (US coins)
    and wrong in general: coins [1, 3, 4], amount 6 -> greedy 4+1+1, best 3+3.
  - Fractional knapsack is greedy by value/weight; 0/1 knapsack is not —
    one big item can beat two high-ratio items that leave capacity unused.
  - Sort keys decide everything. Ties need an argument too.
  - Testing against brute force on random small inputs is how you check a
    greedy you cannot prove — the tests below do exactly that.

Run the tests at the bottom with:  python3 greedy/proofs.py
"""

import random
from fractions import Fraction
from itertools import combinations, permutations


# ---------------------------------------------------------------- implementation


def min_total_completion(durations):
    """Order jobs to minimise the sum of completion times; return that sum.

    Exchange argument: if a longer job a runs right before a shorter job b,
    swapping them leaves everyone else's finish time unchanged, and the pair's
    total drops by len(a) - len(b) > 0. So no optimal order has such a pair:
    the optimum is sorted ascending (shortest processing time first).
    """
    t = total = 0
    for d in sorted(durations):
        t += d
        total += t
    return total


def fractional_knapsack(items, C):
    """Max value with total weight <= C; any fraction of an item may be taken.

    items: [(weight, value)], weights > 0. Returns an exact Fraction.
    Exchange argument: if an optimal solution holds some weight of a lower-ratio
    item while a higher-ratio item is not fully taken, swapping equal weight
    between them never lowers the value.
    """
    total, room = Fraction(0), C
    for w, v in sorted(items, key=lambda it: Fraction(it[1], it[0]), reverse=True):
        take = min(w, room)
        total += Fraction(v, w) * take
        room -= take
        if room == 0:
            break
    return total


def greedy_by_ratio_01(items, C):
    """The *wrong* greedy for 0/1 knapsack: whole items, best ratio first."""
    total, room = 0, C
    for w, v in sorted(items, key=lambda it: Fraction(it[1], it[0]), reverse=True):
        if w <= room:
            total += v
            room -= w
    return total


def greedy_coins(coins, amount):
    """Fewest coins by always taking the largest that fits, or -1 if stuck.

    Correct only for canonical coin systems — see is_canonical.
    """
    count = 0
    for c in sorted(coins, reverse=True):
        count += amount // c
        amount %= c
    return count if amount == 0 else -1


def dp_coins(coins, amount):
    """Fewest coins, always correct: unbounded knapsack (see dynamic_programming/)."""
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] < INF else -1


def is_canonical(coins):
    """Does largest-first give the optimum for every amount?

    Kozen & Zaks: if greedy is ever wrong, the smallest counterexample is below
    the sum of the two largest coins. So checking amounts up to that bound is
    enough. Assumes 1 is a coin (otherwise some amounts are unreachable).
    """
    cs = sorted(coins)
    if len(cs) < 3:
        return True  # {1} and {1, c} are always canonical
    bound = cs[-1] + cs[-2]
    return all(greedy_coins(cs, a) == dp_coins(cs, a) for a in range(bound))


# ------------------------------------------------------------------------ tests


def brute_completion(durations):
    best = float("inf")
    for order in permutations(durations):
        t = total = 0
        for d in order:
            t += d
            total += t
        best = min(best, total)
    return best


def brute_01(items, C):
    best = 0
    for k in range(len(items) + 1):
        for chosen in combinations(items, k):
            if sum(w for w, _ in chosen) <= C:
                best = max(best, sum(v for _, v in chosen))
    return best


def brute_fractional_integer(items, C):
    """Exact fractional optimum when weights and C are integers.

    Split each item into w unit pieces worth v/w; an integral C is then filled
    by whole pieces, and 0/1 knapsack over unit pieces is exact.
    """
    dp = [Fraction(0)] * (C + 1)
    for w, v in items:
        piece = Fraction(v, w)
        for _ in range(w):
            for c in range(C, 0, -1):
                dp[c] = max(dp[c], dp[c - 1] + piece)
    return dp[C]


def test_shortest_job_first_matches_brute_force():
    random.seed(1)
    for _ in range(200):
        d = [random.randint(1, 9) for _ in range(random.randint(0, 6))]
        assert min_total_completion(d) == brute_completion(d)


def test_shortest_job_first_example():
    assert min_total_completion([3, 1, 2]) == 1 + 3 + 6


def test_fractional_knapsack_matches_unit_dp():
    random.seed(2)
    for _ in range(150):
        items = [(random.randint(1, 5), random.randint(1, 20)) for _ in range(random.randint(1, 5))]
        C = random.randint(0, 15)
        assert fractional_knapsack(items, C) == brute_fractional_integer(items, C)


def test_fractional_knapsack_classic():
    assert fractional_knapsack([(10, 60), (20, 100), (30, 120)], 50) == 240


def test_ratio_greedy_fails_on_01_knapsack():
    items = [(10, 60), (20, 100), (30, 120)]
    assert greedy_by_ratio_01(items, 50) == 160  # takes ratios 6 and 5
    assert brute_01(items, 50) == 220            # 100 + 120 is better


def test_greedy_coins_correct_on_canonical_system():
    us = [1, 5, 10, 25]
    assert is_canonical(us)
    for amount in range(200):
        assert greedy_coins(us, amount) == dp_coins(us, amount)


def test_greedy_coins_counterexample():
    assert greedy_coins([1, 3, 4], 6) == 3  # 4 + 1 + 1
    assert dp_coins([1, 3, 4], 6) == 2      # 3 + 3
    assert not is_canonical([1, 3, 4])


def test_greedy_coins_can_get_stuck_without_a_1():
    assert greedy_coins([5, 2], 6) == -1  # 5, then 1 left
    assert dp_coins([5, 2], 6) == 3       # 2 + 2 + 2


def test_canonical_bound_agrees_with_exhaustive_check():
    random.seed(3)
    for _ in range(200):
        coins = [1] + random.sample(range(2, 20), random.randint(1, 4))
        exhaustive = all(greedy_coins(coins, a) == dp_coins(coins, a) for a in range(120))
        assert is_canonical(coins) == exhaustive


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
