"""Knapsack — 0/1 (each item once) and unbounded (each item any number of times).

Signs:
  0/1: each item used at most once under a budget, subset sum, partition into
       two equal halves, "assign + or - to each number to hit target", two
       budgets at once (ones and zeroes).
  Unbounded: reusable items — coins, rod pieces — minimum coins, number of ways
       to make change, number of ordered sequences summing to a target.
Approach: dp[c] = best value (or reachable / count) using capacity c. Process
          one item at a time and let dp[c] also consider dp[c - w] + item.
          The only difference between the two flavours is loop direction:
            - 0/1: capacity *downward*, so dp[c - w] still holds the previous
              round's value, i.e. a table without this item.
            - unbounded: capacity *upward*, so dp[c - w] may already include
              this item, which is exactly "use it again".
          For counting unbounded: items outer counts combinations (each
          multiset once, in item order); capacity outer counts permutations
          (every ordering of the last item is tried at every capacity).
Complexity: O(n * C) time, O(C) space.
Gotchas:
  - Iterating the wrong direction silently turns one flavour into the other.
  - Swapping the loop order silently turns combinations into permutations.
  - +/- target: if P is the plus set, P - (total - P) = target, so
    P = (total + target) / 2. Parity or |target| > total means zero ways.
    Zeros double the count (+0 and -0 are different sign choices), which the
    downward loop handles because range(goal, -1, -1) includes c == 0.
  - Pseudo-polynomial: C is a *value*, so a capacity of 10^9 is hopeless even
    with 20 items — switch to meet-in-the-middle or knapsack over values.

Run the tests at the bottom with:  python3 dynamic_programming/knapsack.py
"""

import random
from itertools import combinations, product


# ---------------------------------------------------------------- implementation


