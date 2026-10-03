"""Reachability — track the furthest point reachable so far.

Signs: "can you reach the end", "minimum jumps", "fewest clips / taps /
       intervals to cover [0, T]", each position lets you extend a range.
Approach: sweep left to right keeping `reach` = furthest index reachable.
  - Can reach: fail as soon as i > reach.
  - Fewest steps: BFS in levels without a queue. [start, end] is the window
    reachable with k steps; scan it, record the furthest next reach, and when
    i hits `end` take one more step (end = furthest). Stays ahead: after k
    steps no strategy reaches further than greedy's `end`.
  - Covering [0, T] with intervals: for every left point keep the furthest
    right end (best[l]); then it is exactly jump game II over best[].
Complexity: O(n) time; covering is O(n + T) with the best[] array.
Gotchas:
  - Jump game II: loop to n - 2, not n - 1 — standing on the last index must
    not trigger another jump.
  - Covering: if `furthest <= i` when you must step, there is a gap -> -1.
  - Taps: tap i covers [i - r, i + r]; clamp the left end to 0.
  - Video stitching covers a *continuous* [0, T]: touching ends (1-3, 3-5)
    count as covering.

Run the tests at the bottom with:  python3 greedy/reachability.py
"""

import random
from itertools import combinations


# ---------------------------------------------------------------- implementation


def can_jump(nums):
    """From index 0, nums[i] = max jump length. Can you reach the last index?"""
    reach = 0
    for i, x in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + x)
    return True


def min_jumps(nums):
    """Fewest jumps to reach the last index, or -1 if impossible."""
    jumps = end = furthest = 0
    for i in range(len(nums) - 1):
        furthest = max(furthest, i + nums[i])
        if i == end:          # window of `jumps` steps used up
            if furthest <= i:
                return -1     # stuck: nothing reaches past i
            jumps += 1
            end = furthest
    return jumps


def _cover(best, T):
    """Jump game II over best[l] = furthest right end starting at or before l."""
    steps = end = furthest = 0
    for i in range(T):
        furthest = max(furthest, best[i])
        if i == end:
            if furthest <= i:
                return -1
            steps += 1
            end = furthest
    return steps


def video_stitching(clips, T):
    """Fewest clips [s, e] whose union covers [0, T], or -1."""
    best = [0] * (T + 1)
    for s, e in clips:
        if s < T:
            best[s] = max(best[s], min(e, T))
    return _cover(best, T)


def min_taps(n, ranges):
    """Garden [0, n]; tap i at position i waters [i - r, i + r]. Fewest taps, or -1."""
    best = [0] * (n + 1)
    for i, r in enumerate(ranges):
        lo, hi = max(0, i - r), min(n, i + r)
        best[lo] = max(best[lo], hi)
    return _cover(best, n)


# ------------------------------------------------------------------------ tests


def dp_jumps(nums):
    """dp[i] = fewest jumps to reach i (O(n^2))."""
    INF = float("inf")
    dp = [0] + [INF] * (len(nums) - 1)
    for i in range(len(nums)):
        for j in range(i + 1, min(len(nums), i + nums[i] + 1)):
            dp[j] = min(dp[j], dp[i] + 1)
    return dp[-1] if dp[-1] < INF else -1


def covers(intervals, T):
    reach = 0
    for s, e in sorted(intervals):
        if s > reach:
            break
        reach = max(reach, e)
    return reach >= T


def brute_cover(intervals, T):
    for k in range(len(intervals) + 1):
        for chosen in combinations(intervals, k):
            if covers(chosen, T):
                return k
    return -1


def test_can_jump_examples():
    assert can_jump([2, 3, 1, 1, 4])
    assert not can_jump([3, 2, 1, 0, 4])
    assert can_jump([0])


def test_min_jumps_examples():
    assert min_jumps([2, 3, 1, 1, 4]) == 2
    assert min_jumps([0]) == 0
    assert min_jumps([1, 0, 1]) == -1


def test_jumps_match_dp():
    random.seed(4)
    for _ in range(400):
        nums = [random.randint(0, 3) for _ in range(random.randint(1, 10))]
        expected = dp_jumps(nums)
        assert min_jumps(nums) == expected
        assert can_jump(nums) == (expected != -1)


def test_video_stitching_examples():
    clips = [[0, 2], [4, 6], [8, 10], [1, 9], [1, 5], [5, 9]]
    assert video_stitching(clips, 10) == 3
    assert video_stitching([[0, 1], [1, 2]], 5) == -1
    assert video_stitching([[0, 5]], 0) == 0


def test_video_stitching_matches_brute_force():
    random.seed(5)
    for _ in range(300):
        T = random.randint(1, 10)
        clips = []
        for _ in range(random.randint(1, 7)):
            s = random.randint(0, 10)
            clips.append([s, s + random.randint(0, 5)])
        assert video_stitching(clips, T) == brute_cover([tuple(c) for c in clips], T)


def test_min_taps_examples():
    assert min_taps(5, [3, 4, 1, 1, 0, 0]) == 1
    assert min_taps(3, [0, 0, 0, 0]) == -1


def test_min_taps_matches_brute_force():
    random.seed(6)
    for _ in range(300):
        n = random.randint(1, 7)
        ranges = [random.randint(0, 3) for _ in range(n + 1)]
        intervals = [(max(0, i - r), min(n, i + r)) for i, r in enumerate(ranges)]
        assert min_taps(n, ranges) == brute_cover(intervals, n)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
