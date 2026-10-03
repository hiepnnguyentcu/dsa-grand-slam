"""Sort, then sweep and merge — merge, insert, summary/missing ranges, partition.

Signs: "merge overlapping intervals", "insert into a sorted list of disjoint
       intervals", "summarise a sorted array as ranges", "what is missing
       between lower and upper", "split a string so each letter is in one part".
Approach: sort by start. Walk left to right holding the interval being built.
          If the next one starts at or before the current end, it overlaps:
          extend the end with max(). Otherwise close the current one and start
          fresh. Insert skips sorting: copy what ends before the new interval,
          absorb what overlaps it, copy the rest.
Complexity: O(n log n) for the sort, O(n) sweep. Insert and ranges are O(n).
Gotchas:
  - Closed [s, e]: touching intervals merge ([1, 4] + [4, 5] -> [1, 5]). For
    half-open use `s < end` instead of `s <= end`.
  - Extend with max(end, e), not e: [1, 10] swallows [2, 3].
  - Integers where adjacency counts ([1, 2] + [3, 4] -> [1, 4]): test
    `s <= end + 1`. Summary/missing ranges and the data-stream version
    (interval_set.py) use that rule.
  - Don't mutate the caller's lists; copy as you append.

Run the tests at the bottom with:  python3 intervals/merging.py
"""


# ---------------------------------------------------------------- implementation


def merge(intervals):
    """LC 56. Closed intervals, any order. Touching ones merge."""
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:            # overlaps the one being built
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def insert(intervals, new):
    """LC 57. `intervals` sorted and disjoint (closed). O(n), no sort."""
    s, e = new
    out, i, n = [], 0, len(intervals)
    while i < n and intervals[i][1] < s:       # entirely to the left
        out.append(list(intervals[i]))
        i += 1
    while i < n and intervals[i][0] <= e:      # overlaps: absorb
        s, e = min(s, intervals[i][0]), max(e, intervals[i][1])
        i += 1
    out.append([s, e])
    out.extend(list(x) for x in intervals[i:])  # entirely to the right
    return out


def summary_ranges(nums):
    """LC 228. Sorted unique ints -> ["0->2", "4", "6->7"]."""
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}->{nums[j]}")
        i = j + 1
    return out


def missing_ranges(nums, lower, upper):
    """LC 163. Sorted unique ints in [lower, upper] -> missing [a, b] ranges.

    Sentinels lower-1 and upper+1 turn the edges into ordinary gaps.
    """
    out, prev = [], lower - 1
    for x in nums + [upper + 1]:
        if x - prev >= 2:
            out.append([prev + 1, x - 1])
        prev = x
    return out


def partition_labels(s):
    """LC 763. Each letter spans [first, last]; merge the spans, return sizes.

    No sort needed: scanning left to right visits spans in start order.
    """
    last = {c: i for i, c in enumerate(s)}
    out, start, end = [], 0, 0
    for i, c in enumerate(s):
        end = max(end, last[c])
        if i == end:                           # nothing open reaches further
            out.append(end - start + 1)
            start = i + 1
    return out


# ------------------------------------------------------------------------ tests


def _runs(points):
    """Sorted ints -> maximal runs of consecutive values as [lo, hi]."""
    out = []
    for x in sorted(points):
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def _brute_merge(intervals):
    """Point coverage at half steps (doubled coords), then read off runs.

    Doubling makes the gap between [1, 2] and [3, 4] visible (2.5 is uncovered)
    while [1, 2] and [2, 3] stay one run.
    """
    pts = {x for s, e in intervals for x in range(2 * s, 2 * e + 1)}
    return [[lo // 2, hi // 2] for lo, hi in _runs(pts)]


def _rand_intervals(rng, n, hi=20):
    out = []
    for _ in range(n):
        a = rng.randint(0, hi)
        out.append([a, a + rng.randint(0, 5)])
    return out


def test_examples():
    assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
    assert merge([[1, 4], [4, 5]]) == [[1, 5]]                  # touching merges
    assert merge([[1, 10], [2, 3]]) == [[1, 10]]                # max(), not e
    assert insert([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
    assert insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]) == [
        [1, 2], [3, 10], [12, 16]]
    assert insert([], [5, 7]) == [[5, 7]]
    assert summary_ranges([0, 1, 2, 4, 5, 7]) == ["0->2", "4->5", "7"]
    assert missing_ranges([0, 1, 3, 50, 75], 0, 99) == [[2, 2], [4, 49], [51, 74], [76, 99]]
    assert missing_ranges([], 1, 1) == [[1, 1]]
    assert partition_labels("ababcbacadefegdehijhklij") == [9, 7, 8]


def test_merge_matches_point_coverage():
    import random

    rng = random.Random(1)
    for _ in range(500):
        iv = _rand_intervals(rng, rng.randint(0, 8))
        before = [list(x) for x in iv]
        assert merge(iv) == _brute_merge(iv)
        assert iv == before                                     # input untouched


def test_insert_matches_merge():
    import random

    rng = random.Random(2)
    for _ in range(500):
        base = merge(_rand_intervals(rng, rng.randint(0, 6)))  # sorted, disjoint
        new = _rand_intervals(rng, 1)[0]
        assert insert(base, new) == _brute_merge(base + [new])


def test_ranges_match_sets():
    import random

    rng = random.Random(3)
    for _ in range(500):
        lower = rng.randint(-5, 5)
        upper = lower + rng.randint(0, 15)
        nums = sorted(rng.sample(range(lower, upper + 1), rng.randint(0, upper - lower + 1)))
        assert summary_ranges(nums) == [
            str(a) if a == b else f"{a}->{b}" for a, b in _runs(nums)]
        missing = set(range(lower, upper + 1)) - set(nums)
        assert missing_ranges(nums, lower, upper) == _runs(missing)


def test_partition_labels_matches_brute_force():
    import random
    from itertools import combinations

    rng = random.Random(4)
    for _ in range(300):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(1, 9)))
        best = None                                             # most parts wins
        for k in range(len(s)):
            for cuts in combinations(range(1, len(s)), k):
                bounds = (0,) + cuts + (len(s),)
                parts = [s[bounds[i]:bounds[i + 1]] for i in range(len(bounds) - 1)]
                if all(not set(p) & set(q) for i, p in enumerate(parts) for q in parts[i + 1:]):
                    best = [len(p) for p in parts]
        assert partition_labels(s) == best


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