def knapsack_01(weights, values, C):
    """Max value with total weight <= C, each item at most once."""
    dp = [0] * (C + 1)
    for w, v in zip(weights, values):
        for c in range(C, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[C]


def knapsack_01_2d(weights, values, C):
    """Full-table 0/1 knapsack, plus which items were chosen.

    Keeping every row costs O(n * C) space but lets you walk back: item i was
    taken exactly when row i + 1 differs from row i at the current capacity.
    """
    n = len(weights)
    dp = [[0] * (C + 1) for _ in range(n + 1)]
    for i in range(n):
        w, v = weights[i], values[i]
        for c in range(C + 1):
            dp[i + 1][c] = dp[i][c]
            if c >= w:
                dp[i + 1][c] = max(dp[i + 1][c], dp[i][c - w] + v)
    chosen, c = [], C
    for i in range(n - 1, -1, -1):
        if dp[i + 1][c] != dp[i][c]:
            chosen.append(i)
            c -= weights[i]
    return dp[n][C], chosen[::-1]


def knapsack_unbounded(weights, values, C):
    """Max value with total weight <= C, items reusable."""
    dp = [0] * (C + 1)
    for w, v in zip(weights, values):
        for c in range(w, C + 1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[C]


def can_partition_equal(a):
    """Can a be split into two groups of equal sum?"""
    total = sum(a)
    if total % 2:
        return False
    target = total // 2
    dp = [True] + [False] * target
    for x in a:
        for c in range(target, x - 1, -1):
            dp[c] = dp[c] or dp[c - x]
    return dp[target]


def subset_sum_bitset(a, target):
    """Subset-sum reachability using a Python int as the whole dp row.

    Bit c is set iff sum c is reachable. `bits << x` shifts every reachable
    sum up by x at once, so the inner loop becomes one big-int operation —
    typically 30-100x faster than the list version. The shift reads the old
    row in full before OR-ing, so it is 0/1 by construction.
    """
    bits = 1
    for x in a:
        bits |= bits << x
    return target >= 0 and bool(bits >> target & 1)


def count_target_signs(a, target):
    """Ways to put + or - before every element so the sum is target."""
    total = sum(a)
    if (total + target) % 2 or abs(target) > total:
        return 0
    goal = (total + target) // 2
    dp = [1] + [0] * goal
    for x in a:
        for c in range(goal, x - 1, -1):
            dp[c] += dp[c - x]
    return dp[goal]


def knapsack_2d_capacity(items, M, N):
    """Largest subset of (zeros, ones) items fitting both budgets M and N.

    Two capacities, both iterated downward — same rule, one more dimension.
    """
    dp = [[0] * (N + 1) for _ in range(M + 1)]
    for z, o in items:
        for i in range(M, z - 1, -1):
            for j in range(N, o - 1, -1):
                dp[i][j] = max(dp[i][j], dp[i - z][j - o] + 1)
    return dp[M][N]


def min_coins(coins, amount):
    """Fewest coins summing to amount, or -1."""
    INF = float("inf")
    dp = [0] + [INF] * amount
    for c in range(1, amount + 1):
        for coin in coins:
            if coin <= c and dp[c - coin] + 1 < dp[c]:
                dp[c] = dp[c - coin] + 1
    return dp[amount] if dp[amount] < INF else -1


def count_combinations(coins, amount):
    """Ways to make amount where order does not matter (coin change II)."""
    dp = [1] + [0] * amount
    for coin in coins:  # items outer
        for c in range(coin, amount + 1):
            dp[c] += dp[c - coin]
    return dp[amount]


def count_permutations(nums, target):
    """Ordered sequences of nums summing to target (combination sum IV)."""
    dp = [1] + [0] * target
    for c in range(1, target + 1):  # capacity outer
        for x in nums:
            if x <= c:
                dp[c] += dp[c - x]
    return dp[target]


# ------------------------------------------------------------------------ tests


def brute_01(weights, values, C):
    best = 0
    for k in range(len(weights) + 1):
        for idx in combinations(range(len(weights)), k):
            if sum(weights[i] for i in idx) <= C:
                best = max(best, sum(values[i] for i in idx))
    return best


def multisets(coins, amount):
    """Every multiplicity vector (k_0, k_1, ...) with sum k_i * coin_i == amount."""
    ranges = [range(amount // c + 1) for c in coins]
    return [ks for ks in product(*ranges) if sum(k * c for k, c in zip(ks, coins)) == amount]


def test_knapsack_01_classic():
    assert knapsack_01([1, 3, 4, 5], [1, 4, 5, 7], 7) == 9
    assert knapsack_01([], [], 10) == 0
    assert knapsack_01([5], [10], 4) == 0


def test_knapsack_01_matches_brute_force():
    random.seed(10)
    for _ in range(300):
        n = random.randint(0, 8)
        w = [random.randint(0, 8) for _ in range(n)]
        v = [random.randint(0, 20) for _ in range(n)]
        C = random.randint(0, 20)
        best = brute_01(w, v, C)
        assert knapsack_01(w, v, C) == best
        value, chosen = knapsack_01_2d(w, v, C)
        assert value == best
        assert len(set(chosen)) == len(chosen)
        assert sum(w[i] for i in chosen) <= C
        assert sum(v[i] for i in chosen) == best


def test_upward_loop_is_the_unbounded_trap():
    # One item of weight 2 worth 3. Capacity 6 fits it once in 0/1, but the
    # upward loop reads dp[c - 2] that already contains the item and takes it 3x.
    def wrong_01(weights, values, C):
        dp = [0] * (C + 1)
        for w, v in zip(weights, values):
            for c in range(w, C + 1):  # wrong direction
                dp[c] = max(dp[c], dp[c - w] + v)
        return dp[C]

    assert knapsack_01([2], [3], 6) == 3
    assert wrong_01([2], [3], 6) == 9
    assert wrong_01([2], [3], 6) == knapsack_unbounded([2], [3], 6)


def test_knapsack_unbounded_matches_brute_force():
    random.seed(11)
    for _ in range(200):
        n = random.randint(1, 4)
        w = [random.randint(1, 6) for _ in range(n)]
        v = [random.randint(0, 15) for _ in range(n)]
        C = random.randint(0, 15)
        best = max(
            sum(k * x for k, x in zip(ks, v))
            for ks in product(*[range(C // x + 1) for x in w])
            if sum(k * x for k, x in zip(ks, w)) <= C
        )
        assert knapsack_unbounded(w, v, C) == best


def test_partition_and_subset_sum():
    assert can_partition_equal([1, 5, 11, 5])
    assert not can_partition_equal([1, 2, 3, 5])
    assert can_partition_equal([])
    random.seed(12)
    for _ in range(300):
        a = [random.randint(0, 12) for _ in range(random.randint(0, 9))]
        sums = {sum(c) for k in range(len(a) + 1) for c in combinations(a, k)}
        assert can_partition_equal(a) == (sum(a) % 2 == 0 and sum(a) // 2 in sums)
        for t in range(-1, sum(a) + 2):
            assert subset_sum_bitset(a, t) == (t in sums)


def test_count_target_signs():
    assert count_target_signs([1, 1, 1, 1, 1], 3) == 5
    assert count_target_signs([1], 2) == 0
    assert count_target_signs([0, 0, 1], 1) == 4  # each zero can be +0 or -0
    random.seed(13)
    for _ in range(200):
        a = [random.randint(0, 5) for _ in range(random.randint(0, 8))]
        target = random.randint(-10, 10)
        brute = sum(
            1 for signs in product((1, -1), repeat=len(a))
            if sum(s * x for s, x in zip(signs, a)) == target
        )
        assert count_target_signs(a, target) == brute


def test_two_capacity_knapsack():
    strs = ["10", "0001", "111001", "1", "0"]
    items = [(s.count("0"), s.count("1")) for s in strs]
    assert knapsack_2d_capacity(items, 5, 3) == 4
    assert knapsack_2d_capacity(items, 1, 1) == 2
    random.seed(14)
    for _ in range(100):
        items = [(random.randint(0, 3), random.randint(0, 3)) for _ in range(random.randint(0, 7))]
        M, N = random.randint(0, 6), random.randint(0, 6)
        best = max(
            k
            for k in range(len(items) + 1)
            for c in combinations(items, k)
            if sum(z for z, _ in c) <= M and sum(o for _, o in c) <= N
        )
        assert knapsack_2d_capacity(items, M, N) == best


def test_coins_classic():
    assert min_coins([1, 2, 5], 11) == 3
    assert min_coins([2], 3) == -1
    assert min_coins([1], 0) == 0
    assert count_combinations([1, 2, 5], 5) == 4
    assert count_combinations([2], 3) == 0
    assert count_permutations([1, 2, 3], 4) == 7


def test_coins_match_brute_force():
    random.seed(15)
    for _ in range(200):
        coins = random.sample(range(1, 8), random.randint(1, 3))
        amount = random.randint(0, 15)
        ms = multisets(coins, amount)
        assert count_combinations(coins, amount) == len(ms)
        assert min_coins(coins, amount) == (min(sum(ks) for ks in ms) if ms else -1)
        perms = sum(
            1 for k in range(amount + 1)
            for seq in product(coins, repeat=k) if sum(seq) == amount
        ) if amount <= 8 else None
        if perms is not None:
            assert count_permutations(coins, amount) == perms


def test_loop_order_is_the_permutation_trap():
    # 1+2 and 2+1 are one combination but two permutations.
    assert count_combinations([1, 2], 3) == 2  # {1,1,1}, {1,2}
    assert count_permutations([1, 2], 3) == 3  # 111, 12, 21


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
