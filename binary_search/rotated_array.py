"""Rotated sorted array — find the minimum, search for a target, with and without duplicates.

Signs: "sorted array rotated at an unknown pivot", "[4, 5, 6, 7, 0, 1, 2]",
       circularly sorted buffer, O(log n) still required.
Approach: compare a[mid] with a[hi] (the right end), never a[lo].
  - Minimum: a[mid] > a[hi] means the drop is right of mid (lo = mid + 1);
    otherwise mid..hi is sorted and the minimum is at mid or left (hi = mid).
  - Search: one half of [lo, hi] is always sorted. Check whether target lies
    inside the sorted half's value range; if so go there, else the other half.
  - Duplicates: a[mid] == a[hi] tells you nothing, so drop hi (hi -= 1). It
    keeps the answer because a[mid] is an equal copy still in range.
Complexity: O(log n) distinct; O(n) worst case with duplicates ([1,1,1,...,0,1]).
Gotchas:
  - Comparing with a[lo] fails on an un-rotated array: a[mid] >= a[lo] holds
    everywhere, so you can't tell which side the drop is on. a[hi] has no
    such blind spot.
  - In search, the sorted-half test uses <= on the low end:
    a[lo] <= target < a[mid]. lo == mid happens on 2-element ranges.
  - With duplicates, a[lo] == a[mid] == a[hi] defeats the sorted-half test;
    shrink both ends by one and continue.
  - Rotation count == index of the minimum.

Run the tests at the bottom with:  python3 binary_search/rotated_array.py
"""


# ---------------------------------------------------------------- implementation


def find_min_index(a):
    """Index of the minimum in a rotated array of DISTINCT values."""
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > a[hi]:
            lo = mid + 1  # drop is strictly right of mid
        else:
            hi = mid      # mid..hi sorted; min is mid or left of it
    return lo


def find_min_with_duplicates(a):
    """Minimum value of a rotated array that may contain duplicates."""
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > a[hi]:
            lo = mid + 1
        elif a[mid] < a[hi]:
            hi = mid
        else:
            hi -= 1  # a[mid] is a copy of a[hi]; losing a[hi] loses nothing
    return a[lo]


def search_rotated(a, target):
    """Index of target in a rotated array of distinct values, or -1."""
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return mid
        if a[lo] <= a[mid]:                      # left half [lo, mid] sorted
            if a[lo] <= target < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                    # right half [mid, hi] sorted
            if a[mid] < target <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


def search_rotated_with_duplicates(a, target):
    """True if target occurs in a rotated array that may contain duplicates."""
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return True
        if a[lo] == a[mid] == a[hi]:
            lo += 1          # can't tell which half is sorted
            hi -= 1
        elif a[lo] <= a[mid]:
            if a[lo] <= target < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if a[mid] < target <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return False


def search_via_pivot(a, target):
    """Second implementation: find the pivot, then a plain bisect on one side."""
    from bisect import bisect_left

    if not a:
        return -1
    p = find_min_index(a)
    lo, hi = (p, len(a)) if a[p] <= target <= a[-1] else (0, p)
    i = bisect_left(a, target, lo, hi)
    return i if i < hi and a[i] == target else -1


# ------------------------------------------------------------------------ tests


def _rotate(a, k):
    return a[k:] + a[:k]


def test_find_min_on_every_rotation():
    import random

    rng = random.Random(20)
    for _ in range(200):
        base = sorted(rng.sample(range(-50, 50), rng.randint(1, 12)))
        for k in range(len(base)):
            a = _rotate(base, k)
            i = find_min_index(a)
            assert a[i] == min(a)
            assert i == (len(a) - k) % len(a)  # rotation count


def test_find_min_with_duplicates_matches_min():
    import random

    rng = random.Random(21)
    for _ in range(500):
        base = sorted(rng.randint(0, 4) for _ in range(rng.randint(1, 12)))
        a = _rotate(base, rng.randrange(len(base)))
        assert find_min_with_duplicates(a) == min(a)


def test_search_matches_index_and_pivot_version():
    import random

    rng = random.Random(22)
    for _ in range(300):
        base = sorted(rng.sample(range(-30, 30), rng.randint(0, 12)))
        a = _rotate(base, rng.randrange(len(base))) if base else []
        for t in range(-32, 32):
            expected = a.index(t) if t in a else -1
            assert search_rotated(a, t) == expected
            assert search_via_pivot(a, t) == expected


def test_search_with_duplicates_matches_membership():
    import random

    rng = random.Random(23)
    for _ in range(500):
        base = sorted(rng.randint(0, 5) for _ in range(rng.randint(0, 12)))
        a = _rotate(base, rng.randrange(len(base))) if base else []
        for t in range(-1, 7):
            assert search_rotated_with_duplicates(a, t) == (t in a)


def test_duplicate_worst_case():
    # a[lo] == a[mid] == a[hi]: the case that forces linear shrinking
    a = [1, 1, 1, 1, 1, 0, 1, 1]
    assert find_min_with_duplicates(a) == 0
    assert search_rotated_with_duplicates(a, 0) is True
    assert search_rotated_with_duplicates([1, 0, 1, 1, 1], 0) is True


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
