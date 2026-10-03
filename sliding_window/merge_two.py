"""Two pointers over two sequences — merge, intersect, subsequence, intervals.

Signs: two sorted arrays or lists, "merge", "intersection", "is s a
       subsequence of t", two sorted lists of intervals, "merge in place into
       the first array which has room at the end".
Approach: one pointer per sequence. Compare the two heads, consume the one
          that is "behind" (smaller value, earlier end), and advance only it.
          For in-place merge into a buffer at the end, write from the BACK so
          nothing unread is overwritten.
Complexity: O(m + n) time; O(1) extra besides the output.
Gotchas:
  - Don't forget the tail: after the loop one side may still have items.
  - In-place merge (LC 88): only nums2 leftovers need copying; nums1's are
    already in place.
  - Interval intersection: overlap is [max(starts), min(ends)] if start <=
    end; then drop the interval that ends FIRST — it can't meet anything else.
  - Intersection with duplicates (LC 350) keeps min(count) copies; set
    intersection (LC 349) skips repeats.
  - k sorted sequences -> heap: stacks_heaps/k_way_merge.py.

Run the tests at the bottom with:  python3 sliding_window/merge_two.py
"""


# ---------------------------------------------------------------- implementation


def merge_sorted(a, b):
    """Merge two sorted lists into a new sorted list. Stable (a before b)."""
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


def merge_into(nums1, m, nums2, n):
    """LC 88. nums1 has m values then n slots; merge nums2 in place."""
    i, j, w = m - 1, n - 1, m + n - 1
    while j >= 0:                      # once nums2 is empty, nums1 is done
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[w] = nums1[i]
            i -= 1
        else:
            nums1[w] = nums2[j]
            j -= 1
        w -= 1


def intersect_sorted(a, b):
    """LC 350 on sorted input: common values with multiplicity."""
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            i += 1
        elif a[i] > b[j]:
            j += 1
        else:
            out.append(a[i])
            i += 1
            j += 1
    return out


def is_subsequence(s, t):
    """LC 392. Greedy: match each char of s at its earliest spot in t."""
    i = 0
    for c in t:
        if i < len(s) and s[i] == c:
            i += 1
    return i == len(s)


def interval_intersection(A, B):
    """LC 986. Both lists sorted and internally disjoint; closed intervals."""
    i = j = 0
    out = []
    while i < len(A) and j < len(B):
        lo = max(A[i][0], B[j][0])
        hi = min(A[i][1], B[j][1])
        if lo <= hi:
            out.append([lo, hi])
        if A[i][1] < B[j][1]:          # A[i] ends first: done with it
            i += 1
        else:
            j += 1
    return out


# ------------------------------------------------------------------------ tests


def test_examples():
    assert merge_sorted([1, 3, 5], [2, 4]) == [1, 2, 3, 4, 5]
    a = [1, 2, 3, 0, 0, 0]
    merge_into(a, 3, [2, 5, 6], 3)
    assert a == [1, 2, 2, 3, 5, 6]
    assert intersect_sorted([1, 2, 2, 3], [2, 2, 4]) == [2, 2]
    assert is_subsequence("abc", "ahbgdc") and not is_subsequence("axc", "ahbgdc")
    A = [[0, 2], [5, 10], [13, 23], [24, 25]]
    B = [[1, 5], [8, 12], [15, 24], [25, 26]]
    assert interval_intersection(A, B) == [[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]


def _rand_sorted(rng, n):
    return sorted(rng.randint(0, 9) for _ in range(n))


def test_merges_match_sorted():
    import random

    rng = random.Random(1)
    for _ in range(500):
        a, b = _rand_sorted(rng, rng.randint(0, 8)), _rand_sorted(rng, rng.randint(0, 8))
        assert merge_sorted(a, b) == sorted(a + b)
        buf = a + [0] * len(b)
        merge_into(buf, len(a), b, len(b))
        assert buf == sorted(a + b)


def test_intersect_matches_counter():
    import random
    from collections import Counter

    rng = random.Random(2)
    for _ in range(500):
        a, b = _rand_sorted(rng, rng.randint(0, 10)), _rand_sorted(rng, rng.randint(0, 10))
        assert intersect_sorted(a, b) == sorted((Counter(a) & Counter(b)).elements())


def test_subsequence_matches_brute_force():
    import random
    from itertools import combinations

    rng = random.Random(3)
    for _ in range(500):
        t = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 4)))
        brute = any("".join(c) == s for c in combinations(t, len(s)))
        assert is_subsequence(s, t) == brute


def test_interval_intersection_matches_point_sets():
    import random

    rng = random.Random(4)

    def rand_intervals():
        pts = sorted(rng.sample(range(30), 2 * rng.randint(0, 5)))
        return [[pts[k], pts[k + 1]] for k in range(0, len(pts), 2)]

    def cover(iv):  # integer points, doubled so touching endpoints count
        return {x for lo, hi in iv for x in range(2 * lo, 2 * hi + 1)}

    for _ in range(500):
        A, B = rand_intervals(), rand_intervals()
        got = interval_intersection(A, B)
        assert cover(got) == cover(A) & cover(B)
        assert got == sorted(got)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
