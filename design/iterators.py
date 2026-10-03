"""Iterators — peeking, flatten nested list, zigzag over k lists, flatten 2D.

Signs: "implement next() and hasNext()", "peek without consuming", "flatten a
       nested list lazily", "alternate between vectors", "iterator over ...".
Approach:
  - Peeking: cache one element ahead. peek returns the cache; next returns it
    and refills from the inner iterator.
  - Nested list: a stack of (list, index) frames. has_next does the work: it
    walks until the top frame points at an integer, descending into sublists
    and popping finished frames. next just returns that integer.
  - Zigzag (k lists): a deque of (list, index). Take from the front, and put
    the pair back at the end only if that list still has elements.
  - 2D vector: (row, col) pointers; has_next skips empty rows.
  - BST iterator (left-spine stack): binary_search_trees/kth_and_iterator.py.
Complexity: O(1) amortised per call for all four. Nested: O(depth) stack.
Gotchas:
  - Put the skipping logic in has_next and have next call it. Then both
    calls in any order, repeated or not, stay correct.
  - Empty sublists ([[]], [[], [[]]]) are the classic bug: has_next must not
    report True just because a frame is left on the stack.
  - Do not flatten everything up front unless asked; "lazy" is the point and
    the follow-up usually says the input is huge or infinite.
  - Python iterators have no has_next: cache one element (sentinel object, not
    None — None can be a real value).

Run the tests at the bottom with:  python3 design/iterators.py
"""

from collections import deque


# ---------------------------------------------------------------- implementation


_END = object()


class PeekingIterator:
    """LC 284. Wraps any Python iterator."""

    def __init__(self, it):
        self.it = iter(it)
        self.nxt = next(self.it, _END)

    def peek(self):
        return self.nxt

    def next(self):
        val = self.nxt
        self.nxt = next(self.it, _END)
        return val

    def has_next(self):
        return self.nxt is not _END


class NestedIterator:
    """LC 341. Elements are ints or (possibly empty) lists of the same."""

    def __init__(self, nested):
        self.stack = [[nested, 0]]  # frames: [list, next index]

    def has_next(self):
        while self.stack:
            frame = self.stack[-1]
            lst, i = frame
            if i == len(lst):
                self.stack.pop()
            elif isinstance(lst[i], list):
                frame[1] += 1
                self.stack.append([lst[i], 0])
            else:
                return True
        return False

    def next(self):
        self.has_next()  # move to an integer if not already there
        frame = self.stack[-1]
        frame[1] += 1
        return frame[0][frame[1] - 1]


class ZigzagIterator:
    """LC 281, generalised to k lists: round-robin, skipping exhausted ones."""

    def __init__(self, *lists):
        self.q = deque((lst, 0) for lst in lists if lst)

    def next(self):
        lst, i = self.q.popleft()
        if i + 1 < len(lst):
            self.q.append((lst, i + 1))
        return lst[i]

    def has_next(self):
        return bool(self.q)


class Vector2D:
    """LC 251. Rows may be empty."""

    def __init__(self, vec):
        self.vec = vec
        self.r = self.c = 0

    def has_next(self):
        while self.r < len(self.vec) and self.c == len(self.vec[self.r]):
            self.r, self.c = self.r + 1, 0
        return self.r < len(self.vec)

    def next(self):
        self.has_next()
        self.c += 1
        return self.vec[self.r][self.c - 1]


# ------------------------------------------------------------------------ tests


def _drain(it, rng):
    """Pull everything, sprinkling extra has_next calls in random spots."""
    out = []
    while True:
        for _ in range(rng.randrange(3)):
            it.has_next()
        if not it.has_next():
            return out
        out.append(it.next())


def _flatten(x):
    return [y for e in x for y in (_flatten(e) if isinstance(e, list) else [e])]


def _random_nested(rng, depth):
    out = []
    for _ in range(rng.randrange(4)):
        if depth and rng.random() < 0.4:
            out.append(_random_nested(rng, depth - 1))
        else:
            out.append(rng.randrange(100))
    return out


def test_peeking_example():
    p = PeekingIterator([1, 2, 3])
    assert p.next() == 1 and p.peek() == 2 and p.next() == 2
    assert p.next() == 3 and not p.has_next()


def test_peeking_matches_list_with_none_values():
    import random

    rng = random.Random(1)
    for _ in range(300):
        xs = [rng.choice([None, 0, 1, 2]) for _ in range(rng.randrange(8))]
        p, i = PeekingIterator(xs), 0
        while i < len(xs):
            assert p.has_next() and p.peek() == xs[i]
            if rng.random() < 0.6:
                assert p.next() == xs[i]
                i += 1
        assert not p.has_next()


def test_nested_example():
    import random

    rng = random.Random(0)
    assert _drain(NestedIterator([[1, 1], 2, [1, 1]]), rng) == [1, 1, 2, 1, 1]
    assert _drain(NestedIterator([1, [4, [6]]]), rng) == [1, 4, 6]


def test_nested_empty_lists():
    import random

    rng = random.Random(2)
    for case in ([], [[]], [[], [[]]], [[], 3, [[[]]], [], 4]):
        assert _drain(NestedIterator(case), rng) == _flatten(case)


def test_nested_matches_recursive_flatten():
    import random

    rng = random.Random(3)
    for _ in range(2000):
        x = _random_nested(rng, 4)
        assert _drain(NestedIterator(x), rng) == _flatten(x)


def test_nested_deep_has_no_recursion_limit():
    x = [7]
    for _ in range(50_000):  # recursion would die at ~1000
        x = [x, []]
    it = NestedIterator(x)
    assert it.has_next() and it.next() == 7 and not it.has_next()


def test_zigzag_example():
    import random

    rng = random.Random(0)
    assert _drain(ZigzagIterator([1, 2], [3, 4, 5, 6]), rng) == [1, 3, 2, 4, 5, 6]
    assert _drain(ZigzagIterator([1, 2, 3], [4, 5, 6, 7], [8, 9]), rng) == [1, 4, 8, 2, 5, 9, 3, 6, 7]


def test_zigzag_matches_round_robin():
    import random

    rng = random.Random(4)
    for _ in range(1000):
        lists = [[rng.randrange(9) for _ in range(rng.randrange(5))] for _ in range(rng.randrange(1, 5))]
        expect = [lst[i] for i in range(max(map(len, lists))) for lst in lists if i < len(lst)]
        assert _drain(ZigzagIterator(*lists), rng) == expect


def test_vector2d_matches_flatten():
    import random

    rng = random.Random(5)
    for _ in range(1000):
        vec = [[rng.randrange(9) for _ in range(rng.choice([0, 0, 1, 3]))] for _ in range(rng.randrange(6))]
        assert _drain(Vector2D(vec), rng) == [x for row in vec for x in row]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
