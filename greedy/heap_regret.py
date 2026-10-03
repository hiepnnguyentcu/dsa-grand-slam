"""Greedy with regret — take everything, undo the worst choice with a heap.

Signs: "maximum number of courses before their deadlines", "fewest refuelling
       stops", "how far can you climb with B bricks and L ladders" — you can't
       know the right choice now, but you can fix it later.
Approach: commit greedily; when a constraint breaks, revoke the past choice
          that hurts most. A heap keeps that choice on top.
  - Course schedule III: sort by deadline, take each course, push its length
    on a max-heap. If time exceeds the deadline, drop the longest course so
    far. Exchange: swapping any taken course for a shorter one keeps the count
    and frees time.
  - Min refuel stops: drive; push every station you pass onto a max-heap of
    fuel. When you can't reach the next point, retroactively refuel at the
    biggest station passed. Stays ahead: after k stops greedy's range is max.
  - Furthest building: give every climb a ladder (min-heap of climbs); once
    ladders run out, the smallest laddered climb is paid with bricks instead.
Complexity: O(n log n) each.
Gotchas:
  - Course III: sort by deadline (end), not by duration.
  - Refuel: the target is the last "station" — loop over stations + [target].
  - Furthest building: drops (h[i+1] <= h[i]) cost nothing; skip them.
  - Related heap greedies (meeting rooms, task scheduler, CPU order):
    stacks_heaps/heap_scheduling.py.

Run the tests at the bottom with:  python3 greedy/heap_regret.py
"""

import heapq
import random
from functools import cache
from itertools import combinations


# ---------------------------------------------------------------- implementation


def schedule_course(courses):
    """courses = [(duration, last_day)]. Max courses taken one at a time."""
    heap, time = [], 0  # max-heap of durations (negated)
    for d, last in sorted(courses, key=lambda c: c[1]):
        time += d
        heapq.heappush(heap, -d)
        if time > last:
            time += heapq.heappop(heap)  # drop the longest so far
    return len(heap)


def min_refuel_stops(target, fuel, stations):
    """stations = [(position, fuel)] sorted by position. Fewest stops, or -1."""
    heap, stops, i = [], 0, 0  # max-heap of fuel at stations passed
    while fuel < target:
        while i < len(stations) and stations[i][0] <= fuel:
            heapq.heappush(heap, -stations[i][1])
            i += 1
        if not heap:
            return -1
        fuel -= heapq.heappop(heap)  # refuel at the best station behind us
        stops += 1
    return stops


def furthest_building(heights, bricks, ladders):
    """Index of the furthest building reachable."""
    heap = []  # min-heap of climbs currently using ladders
    for i in range(len(heights) - 1):
        climb = heights[i + 1] - heights[i]
        if climb <= 0:
            continue
        heapq.heappush(heap, climb)
        if len(heap) > ladders:
            bricks -= heapq.heappop(heap)  # smallest climb pays bricks
            if bricks < 0:
                return i
    return len(heights) - 1


# ------------------------------------------------------------------------ tests


def brute_courses(courses):
    for k in range(len(courses), -1, -1):
        for chosen in combinations(courses, k):
            t, ok = 0, True
            for d, last in sorted(chosen, key=lambda c: c[1]):  # EDF is optimal order
                t += d
                ok &= t <= last
            if ok:
                return k
    return 0


def brute_refuel(target, fuel, stations):
    for k in range(len(stations) + 1):
        for chosen in combinations(stations, k):
            reach, ok = fuel, True
            for pos, f in chosen:
                if pos > reach:
                    ok = False
                    break
                reach += f
            if ok and reach >= target:
                return k
    return -1


def brute_building(heights, bricks, ladders):
    @cache
    def go(i, b, l):
        if i == len(heights) - 1:
            return i
        climb = heights[i + 1] - heights[i]
        if climb <= 0:
            return go(i + 1, b, l)
        best = i
        if b >= climb:
            best = max(best, go(i + 1, b - climb, l))
        if l:
            best = max(best, go(i + 1, b, l - 1))
        return best

    return go(0, bricks, ladders)


def test_course_examples():
    assert schedule_course([(100, 200), (200, 1300), (1000, 1250), (2000, 3200)]) == 3
    assert schedule_course([(1, 2)]) == 1
    assert schedule_course([(3, 2), (4, 3)]) == 0


def test_course_matches_brute_force():
    random.seed(24)
    for _ in range(300):
        courses = [(random.randint(1, 5), random.randint(1, 12)) for _ in range(random.randint(0, 7))]
        assert schedule_course(courses) == brute_courses(courses)


def test_refuel_examples():
    assert min_refuel_stops(1, 1, []) == 0
    assert min_refuel_stops(100, 1, [(10, 100)]) == -1
    assert min_refuel_stops(100, 10, [(10, 60), (20, 30), (30, 30), (60, 40)]) == 2


def test_refuel_matches_brute_force():
    random.seed(25)
    for _ in range(300):
        target = random.randint(1, 30)
        positions = sorted(random.sample(range(1, target + 1), min(target, random.randint(0, 6))))
        stations = [(p, random.randint(1, 10)) for p in positions if p < target]
        fuel = random.randint(1, 12)
        assert min_refuel_stops(target, fuel, stations) == brute_refuel(target, fuel, stations)


def test_building_examples():
    assert furthest_building([4, 2, 7, 6, 9, 14, 12], 5, 1) == 4
    assert furthest_building([4, 12, 2, 7, 3, 18, 20, 3, 19], 10, 2) == 7
    assert furthest_building([14, 3, 19, 3], 17, 0) == 3


def test_building_matches_brute_force():
    random.seed(26)
    for _ in range(300):
        heights = [random.randint(1, 10) for _ in range(random.randint(1, 8))]
        bricks, ladders = random.randint(0, 10), random.randint(0, 2)
        assert furthest_building(heights, bricks, ladders) == brute_building(tuple(heights), bricks, ladders)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
