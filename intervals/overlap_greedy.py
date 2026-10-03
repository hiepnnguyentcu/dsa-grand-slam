"""Greedy by earliest end — can attend, max meetings, remove overlaps, arrows.

Signs: "can one person attend all meetings", "maximum number of meetings /
       activities", "minimum intervals to remove so the rest don't overlap",
       "minimum arrows / points / darts to hit every interval".
Approach: sort by END. Take the interval that finishes first; it leaves the
          most room for everything after it (exchange argument: any optimal
          answer can swap its first pick for this one). Skip whatever
          overlaps the last pick, take the next that doesn't.
  - Max non-overlapping = number of picks. Min removals = n - picks.
  - Min arrows = same count: one arrow at each pick's end bursts every
    balloon that overlaps that pick.
  - Can attend = sort by start, check each start against the previous end.
Complexity: O(n log n) for the sort, O(n) sweep, O(1) extra.
Gotchas:
  - Meetings are half-open [s, e): [1, 2] and [2, 3] don't clash.
    Balloons are closed [s, e]: one arrow at 2 bursts both. Pick `<` vs `<=`
    from the problem, not from habit.
  - Sorting by START for max-meetings is wrong: [1, 100] would block
    [2, 3], [4, 5]. (Start order is fine for can-attend and for merging.)
  - Min meeting ROOMS is a different question (how many overlap at once):
    sweep_line.py, or the heap in stacks_heaps/heap_scheduling.py.

Run the tests at the bottom with:  python3 intervals/overlap_greedy.py
"""


# ---------------------------------------------------------------- implementation


def can_attend_meetings(intervals):
    """LC 252. Half-open: a meeting may start the minute another ends."""
    iv = sorted(intervals)
    return all(iv[i - 1][1] <= iv[i][0] for i in range(1, len(iv)))


def max_meetings(intervals):
    """Activity selection: the most pairwise non-overlapping [s, e)."""
    picked, end = [], float("-inf")
    for s, e in sorted(intervals, key=lambda x: x[1]):
        if s >= end:                           # starts after the last pick ends
            picked.append([s, e])
            end = e
    return picked


def erase_overlap_intervals(intervals):
    """LC 435. Fewest removals so the rest are non-overlapping (half-open)."""
    return len(intervals) - len(max_meetings(intervals))


def find_min_arrow_shots(points):
    """LC 452. Closed [s, e]: an arrow at x bursts every s <= x <= e."""
    arrows, arrow = 0, float("-inf")
    for s, e in sorted(points, key=lambda x: x[1]):
        if s > arrow:                          # this balloon survived: shoot its end
            arrows += 1
            arrow = e
    return arrows


# ------------------------------------------------------------------------ tests


def _overlap_half_open(a, b):
    return a[0] < b[1] and b[0] < a[1]


def _rand_intervals(rng, n, hi=15):
    out = []
    for _ in range(n):
        a = rng.randint(0, hi)
        out.append([a, a + rng.randint(1, 6)])
    return out


def test_examples():
    assert can_attend_meetings([[7, 10], [2, 4]])
    assert not can_attend_meetings([[0, 30], [5, 10], [15, 20]])
    assert can_attend_meetings([[1, 2], [2, 3]])                 # touching is fine
    assert erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1
    assert erase_overlap_intervals([[1, 2], [1, 2], [1, 2]]) == 2
    assert max_meetings([[1, 100], [2, 3], [4, 5]]) == [[2, 3], [4, 5]]
    assert find_min_arrow_shots([[10, 16], [2, 8], [1, 6], [7, 12]]) == 2
    assert find_min_arrow_shots([[1, 2], [2, 3], [3, 4], [4, 5]]) == 2  # closed


def test_can_attend_matches_pairwise():
    import random

    rng = random.Random(1)
    for _ in range(500):
        iv = _rand_intervals(rng, rng.randint(0, 5))
        brute = not any(_overlap_half_open(iv[i], iv[j])
                        for i in range(len(iv)) for j in range(i + 1, len(iv)))
        assert can_attend_meetings(iv) == brute


def test_max_meetings_matches_subsets():
    import random

    rng = random.Random(2)
    for _ in range(300):
        iv = _rand_intervals(rng, rng.randint(0, 9))
        best = 0
        for mask in range(1 << len(iv)):
            chosen = [iv[i] for i in range(len(iv)) if mask >> i & 1]
            if all(not _overlap_half_open(a, b)
                   for i, a in enumerate(chosen) for b in chosen[i + 1:]):
                best = max(best, len(chosen))
        picked = max_meetings(iv)
        assert len(picked) == best
        assert all(not _overlap_half_open(a, b)
                   for i, a in enumerate(picked) for b in picked[i + 1:])
        assert erase_overlap_intervals(iv) == len(iv) - best


def test_arrows_match_hitting_set_brute_force():
    import random
    from itertools import combinations

    rng = random.Random(3)
    for _ in range(300):
        pts = _rand_intervals(rng, rng.randint(0, 6))
        spots = sorted({x for s, e in pts for x in range(s, e + 1)})
        best = 0 if not pts else None
        for k in range(1, len(pts) + 1):                        # smallest k that hits all
            if any(all(any(s <= x <= e for x in xs) for s, e in pts)
                   for xs in combinations(spots, k)):
                best = k
                break
        assert find_min_arrow_shots(pts) == best


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
