"""Running balance — one pass over a running sum, reset when it goes bad.

Signs: a circular route with gains and costs, "minimum starting value so the
       running sum never drops below 1", unlimited buy/sell of a stock.
Approach: keep a running balance and react the moment it fails.
  - Gas station: if the tank goes negative at i, no start in [start, i] works
    (each of them arrives at i with no more fuel than `start` did), so restart
    at i + 1. If the total gas >= total cost, the last restart is the answer.
  - Minimum start value: the answer is 1 - (lowest prefix sum), floored at 1.
  - Stock II (unlimited trades): every rising day-to-day step is profit you can
    take; sum the positive differences.
Complexity: O(n) time, O(1) space.
Gotchas:
  - Gas station: check total >= 0 *separately* — the restart index alone does
    not prove the loop closes.
  - Stock II is a special case of the state-machine DP
    (dynamic_programming/state_machine.py); cooldowns or fees break the greedy.
  - Stock II never needs to hold across a dip: buy-low-sell-high over a span
    equals the sum of its rising steps.

Run the tests at the bottom with:  python3 greedy/running_balance.py
"""

import random
from functools import cache


# ---------------------------------------------------------------- implementation


def can_complete_circuit(gas, cost):
    """Start index to drive the full circle once, or -1."""
    total = tank = start = 0
    for i, (g, c) in enumerate(zip(gas, cost)):
        total += g - c
        tank += g - c
        if tank < 0:
            start, tank = i + 1, 0
    return start if total >= 0 else -1


def min_start_value(nums):
    """Smallest positive start so start + every prefix sum stays >= 1."""
    run = low = 0
    for x in nums:
        run += x
        low = min(low, run)
    return 1 - low


def max_profit_unlimited(prices):
    """Max profit with any number of buy-then-sell trades (hold one share max)."""
    return sum(max(0, b - a) for a, b in zip(prices, prices[1:]))


# ------------------------------------------------------------------------ tests


def completes_from(gas, cost, s):
    n, tank = len(gas), 0
    for k in range(n):
        i = (s + k) % n
        tank += gas[i] - cost[i]
        if tank < 0:
            return False
    return True


def brute_profit(prices):
    """Exhaustive search over hold / not hold on every day."""

    @cache
    def go(i, holding):
        if i == len(prices):
            return 0 if not holding else float("-inf")
        skip = go(i + 1, holding)
        trade = go(i + 1, not holding) + (prices[i] if holding else -prices[i])
        return max(skip, trade)

    return go(0, False)


def test_gas_station_examples():
    assert can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
    assert can_complete_circuit([2, 3, 4], [3, 4, 3]) == -1


def test_gas_station_matches_simulation():
    random.seed(7)
    for _ in range(500):
        n = random.randint(1, 7)
        gas = [random.randint(0, 5) for _ in range(n)]
        cost = [random.randint(0, 5) for _ in range(n)]
        valid = [s for s in range(n) if completes_from(gas, cost, s)]
        got = can_complete_circuit(gas, cost)
        if valid:
            assert got in valid
        else:
            assert got == -1


def test_min_start_value():
    assert min_start_value([-3, 2, -3, 4, 2]) == 5
    assert min_start_value([1, 2]) == 1
    random.seed(8)
    for _ in range(200):
        nums = [random.randint(-5, 5) for _ in range(random.randint(1, 8))]
        brute = next(s for s in range(1, 100)
                     if all(s + sum(nums[:i + 1]) >= 1 for i in range(len(nums))))
        assert min_start_value(nums) == brute


def test_stock_examples():
    assert max_profit_unlimited([7, 1, 5, 3, 6, 4]) == 7
    assert max_profit_unlimited([1, 2, 3, 4, 5]) == 4
    assert max_profit_unlimited([7, 6, 4, 3, 1]) == 0
    assert max_profit_unlimited([]) == 0


def test_stock_matches_exhaustive_search():
    random.seed(9)
    for _ in range(300):
        prices = [random.randint(1, 10) for _ in range(random.randint(0, 10))]
        assert max_profit_unlimited(prices) == brute_profit(tuple(prices))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
