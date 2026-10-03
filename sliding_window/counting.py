"""Counting subarrays with a window — at most k, exactly k, and when to stop.

Signs: "number of subarrays such that ...", "product less than k", "exactly
       k distinct", "binary subarrays with sum S", "nice subarrays (k odds)".
Approach: with a longest-valid window, every subarray ending at right and
          starting in [left, right] is valid -> add right - left + 1. That
          counts "at most k". "Exactly k" isn't monotone, so it can't be a
          window directly; but exactly(k) = atMost(k) - atMost(k - 1).
          Values can be negative (or the rule isn't monotone)? Switch to
          prefix sums + a hash map of prefix counts.
Complexity: O(n) per atMost call; prefix-sum version O(n) time and space.
Gotchas:
  - atMost(k - 1) with k == 0 means atMost(-1) == 0: guard k < 0.
  - Product < k: if k <= 1 no positive product qualifies; return 0 before
    the loop or `while prod >= k` runs left past right.
  - Binary sum / nice subarrays are the same problem: map odd -> 1, even -> 0.
  - Prefix-sum count: seed the map with {0: 1} for subarrays starting at 0.
    It works with negatives; the window does not.

Run the tests at the bottom with:  python3 sliding_window/counting.py
"""

from collections import defaultdict


# ---------------------------------------------------------------- implementation


def num_subarray_product_less_than_k(a, k):
    """LC 713. Positive a; subarrays with product < k."""
    if k <= 1:
        return 0
    prod, left, count = 1, 0, 0
    for right, x in enumerate(a):
        prod *= x
        while prod >= k:
            prod //= a[left]   # exact: a[left] divides prod
            left += 1
        count += right - left + 1  # every start in [left, right] works
    return count


def at_most_k_distinct(a, k):
    """Subarrays with at most k distinct values."""
    if k < 0:
        return 0
    seen = defaultdict(int)
    left = count = 0
    for right, x in enumerate(a):
        seen[x] += 1
        while len(seen) > k:
            seen[a[left]] -= 1
            if seen[a[left]] == 0:
                del seen[a[left]]
            left += 1
        count += right - left + 1
    return count


def subarrays_with_k_distinct(a, k):
    """LC 992. Exactly k distinct = atMost(k) - atMost(k - 1)."""
    return at_most_k_distinct(a, k) - at_most_k_distinct(a, k - 1)


def at_most_sum(a, s):
    """Subarrays of a non-negative array with sum <= s."""
    if s < 0:
        return 0
    left = total = count = 0
    for right, x in enumerate(a):
        total += x
        while total > s:
            total -= a[left]
            left += 1
        count += right - left + 1
    return count


def num_subarrays_with_sum(a, goal):
    """LC 930. Binary array; subarrays summing to exactly goal."""
    return at_most_sum(a, goal) - at_most_sum(a, goal - 1)


def number_of_nice_subarrays(a, k):
    """LC 1248. Subarrays with exactly k odd numbers."""
    return num_subarrays_with_sum([x % 2 for x in a], k)


def subarray_sum_equals_k(a, k):
    """LC 560. Any integers (negatives too): prefix sums + hash map.

    The fallback when a window can't work. Count earlier prefixes p with
    current - p == k.
    """
    seen = defaultdict(int)
    seen[0] = 1
    cur = count = 0
    for x in a:
        cur += x
        count += seen[cur - k]
        seen[cur] += 1
    return count


# ------------------------------------------------------------------------ tests


def _brute_count(a, valid):
    n = len(a)
    return sum(valid(a[i:j]) for i in range(n) for j in range(i + 1, n + 1))


def test_examples():
    assert num_subarray_product_less_than_k([10, 5, 2, 6], 100) == 8
    assert num_subarray_product_less_than_k([1, 2, 3], 0) == 0
    assert subarrays_with_k_distinct([1, 2, 1, 2, 3], 2) == 7
    assert num_subarrays_with_sum([1, 0, 1, 0, 1], 2) == 4
    assert number_of_nice_subarrays([1, 1, 2, 1, 1], 3) == 2
    assert subarray_sum_equals_k([1, -1, 0], 0) == 3


def test_product_matches_brute_force():
    import random
    from math import prod

    rng = random.Random(1)
    for _ in range(400):
        a = [rng.randint(1, 6) for _ in range(rng.randint(0, 10))]
        k = rng.randint(0, 60)
        assert num_subarray_product_less_than_k(a, k) == _brute_count(a, lambda w: prod(w) < k)


def test_exactly_k_matches_brute_force():
    import random

    rng = random.Random(2)
    for _ in range(400):
        a = [rng.randint(0, 3) for _ in range(rng.randint(0, 10))]
        k = rng.randint(0, 4)
        assert subarrays_with_k_distinct(a, k) == _brute_count(a, lambda w: len(set(w)) == k)
        b = [rng.randint(0, 1) for _ in range(rng.randint(0, 10))]
        g = rng.randint(0, 4)
        assert num_subarrays_with_sum(b, g) == _brute_count(b, lambda w: sum(w) == g)
        c = [rng.randint(1, 9) for _ in range(rng.randint(0, 10))]
        assert number_of_nice_subarrays(c, g) == _brute_count(c, lambda w: sum(x % 2 for x in w) == g)


def test_prefix_sum_handles_negatives():
    import random

    rng = random.Random(3)
    for _ in range(400):
        a = [rng.randint(-3, 3) for _ in range(rng.randint(0, 10))]
        k = rng.randint(-4, 4)
        assert subarray_sum_equals_k(a, k) == _brute_count(a, lambda w: sum(w) == k)


def test_window_fails_on_negatives():
    # at_most_sum assumes x >= 0. At right=2 it drops -3 and 5 together, so
    # it counts [1] but also the start it skipped — 4 instead of 3.
    a = [-3, 5, 1]
    assert _brute_count(a, lambda w: sum(w) <= 2) == 3
    assert at_most_sum(a, 2) == 4


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
