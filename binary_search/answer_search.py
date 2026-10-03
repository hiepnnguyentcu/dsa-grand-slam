"""Binary search on the answer — guess a value, check feasibility, halve.

Signs: "minimise the maximum", "maximise the minimum", "smallest speed /
       capacity / days such that ...", a feasibility check that is easy when
       the answer is GIVEN, answers in a big numeric range (up to 1e9).
Approach: the answer is a number in [lo, hi]. Write feasible(x): "can it be
          done with x?" If feasible is monotone (feasible(x) implies
          feasible(x + 1)), the answer is first_true over [lo, hi]. The check
          is usually one greedy pass.
Complexity: O(check x log(hi - lo)). With an O(n) greedy check and a 1e9
            range, that is about 30 passes.
Gotchas:
  - Bounds must bracket the answer: lo = the smallest value that could ever
    work (often max(a)), hi = one that always works (often sum(a)).
  - Prove monotonicity before coding. If feasible(x) does not imply
    feasible(x + 1), binary search silently returns garbage.
  - "Maximise the minimum" is last_true; flip the predicate or search the
    complement.
  - Ceil division in the check: (p + k - 1) // k, or -(-p // k).
  - Impossible inputs (fewer flowers than m * k) need a guard, not a search.

Run the tests at the bottom with:  python3 binary_search/answer_search.py
"""


# ---------------------------------------------------------------- implementation


def first_true(lo, hi, pred):
    """Smallest x in [lo, hi] with pred(x) True. Caller guarantees pred(hi)."""
    while lo < hi:
        mid = (lo + hi) // 2
        if pred(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def min_eating_speed(piles, h):
    """Koko: smallest k so that eating k bananas/hour finishes in <= h hours.

    Hours at speed k = sum(ceil(p / k)). More speed never costs more hours.
    """
    def ok(k):
        return sum(-(-p // k) for p in piles) <= h

    return first_true(1, max(piles), ok)


def ship_within_days(weights, days):
    """Smallest ship capacity that ships all packages, in order, within `days`.

    Greedy check: fill a day until the next package would overflow.
    Capacity must be at least max(weights) or one package never fits.
    """
    def ok(cap):
        used, load = 1, 0
        for w in weights:
            if load + w > cap:
                used, load = used + 1, 0
            load += w
        return used <= days

    return first_true(max(weights), sum(weights), ok)


def split_array_largest_sum(nums, k):
    """Split into k non-empty contiguous parts minimising the largest part sum.

    Same check as shipping: "can it be cut into <= k parts each <= cap?"
    Fewer parts than k is fine — any part with 2+ elements can be split more.
    """
    return ship_within_days(nums, k)


def min_days_bouquets(bloom_day, m, k):
    """Fewest days until m bouquets of k ADJACENT bloomed flowers can be made, or -1.

    By day d, flower i is bloomed iff bloom_day[i] <= d. Count runs greedily.
    """
    if m * k > len(bloom_day):
        return -1

    def ok(d):
        made = run = 0
        for b in bloom_day:
            run = run + 1 if b <= d else 0
            if run == k:
                made, run = made + 1, 0
        return made >= m

    return first_true(min(bloom_day), max(bloom_day), ok)


def max_min_distance(positions, balls):
    """Place `balls` in sorted positions maximising the minimum gap (magnetic force).

    Maximise-the-minimum: feasible(g) = "a gap of at least g is achievable"
    is True ... True False ... False, so search the first g that FAILS and
    step back.
    """
    pos = sorted(positions)

    def can(g):
        count, last = 1, pos[0]
        for p in pos[1:]:
            if p - last >= g:
                count, last = count + 1, p
        return count >= balls

    hi = pos[-1] - pos[0] + 1                  # can(hi) is always False
    return first_true(1, hi, lambda g: not can(g)) - 1


# ----------------------------------------------------------------- brute force


def _brute_koko(piles, h):
    k = 1
    while sum(-(-p // k) for p in piles) > h:
        k += 1
    return k


def _brute_split(nums, k):
    """Try every placement of k - 1 cuts."""
    from itertools import combinations

    n = len(nums)
    best = float("inf")
    for cuts in combinations(range(1, n), k - 1):
        bounds = (0, *cuts, n)
        best = min(best, max(sum(nums[a:b]) for a, b in zip(bounds, bounds[1:])))
    return best


def _brute_bouquets(bloom_day, m, k):
    for d in sorted(set(bloom_day)):
        made = run = 0
        for b in bloom_day:
            run = run + 1 if b <= d else 0
            if run == k:
                made, run = made + 1, 0
        if made >= m:
            return d
    return -1


def _brute_max_min(positions, balls):
    from itertools import combinations

    return max(
        min(b - a for a, b in zip(c, c[1:]))
        for c in combinations(sorted(positions), balls)
    )


# ------------------------------------------------------------------------ tests


def test_koko_examples_and_brute_force():
    import random

    assert min_eating_speed([3, 6, 7, 11], 8) == 4
    assert min_eating_speed([30, 11, 23, 4, 20], 5) == 30
    rng = random.Random(40)
    for _ in range(300):
        piles = [rng.randint(1, 30) for _ in range(rng.randint(1, 6))]
        h = rng.randint(len(piles), len(piles) + 20)
        assert min_eating_speed(piles, h) == _brute_koko(piles, h)


def test_ship_and_split_match_brute_force():
    import random

    assert ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
    assert split_array_largest_sum([7, 2, 5, 10, 8], 2) == 18
    rng = random.Random(41)
    for _ in range(300):
        nums = [rng.randint(0, 20) for _ in range(rng.randint(1, 8))]
        k = rng.randint(1, len(nums))
        assert split_array_largest_sum(nums, k) == _brute_split(nums, k)


def test_bouquets_match_brute_force():
    import random

    assert min_days_bouquets([1, 10, 3, 10, 2], 3, 1) == 3
    assert min_days_bouquets([1, 10, 3, 10, 2], 3, 2) == -1
    assert min_days_bouquets([7, 7, 7, 7, 12, 7, 7], 2, 3) == 12
    rng = random.Random(42)
    for _ in range(500):
        bloom = [rng.randint(1, 15) for _ in range(rng.randint(1, 10))]
        m, k = rng.randint(1, 4), rng.randint(1, 3)
        assert min_days_bouquets(bloom, m, k) == _brute_bouquets(bloom, m, k)


def test_max_min_distance_matches_brute_force():
    import random

    assert max_min_distance([1, 2, 3, 4, 7], 3) == 3
    assert max_min_distance([5, 4, 3, 2, 1, 1000000000], 2) == 999999999
    rng = random.Random(43)
    for _ in range(300):
        pos = rng.sample(range(0, 40), rng.randint(2, 8))
        balls = rng.randint(2, len(pos))
        assert max_min_distance(pos, balls) == _brute_max_min(pos, balls)


def test_feasibility_is_monotone():
    # The precondition for all of the above, checked directly.
    import random

    rng = random.Random(44)
    for _ in range(100):
        w = [rng.randint(1, 10) for _ in range(rng.randint(1, 8))]
        d = rng.randint(1, len(w))
        flags = []
        for cap in range(max(w), sum(w) + 1):
            used, load = 1, 0
            for x in w:
                if load + x > cap:
                    used, load = used + 1, 0
                load += x
            flags.append(used <= d)
        assert flags == sorted(flags)  # F..F T..T
        assert flags[-1]               # hi always works


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
