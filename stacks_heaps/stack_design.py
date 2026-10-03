"""Stack design — min stack, queue from stacks, stack from a queue, freq stack.

Signs: "design a stack that supports getMin in O(1)", "implement a queue using
       stacks", "pop the most frequent element".
Approach:
  - MinStack: store (value, min so far) per entry. The min below an entry
    never changes while that entry exists, so it can be cached with it.
  - Queue via two stacks: push onto `inbox`; pop from `outbox`, refilling it
    by reversing `inbox` only when `outbox` is empty.
  - Stack via one queue: after each push, rotate the older items behind it.
  - FreqStack: a stack per frequency level. An element pushed for the k-th
    time goes on stack k; pop takes from the highest non-empty level.
Complexity: MinStack and FreqStack O(1) per op. Queue O(1) amortised — each
            item moves inbox -> outbox once. Stack-via-queue push O(n).
Gotchas:
  - Queue: never move items while `outbox` still has some, or order breaks.
  - MinStack with a separate min-stack: push onto it on <=, not <, or popping
    a duplicate minimum loses it.
  - FreqStack: an element lives on every level up to its count; popping only
    removes its top copy.

Run the tests at the bottom with:  python3 stacks_heaps/stack_design.py
"""

from collections import defaultdict, deque


# ---------------------------------------------------------------- implementation


class MinStack:
    def __init__(self):
        self.items = []  # (value, min of this and everything below)

    def push(self, x):
        self.items.append((x, min(x, self.items[-1][1]) if self.items else x))

    def pop(self):
        return self.items.pop()[0]

    def top(self):
        return self.items[-1][0]

    def get_min(self):
        return self.items[-1][1]


class MyQueue:
    def __init__(self):
        self.inbox, self.outbox = [], []

    def push(self, x):
        self.inbox.append(x)

    def _shift(self):
        if not self.outbox:  # only when empty, or FIFO order breaks
            while self.inbox:
                self.outbox.append(self.inbox.pop())

    def pop(self):
        self._shift()
        return self.outbox.pop()

    def peek(self):
        self._shift()
        return self.outbox[-1]

    def empty(self):
        return not self.inbox and not self.outbox


class MyStack:
    def __init__(self):
        self.q = deque()

    def push(self, x):
        self.q.append(x)
        for _ in range(len(self.q) - 1):  # rotate so x is at the front
            self.q.append(self.q.popleft())

    def pop(self):
        return self.q.popleft()

    def top(self):
        return self.q[0]

    def empty(self):
        return not self.q


class FreqStack:
    """pop() removes the most frequent value; ties go to the most recent."""

    def __init__(self):
        self.freq = defaultdict(int)
        self.levels = defaultdict(list)  # count -> values pushed at that count
        self.max_freq = 0

    def push(self, x):
        self.freq[x] += 1
        f = self.freq[x]
        self.max_freq = max(self.max_freq, f)
        self.levels[f].append(x)

    def pop(self):
        x = self.levels[self.max_freq].pop()
        self.freq[x] -= 1
        if not self.levels[self.max_freq]:
            self.max_freq -= 1
        return x


# ------------------------------------------------------------------------ tests


def test_min_stack_example():
    s = MinStack()
    for x in (-2, 0, -3):
        s.push(x)
    assert s.get_min() == -3
    s.pop()
    assert s.top() == 0
    assert s.get_min() == -2


def test_min_stack_matches_list():
    import random

    rng = random.Random(1)
    s, ref = MinStack(), []
    for _ in range(5000):
        if ref and rng.random() < 0.45:
            assert s.pop() == ref.pop()
        else:
            x = rng.randint(-5, 5)  # duplicates of the minimum are the trap
            s.push(x)
            ref.append(x)
        if ref:
            assert s.top() == ref[-1]
            assert s.get_min() == min(ref)


def test_queue_via_stacks_matches_deque():
    import random

    rng = random.Random(2)
    q, ref = MyQueue(), deque()
    for _ in range(5000):
        r = rng.random()
        if ref and r < 0.3:
            assert q.pop() == ref.popleft()
        elif ref and r < 0.45:
            assert q.peek() == ref[0]
        else:
            x = rng.randint(0, 99)
            q.push(x)
            ref.append(x)
        assert q.empty() == (not ref)


def test_stack_via_queue_matches_list():
    import random

    rng = random.Random(3)
    s, ref = MyStack(), []
    for _ in range(2000):
        if ref and rng.random() < 0.4:
            assert s.pop() == ref.pop()
        else:
            x = rng.randint(0, 99)
            s.push(x)
            ref.append(x)
        assert s.empty() == (not ref)
        if ref:
            assert s.top() == ref[-1]


def test_freq_stack_example():
    s = FreqStack()
    for x in (5, 7, 5, 7, 4, 5):
        s.push(x)
    assert [s.pop() for _ in range(4)] == [5, 7, 5, 4]


def test_freq_stack_matches_brute_force():
    import random

    rng = random.Random(4)
    s, history = FreqStack(), []  # history: the live pushes, oldest first
    for _ in range(3000):
        if history and rng.random() < 0.4:
            counts = {}
            for x in history:
                counts[x] = counts.get(x, 0) + 1
            top = max(counts.values())
            # most recent push of any value having the top count
            k = max(i for i, x in enumerate(history) if counts[x] == top)
            expect = history.pop(k)
            assert s.pop() == expect
        else:
            x = rng.randint(0, 4)
            s.push(x)
            history.append(x)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
