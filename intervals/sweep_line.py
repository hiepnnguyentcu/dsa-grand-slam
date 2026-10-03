"""Sweep line over event points — rooms, busiest time, free time, skyline.

Signs: "how many at once", "minimum rooms / platforms / servers", "when is
       it busiest", "common free time", "outline of overlapping rectangles".
Approach: split every interval into two events, +1 at start and -1 at end,
          sort, and walk them keeping a running count (or a heap of what is
          active). The answer changes only at event points, so nothing
          between them needs checking.
  - Rooms: sort starts and ends separately. Each start either reuses the
    room of the earliest unfinished end (start >= that end) or opens a new
    one. No heap needed when you only want the count.
  - Free time: merge everyone's busy blocks, then report the gaps.
  - Skyline: a max-heap of (height, right edge) of active buildings. Expired
    buildings are popped lazily when they reach the top.
Complexity: O(n log n) for the sort; skyline O(n log n) with the heap.
Gotchas:
  - Ties decide the answer. Half-open [s, e): process the end before the
    start at the same time, so [1, 2] and [2, 3] need one room. Closed: start
    first. As tuples, (t, -1) sorts before (t, +1) for free.
  - Contrasting versions elsewhere: rooms with a heap of end times
    (stacks_heaps/heap_scheduling.py), max overlap via a difference Counter
    (prefix_sums/difference_array.py). This file returns WHEN, not just how many.
  - Skyline: emit a point only when the max height changes, or you get
    duplicates at shared edges.

Run the tests at the bottom with:  python3 intervals/sweep_line.py
"""

import heapq


# ---------------------------------------------------------------- implementation


def min_meeting_rooms(intervals):
    """LC 253 with two sorted arrays. Half-open: ending at t frees a room for t."""
    starts = sorted(s for s, _ in intervals)
    ends = sorted(e for _, e in intervals)
    rooms = j = 0
    for s in starts:
        if s >= ends[j]:      # earliest-ending meeting is done: reuse its room
            j += 1
        else:
            rooms += 1
    return rooms


def busiest_time(intervals):
    """(max overlap, earliest time it is reached) for half-open [s, e).

    Returns (0, None) for no intervals.
    """
    events = sorted([(s, 1) for s, _ in intervals] + [(e, -1) for _, e in intervals])
    best, when, cur = 0, None, 0
    for t, d in events:       # (t, -1) before (t, +1): ends release first
        cur += d
        if cur > best:
            best, when = cur, t
    return best, when


def employee_free_time(schedule):
    """LC 759. schedule[i] = employee i's busy [s, e) blocks.

    Returns the finite gaps of positive length when nobody is busy.
    """
    blocks = sorted(iv for person in schedule for iv in person)
    gaps = []
    if not blocks:
        return gaps
    end = blocks[0][1]
    for s, e in blocks:
        if s > end:           # strict: touching blocks leave no gap
            gaps.append([end, s])
        end = max(end, e)
    return gaps


def get_skyline(buildings):
    """LC 218. buildings = [left, right, height]; returns [[x, height]] key points."""
    events = [(l, -h, r) for l, r, h in buildings]   # starts, tallest first
    events += [(r, 0, 0) for _, r, _ in buildings]   # ends after starts at same x
    events.sort()
    out = [[0, 0]]
    heap = [(0, float("inf"))]                       # (-height, right); ground never ends
    for x, neg_h, r in events:
        while heap[0][1] <= x:                       # lazy deletion of expired tops
            heapq.heappop(heap)
        if neg_h:
            heapq.heappush(heap, (neg_h, r))
        h = -heap[0][0]
        if out[-1][1] != h:
            out.append([x, h])
    return out[1:]


# ------------------------------------------------------------------------ tests


def _rand_intervals(rng, n, hi=20):
    out = []
    for _ in range(n):
        a = rng.randint(0, hi)
        out.append([a, a + rng.randint(1, 6)])
    return out


def _timeline(intervals):
    """count[t] = intervals covering unit cell [t, t+1)."""
    if not intervals:
        return {}
    lo, hi = min(s for s, _ in intervals), max(e for _, e in intervals)
    return {t: sum(s <= t < e for s, e in intervals) for t in range(lo, hi)}


def test_examples():
    assert min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2
    assert min_meeting_rooms([[1, 2], [2, 3]]) == 1               # half-open
    assert min_meeting_rooms([]) == 0
    assert busiest_time([[1, 4], [2, 5], [7, 9], [3, 6]]) == (3, 3)
    assert employee_free_time([[[1, 2], [5, 6]], [[1, 3]], [[4, 10]]]) == [[3, 4]]
    assert employee_free_time([[[1, 3], [6, 7]], [[2, 4]], [[2, 5], [9, 12]]]) == [
        [5, 6], [7, 9]]
    assert get_skyline([[2, 9, 10], [3, 7, 15], [5, 12, 12], [15, 20, 10], [19, 24, 8]]) == [
        [2, 10], [3, 15], [7, 12], [12, 0], [15, 10], [20, 8], [24, 0]]
    assert get_skyline([[0, 2, 3], [2, 5, 3]]) == [[0, 3], [5, 0]]  # no dup at x=2


def test_rooms_and_busiest_match_timeline():
    import random

    rng = random.Random(1)
    for _ in range(500):
        iv = _rand_intervals(rng, rng.randint(0, 8))
        line = _timeline(iv)
        peak = max(line.values(), default=0)
        assert min_meeting_rooms(iv) == peak
        when = min((t for t, c in line.items() if c == peak), default=None)
        assert busiest_time(iv) == (peak, when if peak else None)


def test_free_time_matches_timeline():
    import random

    rng = random.Random(2)
    for _ in range(500):
        schedule = [_rand_intervals(rng, rng.randint(1, 3)) for _ in range(rng.randint(1, 4))]
        line = _timeline([iv for p in schedule for iv in p])
        free = [t for t, c in line.items() if c == 0]
        gaps = []
        for t in free:                                            # runs of free cells
            if gaps and gaps[-1][1] == t:
                gaps[-1][1] = t + 1
            else:
                gaps.append([t, t + 1])
        assert employee_free_time(schedule) == gaps


def test_skyline_matches_height_scan():
    import random

    rng = random.Random(3)
    for _ in range(500):
        bs = []
        for _ in range(rng.randint(1, 6)):
            l = rng.randint(0, 15)
            bs.append([l, l + rng.randint(1, 6), rng.randint(1, 5)])
        brute, prev = [], 0
        for x in range(min(b[0] for b in bs), max(b[1] for b in bs) + 1):
            h = max((hh for l, r, hh in bs if l <= x < r), default=0)
            if h != prev:
                brute.append([x, h])
                prev = h
        assert get_skyline(bs) == brute


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
