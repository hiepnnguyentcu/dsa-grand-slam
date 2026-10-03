"""Scheduling with heaps — greedy choices over time.

Signs: intervals competing for rooms/servers, a CPU picking the next job,
       cooldowns between equal tasks, "rearrange so no two equal items are
       adjacent", "minimum number of X needed at once".
Approach: sort events by start time and keep a heap of whatever matters next:
  - Meeting rooms: a min-heap of end times of rooms in use. If the earliest
    end is <= the new start, reuse that room (pop); always push the new end.
    The heap's peak size is the answer.
  - Reorganise / task scheduler: a max-heap of remaining counts. Always place
    the most plentiful item that is allowed right now; park used items until
    their cooldown passes.
  - Single-threaded CPU: push every task that has arrived by the current time
    into a heap keyed by (duration, index); if none has, jump the clock to the
    next arrival.
Complexity: O(n log n) for all of these (task scheduler O(total x log 26)).
Gotchas:
  - Meeting rooms: a meeting ending at t frees its room for one starting at t
    (<=, not <), unless the problem says otherwise.
  - Task scheduler has a closed form: max((maxc - 1) * (n + 1) + ties, total).
  - Reorganise is impossible iff some count > (len + 1) // 2.
  - CPU: when the heap is empty, jump time forward — don't tick one by one.

Run the tests at the bottom with:  python3 stacks_heaps/heap_scheduling.py
"""

import heapq
from collections import Counter, deque


# ---------------------------------------------------------------- implementation


def min_meeting_rooms(intervals):
    """Fewest rooms so no two overlapping [start, end) meetings share one."""
    ends = []
    for start, end in sorted(intervals):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)  # reuse the room that frees first
        else:
            heapq.heappush(ends, end)
    return len(ends)


def least_interval(tasks, n):
    """CPU slots to run all tasks when equal tasks need n slots between them.

    Simulation: a max-heap of remaining counts, plus a queue of tasks cooling
    down as (count_left, time_available_again).
    """
    heap = [-c for c in Counter(tasks).values()]
    heapq.heapify(heap)
    cooling = deque()
    time = 0
    while heap or cooling:
        time += 1
        if heap:
            left = heapq.heappop(heap) + 1  # negated count, one fewer
            if left:
                cooling.append((left, time + n))
        elif cooling:
            time = cooling[0][1]  # idle: jump to the next task ready
        if cooling and cooling[0][1] == time:
            heapq.heappush(heap, cooling.popleft()[0])
    return time


def least_interval_formula(tasks, n):
    """Closed form: the most frequent task sets the frame."""
    counts = Counter(tasks).values()
    maxc = max(counts)
    ties = sum(1 for c in counts if c == maxc)
    return max((maxc - 1) * (n + 1) + ties, len(tasks))


def reorganize_string(s):
    """A rearrangement of s with no two equal adjacent chars, or ""."""
    heap = [(-c, ch) for ch, c in Counter(s).items()]
    heapq.heapify(heap)
    out = []
    held = None  # the char just used: unavailable for exactly one step
    while heap:
        c, ch = heapq.heappop(heap)
        out.append(ch)
        if held:
            heapq.heappush(heap, held)
        held = (c + 1, ch) if c + 1 else None
    return "".join(out) if len(out) == len(s) else ""


def cpu_order(tasks):
    """Single-threaded CPU: tasks[i] = (enqueue_time, duration).

    When idle, run the available task with the shortest duration (ties: lower
    index). Returns the order of indices.
    """
    order = sorted(range(len(tasks)), key=lambda i: tasks[i][0])
    ready = []
    time, i, out = 0, 0, []
    while len(out) < len(tasks):
        if not ready and time < tasks[order[i]][0]:
            time = tasks[order[i]][0]  # idle: jump to the next arrival
        while i < len(order) and tasks[order[i]][0] <= time:
            heapq.heappush(ready, (tasks[order[i]][1], order[i]))
            i += 1
        dur, idx = heapq.heappop(ready)
        time += dur
        out.append(idx)
    return out


# ------------------------------------------------------------------------ tests


def brute_rooms(intervals):
    """Peak number of meetings live at any instant (half-open)."""
    points = {s for s, _ in intervals}
    return max((sum(1 for s, e in intervals if s <= t < e) for t in points), default=0)


def test_meeting_rooms():
    import random

    assert min_meeting_rooms([(0, 30), (5, 10), (15, 20)]) == 2
    assert min_meeting_rooms([(7, 10), (2, 4)]) == 1
    assert min_meeting_rooms([(1, 5), (5, 10)]) == 1  # back to back
    assert min_meeting_rooms([]) == 0
    rng = random.Random(1)
    for _ in range(1000):
        iv = []
        for _ in range(rng.randint(0, 8)):
            s = rng.randint(0, 15)
            iv.append((s, s + rng.randint(1, 6)))
        assert min_meeting_rooms(iv) == brute_rooms(iv), iv


def test_task_scheduler():
    import random

    assert least_interval(list("AAABBB"), 2) == 8
    assert least_interval(list("ACABDB"), 1) == 6
    assert least_interval(list("AAABBB"), 3) == 10
    assert least_interval(list("AAAAAABCDEFG"), 2) == 16
    rng = random.Random(2)
    for _ in range(1000):
        tasks = [rng.choice("ABCDE") for _ in range(rng.randint(1, 14))]
        n = rng.randint(0, 4)
        assert least_interval(tasks, n) == least_interval_formula(tasks, n), (tasks, n)


def test_reorganize_string():
    import random
    from itertools import permutations

    assert reorganize_string("aaab") == ""
    out = reorganize_string("aab")
    assert out == "aba"
    rng = random.Random(3)
    for _ in range(400):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 7)))
        out = reorganize_string(s)
        possible = any(all(p[i] != p[i + 1] for i in range(len(p) - 1)) for p in set(permutations(s)))
        if possible:
            assert sorted(out) == sorted(s)
            assert all(out[i] != out[i + 1] for i in range(len(out) - 1)), (s, out)
        else:
            assert out == "", s


def brute_cpu_order(tasks):
    """Tick-free replay: scan every waiting task each time the CPU frees."""
    left = set(range(len(tasks)))
    time, out = 0, []
    while left:
        avail = [i for i in left if tasks[i][0] <= time]
        if not avail:
            time = min(tasks[i][0] for i in left)
            continue
        i = min(avail, key=lambda j: (tasks[j][1], j))
        time += tasks[i][1]
        out.append(i)
        left.remove(i)
    return out


def test_cpu_order():
    import random

    assert cpu_order([(1, 2), (2, 4), (3, 2), (4, 1)]) == [0, 2, 3, 1]
    assert cpu_order([(7, 10), (7, 12), (7, 5), (7, 4), (7, 2)]) == [4, 3, 2, 0, 1]
    rng = random.Random(4)
    for _ in range(800):
        tasks = [(rng.randint(0, 12), rng.randint(1, 4)) for _ in range(rng.randint(1, 8))]
        assert cpu_order(tasks) == brute_cpu_order(tasks), tasks


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
