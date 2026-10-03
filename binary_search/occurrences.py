"""Occurrences and positions — first/last, count, insert position, floor/ceil, k closest.

Signs: "first and last position of x", "how many times does x appear",
       "where would x be inserted", "largest element <= x", "closest value",
       "k closest elements", repeated range-count queries on a sorted list.
Approach: all of these are two boundaries in a sorted array:
          lower = first index with a[i] >= x, upper = first index with a[i] > x.
          The run of x is [lower, upper); its length is the count; lower is the
          insert position; a[lower - 1] is the floor of anything below x.
          In Python these are bisect_left and bisect_right.
Complexity: O(log n) per query. Building the sorted list is O(n log n) once.
Gotchas:
  - bisect_left vs bisect_right only differ when x is present. Insert
    position for "before equals" is left; "after equals" is right.
  - Always check the index is in range before reading a[i] — both functions
    can return len(a).
  - bisect's `key=` (Python 3.10+) applies to the elements, NOT to x: pass
    x already transformed. insort with key does transform the inserted item.
  - insort into a list is O(n) because of the shift. Many inserts + queries
    want a balanced tree / SortedList, or offline sorting.
  - k closest: binary search the LEFT EDGE of the window, not x itself.

Run the tests at the bottom with:  python3 binary_search/occurrences.py
"""

from bisect import bisect_left, bisect_right


# ---------------------------------------------------------------- implementation


def search_range(a, x):
    """[first, last] index of x in sorted a, or [-1, -1]."""
    lo = bisect_left(a, x)
    if lo == len(a) or a[lo] != x:
        return [-1, -1]
    return [lo, bisect_right(a, x) - 1]


def count_occurrences(a, x):
    return bisect_right(a, x) - bisect_left(a, x)


def count_in_range(a, lo, hi):
    """How many values v in sorted a have lo <= v <= hi."""
    return max(0, bisect_right(a, hi) - bisect_left(a, lo))  # hi < lo would go negative


def search_insert(a, x):
    """Index of x if present, else where it would go to keep a sorted."""
    return bisect_left(a, x)


def floor_value(a, x):
    """Largest value <= x, or None."""
    i = bisect_right(a, x)
    return a[i - 1] if i else None


def ceil_value(a, x):
    """Smallest value >= x, or None."""
    i = bisect_left(a, x)
    return a[i] if i < len(a) else None


def closest_value(a, x):
    """Value in non-empty sorted a nearest to x; ties go to the smaller one."""
    i = bisect_left(a, x)
    candidates = a[max(0, i - 1):i + 1]
    return min(candidates, key=lambda v: (abs(v - x), v))


def k_closest(a, k, x):
    """The k values nearest x (ties prefer smaller), in sorted order.

    Search for the window's left edge L in [0, n - k]. Window [L, L + k)
    should move right while x is closer to a[L + k] than to a[L]:
    x - a[L] > a[L + k] - x. That predicate is monotone in L (True ... False),
    so the first L where it is False is the answer.
    """
    lo, hi = 0, len(a) - k
    while lo < hi:
        mid = (lo + hi) // 2
        if x - a[mid] > a[mid + k] - x:
            lo = mid + 1
        else:
            hi = mid
    return a[lo:lo + k]


def bisect_with_key(records, target_age):
    """Index of the first record with age >= target_age. records sorted by age.

    `key` is applied to list elements only. target_age is passed raw.
    """
    return bisect_left(records, target_age, key=lambda r: r[1])


# ------------------------------------------------------------------------ tests


def _random_sorted(rng, n, span):
    return sorted(rng.randint(-span, span) for _ in range(n))


def test_search_range_and_count_match_brute_force():
    import random

    rng = random.Random(10)
    for _ in range(500):
        a = _random_sorted(rng, rng.randint(0, 15), 5)
        x = rng.randint(-7, 7)
        idx = [i for i, v in enumerate(a) if v == x]
        assert search_range(a, x) == ([idx[0], idx[-1]] if idx else [-1, -1])
        assert count_occurrences(a, x) == len(idx)


def test_count_in_range_matches_brute_force():
    import random

    rng = random.Random(11)
    for _ in range(500):
        a = _random_sorted(rng, rng.randint(0, 15), 10)
        lo = rng.randint(-12, 12)
        hi = lo + rng.randint(-2, 10)  # sometimes an empty range (hi < lo)
        assert count_in_range(a, lo, hi) == sum(lo <= v <= hi for v in a)


def test_insert_position_keeps_list_sorted():
    import random

    rng = random.Random(12)
    for _ in range(300):
        a = sorted(set(_random_sorted(rng, rng.randint(0, 12), 10)))
        x = rng.randint(-12, 12)
        i = search_insert(a, x)
        b = a[:i] + [x] + a[i:]
        assert b == sorted(b)
        if x in a:
            assert a[i] == x


def test_floor_ceil_closest_match_brute_force():
    import random

    rng = random.Random(13)
    for _ in range(500):
        a = _random_sorted(rng, rng.randint(1, 12), 10)
        x = rng.randint(-12, 12)
        assert floor_value(a, x) == max((v for v in a if v <= x), default=None)
        assert ceil_value(a, x) == min((v for v in a if v >= x), default=None)
        assert closest_value(a, x) == min(a, key=lambda v: (abs(v - x), v))


def test_k_closest_matches_sort_by_distance():
    import random

    rng = random.Random(14)
    for _ in range(500):
        a = _random_sorted(rng, rng.randint(1, 12), 10)
        k = rng.randint(1, len(a))
        x = rng.randint(-14, 14)
        expected = sorted(sorted(a, key=lambda v: (abs(v - x), v))[:k])
        assert k_closest(a, k, x) == expected


def test_k_closest_examples():
    assert k_closest([1, 2, 3, 4, 5], 4, 3) == [1, 2, 3, 4]
    assert k_closest([1, 1, 2, 3, 4, 5], 4, -1) == [1, 1, 2, 3]


def test_bisect_key_is_not_applied_to_target():
    people = [("ann", 19), ("bob", 25), ("cat", 25), ("dan", 40)]
    assert bisect_with_key(people, 25) == 1
    assert bisect_with_key(people, 26) == 3
    assert bisect_with_key(people, 99) == 4


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
