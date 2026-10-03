"""Sort then assign — sort, then pair from the ends with two pointers.

Signs: match items to people (cookies to children, people to boats), split 2n
       people between two cities, spend or earn with tokens, "largest
       perimeter / sum using some of these".
Approach: sort so the right partner for each item is at a known end.
  - Assign cookies: smallest cookie that satisfies the least greedy child.
    Exchange: giving a bigger cookie never helps a child already satisfied.
  - Boats (two per boat): the heaviest person goes now; pair them with the
    lightest if possible. If even the lightest can't fit, nobody can.
  - Two cities: sort by cost_A - cost_B; the first half (biggest saving by
    flying to A) goes to A.
  - Bag of tokens: face-up the cheapest token (gain score), face-down the
    most valuable (gain power) only when stuck and more tokens remain.
  - Largest perimeter: sort descending; the first triple a < b + c wins. If a
    fails with the two largest below it, it fails with any pair.
Complexity: O(n log n) for the sort, then O(n).
Gotchas:
  - Boats: count a boat for every heaviest person, paired or not.
  - Bag of tokens: track the best score seen — the final score after a
    face-down can be lower than the peak.
  - Two cities: sort by the *difference*, not by either cost alone.

Run the tests at the bottom with:  python3 greedy/sort_assign.py
"""

import random
from functools import cache
from itertools import combinations


# ---------------------------------------------------------------- implementation


def assign_cookies(greed, sizes):
    """Max children content; child i needs a cookie of size >= greed[i]."""
    greed, sizes = sorted(greed), sorted(sizes)
    child = 0
    for s in sizes:
        if child < len(greed) and s >= greed[child]:
            child += 1
    return child


def num_boats(people, limit):
    """Fewest boats; each holds at most two people with total weight <= limit."""
    people = sorted(people)
    lo, hi, boats = 0, len(people) - 1, 0
    while lo <= hi:
        if people[lo] + people[hi] <= limit:
            lo += 1
        hi -= 1
        boats += 1
    return boats


def two_city_cost(costs):
    """2n people, costs[i] = (to_A, to_B). Exactly n to each. Min total."""
    costs = sorted(costs, key=lambda c: c[0] - c[1])
    n = len(costs) // 2
    return sum(a for a, _ in costs[:n]) + sum(b for _, b in costs[n:])


def bag_of_tokens(tokens, power):
    """Face-up: pay token, +1 score. Face-down: -1 score, gain token. Max score."""
    tokens = sorted(tokens)
    lo, hi = 0, len(tokens) - 1
    score = best = 0
    while lo <= hi:
        if power >= tokens[lo]:
            power -= tokens[lo]
            lo += 1
            score += 1
            best = max(best, score)
        elif score > 0 and lo < hi:
            power += tokens[hi]
            hi -= 1
            score -= 1
        else:
            break
    return best


def largest_perimeter(nums):
    """Largest perimeter of a non-degenerate triangle from three sides, or 0."""
    a = sorted(nums, reverse=True)
    for i in range(len(a) - 2):
        if a[i] < a[i + 1] + a[i + 2]:
            return a[i] + a[i + 1] + a[i + 2]
    return 0


# ------------------------------------------------------------------------ tests


def brute_cookies(greed, sizes):
    @cache
    def go(i, used):  # best for children i.. with cookie bitmask `used`
        if i == len(greed):
            return 0
        best = go(i + 1, used)  # child i gets nothing
        for j, s in enumerate(sizes):
            if not used >> j & 1 and s >= greed[i]:
                best = max(best, 1 + go(i + 1, used | 1 << j))
        return best

    return go(0, 0)


def brute_boats(people, limit):
    @cache
    def go(left):  # sorted tuple of people still on shore
        if not left:
            return 0
        first, rest = left[0], left[1:]
        best = 1 + go(rest)  # first rides alone
        for j in range(len(rest)):
            if first + rest[j] <= limit:
                best = min(best, 1 + go(rest[:j] + rest[j + 1:]))
        return best

    return go(tuple(sorted(people)))


def brute_two_city(costs):
    n = len(costs) // 2
    best = float("inf")
    for to_a in combinations(range(len(costs)), n):
        a = set(to_a)
        best = min(best, sum(costs[i][0] if i in a else costs[i][1] for i in range(len(costs))))
    return best


def brute_tokens(tokens, power):
    @cache
    def go(used, power, score):
        best = score
        for i, t in enumerate(tokens):
            if used >> i & 1:
                continue
            if power >= t:
                best = max(best, go(used | 1 << i, power - t, score + 1))
            if score > 0:
                best = max(best, go(used | 1 << i, power + t, score - 1))
        return best

    return go(0, power, 0)


def brute_perimeter(nums):
    best = 0
    for a, b, c in combinations(nums, 3):
        x, y, z = sorted((a, b, c))
        if x + y > z:
            best = max(best, a + b + c)
    return best


def test_assign_cookies():
    assert assign_cookies([1, 2, 3], [1, 1]) == 1
    assert assign_cookies([1, 2], [1, 2, 3]) == 2
    random.seed(10)
    for _ in range(300):
        g = [random.randint(1, 6) for _ in range(random.randint(0, 6))]
        s = [random.randint(1, 6) for _ in range(random.randint(0, 6))]
        assert assign_cookies(g, s) == brute_cookies(tuple(g), tuple(s))


def test_boats():
    assert num_boats([3, 2, 2, 1], 3) == 3
    assert num_boats([3, 5, 3, 4], 5) == 4
    random.seed(11)
    for _ in range(300):
        limit = random.randint(3, 10)
        people = [random.randint(1, limit) for _ in range(random.randint(1, 8))]
        assert num_boats(people, limit) == brute_boats(people, limit)


def test_two_city():
    assert two_city_cost([(10, 20), (30, 200), (400, 50), (30, 20)]) == 110
    random.seed(12)
    for _ in range(200):
        n = random.randint(1, 4)
        costs = [(random.randint(1, 50), random.randint(1, 50)) for _ in range(2 * n)]
        assert two_city_cost(costs) == brute_two_city(costs)


def test_bag_of_tokens():
    assert bag_of_tokens([100], 50) == 0
    assert bag_of_tokens([200, 100], 150) == 1
    assert bag_of_tokens([100, 200, 300, 400], 200) == 2
    random.seed(13)
    for _ in range(300):
        tokens = tuple(random.randint(1, 10) for _ in range(random.randint(0, 6)))
        power = random.randint(0, 15)
        assert bag_of_tokens(list(tokens), power) == brute_tokens(tokens, power)


def test_largest_perimeter():
    assert largest_perimeter([2, 1, 2]) == 5
    assert largest_perimeter([1, 2, 1, 10]) == 0
    random.seed(14)
    for _ in range(300):
        nums = [random.randint(1, 12) for _ in range(random.randint(3, 8))]
        assert largest_perimeter(nums) == brute_perimeter(nums)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
