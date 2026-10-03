"""Heap basics — heapq idioms and a hand-rolled binary heap.

Signs: "repeatedly take the smallest/largest", a priority queue, "process in
       order of cost/time", anything that needs min and insert interleaved.
Approach: a binary heap is a complete tree stored in a list: children of i
          are 2i+1 and 2i+2, parent is (i-1)//2. Every parent <= its children,
          so the min sits at index 0. Push = append + sift up; pop = move the
          last item to the root + sift down. heapq does exactly this.
Complexity: push/pop O(log n), peek O(1), heapify O(n) (not n log n — most
            nodes are near the bottom and sift only a little).
Gotchas:
  - heapq is min-only. Max-heap: push -x and negate on the way out. For
    tuples, negate the key field: (-priority, ...).
  - Tuples compare field by field. If two keys tie, Python compares the next
    field — a dict or custom object there raises TypeError. Put a counter in
    between: (key, seq, payload).
  - heap[0] is the min, but heap[1] is *not* the second smallest in general.
  - Changing an item's key in place breaks the heap. Re-heapify, or push the
    new version and skip stale ones on pop (see lazy_deletion.py).

Run the tests at the bottom with:  python3 stacks_heaps/heap_basics.py
"""

import heapq
from itertools import count


# ---------------------------------------------------------------- implementation


class BinaryHeap:
    """Min-heap with an optional key function, equivalent to heapq."""

    def __init__(self, items=(), key=lambda x: x):
        self.key = key
        self.a = list(items)
        for i in range(len(self.a) // 2 - 1, -1, -1):  # heapify: O(n)
            self._sift_down(i)

    def __len__(self):
        return len(self.a)

    def push(self, x):
        self.a.append(x)
        self._sift_up(len(self.a) - 1)

    def peek(self):
        return self.a[0]

    def pop(self):
        last = self.a.pop()
        if not self.a:
            return last
        top, self.a[0] = self.a[0], last
        self._sift_down(0)
        return top

    def _sift_up(self, i):
        a, key = self.a, self.key
        while i > 0:
            p = (i - 1) // 2
            if key(a[i]) >= key(a[p]):
                break
            a[i], a[p] = a[p], a[i]
            i = p

    def _sift_down(self, i):
        a, key, n = self.a, self.key, len(self.a)
        while True:
            smallest = i
            for c in (2 * i + 1, 2 * i + 2):
                if c < n and key(a[c]) < key(a[smallest]):
                    smallest = c
            if smallest == i:
                return
            a[i], a[smallest] = a[smallest], a[i]
            i = smallest

    def is_valid(self):
        return all(self.key(self.a[(i - 1) // 2]) <= self.key(self.a[i]) for i in range(1, len(self.a)))


def heap_sort(xs):
    """Ascending sort by heapify + n pops: O(n log n), not stable."""
    h = list(xs)
    heapq.heapify(h)
    return [heapq.heappop(h) for _ in range(len(h))]


class MaxHeap:
    """heapq with negated keys — the standard max-heap idiom."""

    def __init__(self):
        self.h = []

    def push(self, x):
        heapq.heappush(self.h, -x)

    def pop(self):
        return -heapq.heappop(self.h)

    def peek(self):
        return -self.h[0]

    def __len__(self):
        return len(self.h)


class TaskQueue:
    """Priority queue of arbitrary payloads; FIFO among equal priorities.

    The counter breaks ties before Python ever compares two payloads, and it
    makes equal priorities come out in insertion order.
    """

    def __init__(self):
        self.h = []
        self.seq = count()

    def push(self, priority, payload):
        heapq.heappush(self.h, (priority, next(self.seq), payload))

    def pop(self):
        priority, _, payload = heapq.heappop(self.h)
        return priority, payload

    def __len__(self):
        return len(self.h)


# ------------------------------------------------------------------------ tests


def test_heapify_builds_a_valid_heap():
    import random

    rng = random.Random(1)
    for _ in range(300):
        xs = [rng.randint(0, 20) for _ in range(rng.randint(0, 30))]
        h = BinaryHeap(xs)
        assert h.is_valid()
        assert sorted(h.a) == sorted(xs)


def test_binary_heap_matches_heapq():
    import random

    rng = random.Random(2)
    mine, ref = BinaryHeap(), []
    for _ in range(5000):
        if ref and rng.random() < 0.45:
            assert mine.pop() == heapq.heappop(ref)
        else:
            x = rng.randint(-50, 50)
            mine.push(x)
            heapq.heappush(ref, x)
        assert len(mine) == len(ref)
        if ref:
            assert mine.peek() == ref[0]
    assert mine.is_valid()


def test_binary_heap_with_key():
    words = ["pear", "fig", "banana", "kiwi", "apple"]
    h = BinaryHeap(words, key=len)
    lengths = [len(h.pop()) for _ in range(len(words))]
    assert lengths == sorted(lengths)


def test_heap_sort():
    import random

    rng = random.Random(3)
    for _ in range(300):
        xs = [rng.randint(-9, 9) for _ in range(rng.randint(0, 25))]
        assert heap_sort(xs) == sorted(xs)


def test_max_heap_via_negation():
    import random

    rng = random.Random(4)
    h, ref = MaxHeap(), []
    for _ in range(2000):
        if ref and rng.random() < 0.4:
            ref.remove(max(ref))
            h.pop()
        else:
            x = rng.randint(-20, 20)
            h.push(x)
            ref.append(x)
        if ref:
            assert h.peek() == max(ref)


def test_tiebreaker_avoids_comparing_payloads():
    try:
        heapq.heapify([(1, {"a": 1}), (1, {"b": 2})])  # ties fall through to dicts
        raised = False
    except TypeError:
        raised = True
    assert raised

    q = TaskQueue()
    q.push(2, {"job": "c"})
    q.push(1, {"job": "a"})
    q.push(2, {"job": "d"})
    q.push(1, {"job": "b"})
    assert [q.pop()[1]["job"] for _ in range(4)] == ["a", "b", "c", "d"]  # FIFO on ties


def test_heapq_helpers_agree_with_sorting():
    import random

    rng = random.Random(5)
    for _ in range(200):
        xs = [rng.randint(0, 50) for _ in range(rng.randint(0, 20))]
        k = rng.randint(0, len(xs))
        assert heapq.nsmallest(k, xs) == sorted(xs)[:k]
        assert heapq.nlargest(k, xs) == sorted(xs, reverse=True)[:k]
        runs = [sorted(rng.sample(range(100), 4)) for _ in range(3)]
        assert list(heapq.merge(*runs)) == sorted(sum(runs, []))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
