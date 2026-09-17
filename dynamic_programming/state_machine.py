"""State machine DP — stock trading variants, paint house.

Signs: a small, fixed set of modes that change over time — holding / not
       holding a stock, cooling down, transactions left, colour of the
       previous house.
Approach: draw the state diagram first. Keep one variable per state and, at
          each step, compute every new state from the *old* states at once
          (tuple assignment or temporaries). Each edge of the diagram is one
          term in a max/min.
Complexity: O(n * states) time, O(states) space.
Gotchas:
  - Sequential assignment (hold = ...; sold = hold + p) reads the *new* hold
    and lets you buy and sell on the same day through the cooldown. Use one
    tuple assignment.
  - Start "holding" at -inf, not 0: you cannot hold a stock you never bought.
  - k transactions with k >= n // 2 is unlimited trading — short-circuit, or
    the O(n * k) loop is wasted work.
  - Paint house with k colours: min over "every other colour" is O(k^2) per
    house; track the best and second best instead for O(k). One colour and
    more than one house is impossible.

Run the tests at the bottom with:  python3 dynamic_programming/state_machine.py
"""

import random
from functools import cache
from itertools import product


NEG = float("-inf")
INF = float("inf")


# ---------------------------------------------------------------- implementation


def stock_unlimited(prices):
    """Any number of transactions: sum every upward step."""
    return sum(max(0, b - a) for a, b in zip(prices, prices[1:]))


def stock_cooldown(prices):
    """Unlimited trades, but after selling you must skip a day.

        rest --buy--> hold --sell--> sold --(wait)--> rest
    """
    hold, sold, rest = NEG, 0, 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return max(sold, rest)


def stock_fee(prices, fee):
    """Unlimited trades, each sale pays `fee`."""
    hold, cash = NEG, 0
    for p in prices:
        hold, cash = max(hold, cash - p), max(cash, hold + p - fee)
    return cash


def stock_k_transactions(prices, k):
    """At most k buy-sell pairs, never holding more than one share.

    buy[t] / sell[t] = best cash after the t-th buy / sell. Updating in place
    within a day only allows buying and selling on the same day, which gains
    nothing and so cannot corrupt the answer.
    """
    if k >= len(prices) // 2:
        return stock_unlimited(prices)
    buy = [NEG] * (k + 1)
    sell = [0] * (k + 1)
    for p in prices:
        for t in range(1, k + 1):
            buy[t] = max(buy[t], sell[t - 1] - p)
            sell[t] = max(sell[t], buy[t] + p)
    return sell[k]


def paint_min_cost(costs):
    """Min cost to paint houses so neighbours differ; costs[house][colour]."""
    if not costs:
        return 0
    prev = list(costs[0])  # the first house has no neighbour to clash with
    for row in costs[1:]:
        # the best other colour is the best one unless that is c itself
        order = sorted(range(len(prev)), key=prev.__getitem__)
        b1 = order[0]
        second = prev[order[1]] if len(order) > 1 else INF
        prev = [row[c] + (second if c == b1 else prev[b1]) for c in range(len(row))]
    best = min(prev)
    return best if best < INF else -1


# ------------------------------------------------------------------------ tests


def brute_stock(prices, k=None, cooldown=False, fee=0):
    """Try every day's action: buy, sell, or nothing."""
    n = len(prices)

    @cache
    def go(i, holding, left, blocked):
        if i == n:
            return 0
        best = go(i + 1, holding, left, False)  # do nothing
        if holding:
            best = max(best, prices[i] - fee + go(i + 1, False, left, cooldown))
        elif not blocked and (left is None or left > 0):
            best = max(best, -prices[i] + go(i + 1, True, None if left is None else left - 1, False))
        return best

    return go(0, False, k, False)


def test_classic():
    assert stock_cooldown([1, 2, 3, 0, 2]) == 3
    assert stock_cooldown([1]) == 0
    assert stock_fee([1, 3, 2, 8, 4, 9], 2) == 8
    assert stock_fee([1, 3, 7, 5, 10, 3], 3) == 6
    assert stock_k_transactions([2, 4, 1], 2) == 2
    assert stock_k_transactions([3, 2, 6, 5, 0, 3], 2) == 7
    assert stock_k_transactions([3, 3, 5, 0, 0, 3, 1, 4], 2) == 6
    assert stock_k_transactions([1, 2], 0) == 0
    assert paint_min_cost([[17, 2, 17], [16, 16, 5], [14, 3, 19]]) == 10
    assert paint_min_cost([[1, 5, 3], [2, 9, 4]]) == 5
    assert paint_min_cost([]) == 0


def test_stocks_match_brute_force():
    random.seed(100)
    for _ in range(300):
        prices = [random.randint(0, 10) for _ in range(random.randint(0, 9))]
        k = random.randint(0, 4)
        fee = random.randint(0, 3)
        assert stock_unlimited(prices) == brute_stock(prices)
        assert stock_cooldown(prices) == brute_stock(prices, cooldown=True)
        assert stock_fee(prices, fee) == brute_stock(prices, fee=fee)
        assert stock_k_transactions(prices, k) == brute_stock(prices, k=k)


def test_sequential_update_is_the_trap():
    # Updating one variable at a time reads today's hold when computing sold,
    # which lets you buy and sell on the same day and skip the cooldown.
    def wrong(prices):
        hold, sold, rest = NEG, 0, 0
        for p in prices:
            hold = max(hold, rest - p)
            sold = hold + p
            rest = max(rest, sold)
        return max(sold, rest)

    prices = [1, 4, 2, 5]
    assert stock_cooldown(prices) == brute_stock(prices, cooldown=True) == 4
    assert wrong(prices) != stock_cooldown(prices)


def test_paint_matches_brute_force():
    random.seed(101)
    for _ in range(300):
        n, k = random.randint(1, 5), random.randint(1, 4)
        costs = [[random.randint(0, 20) for _ in range(k)] for _ in range(n)]
        valid = [
            sum(costs[i][c] for i, c in enumerate(cols))
            for cols in product(range(k), repeat=n)
            if all(a != b for a, b in zip(cols, cols[1:]))
        ]
        assert paint_min_cost(costs) == (min(valid) if valid else -1)


def test_one_colour():
    assert paint_min_cost([[4]]) == 4
    assert paint_min_cost([[4], [5]]) == -1  # two neighbours, one colour


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
