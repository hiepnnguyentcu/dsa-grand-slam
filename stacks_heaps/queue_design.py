"""Queue design — ring buffers, a circular deque, time windows, moving average.

Signs: "design a circular queue/deque of capacity k", "count requests in the
       last 3000 ms", "average of the last n values", any fixed-size FIFO.
Approach:
  - Ring buffer: a list of size k, a `head` index and a `count`. The tail is
    (head + count) % k, so nothing ever shifts — indices wrap instead.
  - Circular deque: same buffer; push-front steps head back one, mod k.
  - Time window: append each timestamp, pop from the left while it has fallen
    out of the window. Timestamps arrive sorted, so the stale ones are in front.
  - Moving average: deque plus a running sum; add the new value, subtract the
    one that falls off.
Complexity: O(1) per op (window counter O(1) amortised — each ping leaves once).
Gotchas:
  - Track `count`, not just head and tail: with head == tail alone you cannot
    tell empty from full.
  - Python's `%` is non-negative, so (head - 1) % k wraps correctly; in C/Java
    write (head - 1 + k) % k.
  - In Python, `collections.deque` is the queue. `list.pop(0)` is O(n).

Run the tests at the bottom with:  python3 stacks_heaps/queue_design.py
"""

from collections import deque


# ---------------------------------------------------------------- implementation


class CircularQueue:
    """LC 622. Fixed capacity FIFO; -1 means empty, like the LeetCode API."""

    def __init__(self, k):
        self.buf = [0] * k
        self.k = k
        self.head = 0
        self.count = 0

    def enqueue(self, x):
        if self.count == self.k:
            return False
        self.buf[(self.head + self.count) % self.k] = x
        self.count += 1
        return True

    def dequeue(self):
        if self.count == 0:
            return False
        self.head = (self.head + 1) % self.k
        self.count -= 1
        return True

    def front(self):
        return self.buf[self.head] if self.count else -1

    def rear(self):
        return self.buf[(self.head + self.count - 1) % self.k] if self.count else -1

    def is_empty(self):
        return self.count == 0

    def is_full(self):
        return self.count == self.k


class CircularDeque:
    """LC 641. Ring buffer that grows at either end."""

    def __init__(self, k):
        self.buf = [0] * k
        self.k = k
        self.head = 0
        self.count = 0

    def insert_front(self, x):
        if self.count == self.k:
            return False
        self.head = (self.head - 1) % self.k  # Python % wraps to k-1
        self.buf[self.head] = x
        self.count += 1
        return True

    def insert_last(self, x):
        if self.count == self.k:
            return False
        self.buf[(self.head + self.count) % self.k] = x
        self.count += 1
        return True

    def delete_front(self):
        if self.count == 0:
            return False
        self.head = (self.head + 1) % self.k
        self.count -= 1
        return True

    def delete_last(self):
        if self.count == 0:
            return False
        self.count -= 1
        return True

    def get_front(self):
        return self.buf[self.head] if self.count else -1

    def get_rear(self):
        return self.buf[(self.head + self.count - 1) % self.k] if self.count else -1


class RecentCounter:
    """LC 933. Pings in [t - window, t]; timestamps strictly increase."""

    def __init__(self, window=3000):
        self.window = window
        self.q = deque()

    def ping(self, t):
        self.q.append(t)
        while self.q[0] < t - self.window:
            self.q.popleft()
        return len(self.q)


class MovingAverage:
    """LC 346. Mean of the last `size` values."""

    def __init__(self, size):
        self.size = size
        self.q = deque()
        self.total = 0

    def next(self, x):
        self.q.append(x)
        self.total += x
        if len(self.q) > self.size:
            self.total -= self.q.popleft()
        return self.total / len(self.q)


# ------------------------------------------------------------------------ tests


def test_circular_queue_example():
    q = CircularQueue(3)
    assert [q.enqueue(x) for x in (1, 2, 3, 4)] == [True, True, True, False]
    assert q.rear() == 3 and q.is_full()
    assert q.dequeue() and q.enqueue(4)
    assert q.rear() == 4 and q.front() == 2


def test_circular_queue_matches_deque():
    import random

    rng = random.Random(11)
    for k in (1, 2, 5):
        q, ref = CircularQueue(k), deque()
        for _ in range(3000):
            r = rng.random()
            if r < 0.45:
                x = rng.randint(0, 99)
                ok = len(ref) < k
                assert q.enqueue(x) == ok
                if ok:
                    ref.append(x)
            elif r < 0.8:
                assert q.dequeue() == bool(ref)
                if ref:
                    ref.popleft()
            assert q.front() == (ref[0] if ref else -1)
            assert q.rear() == (ref[-1] if ref else -1)
            assert q.is_empty() == (not ref) and q.is_full() == (len(ref) == k)


def test_circular_deque_matches_deque():
    import random

    rng = random.Random(12)
    for k in (1, 3, 6):
        d, ref = CircularDeque(k), deque()
        for _ in range(4000):
            op = rng.randrange(4)
            x = rng.randint(0, 99)
            if op == 0:
                ok = len(ref) < k
                assert d.insert_front(x) == ok
                if ok:
                    ref.appendleft(x)
            elif op == 1:
                ok = len(ref) < k
                assert d.insert_last(x) == ok
                if ok:
                    ref.append(x)
            elif op == 2:
                assert d.delete_front() == bool(ref)
                if ref:
                    ref.popleft()
            else:
                assert d.delete_last() == bool(ref)
                if ref:
                    ref.pop()
            assert d.get_front() == (ref[0] if ref else -1)
            assert d.get_rear() == (ref[-1] if ref else -1)


def test_recent_counter():
    c = RecentCounter()
    assert [c.ping(t) for t in (1, 100, 3001, 3002)] == [1, 2, 3, 3]


def test_recent_counter_matches_brute_force():
    import random

    rng = random.Random(13)
    c, seen, t = RecentCounter(50), [], 0
    for _ in range(2000):
        t += rng.randint(1, 20)
        seen.append(t)
        assert c.ping(t) == sum(1 for s in seen if t - 50 <= s <= t)


def test_moving_average_matches_slice():
    import random

    rng = random.Random(14)
    for size in (1, 3, 7):
        m, xs = MovingAverage(size), []
        for _ in range(500):
            x = rng.randint(-50, 50)
            xs.append(x)
            window = xs[-size:]
            assert abs(m.next(x) - sum(window) / len(window)) < 1e-9


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
