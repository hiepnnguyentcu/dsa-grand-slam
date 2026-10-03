"""Sorted disjoint intervals as a data structure — Range Module, data stream.

Signs: add / remove / query ranges online, "track which numbers are covered",
       "return the stream so far as disjoint intervals", the set must stay
       merged after every update.
Approach: keep the intervals sorted and disjoint at all times; bisect to the
          affected stretch and splice it.
  - RangeModule: store the boundaries as one flat sorted list
    [s0, e0, s1, e1, ...]. A position's index parity says if it is inside:
    odd insertion index = inside a range. add/remove replace the boundaries
    in [left, right] with at most two new ones.
  - SummaryRanges: parallel starts/ends lists. A new value either sits inside
    an interval, extends one neighbour, bridges two, or stands alone.
Complexity: O(log n) to find, O(n) for the list splice (fine in interviews;
            a balanced BST or sortedcontainers gives O(log n)). Query O(log n).
Gotchas:
  - RangeModule is half-open [left, right): adding [1, 5) then [5, 7) gives
    [1, 7). bisect_left vs bisect_right is what makes touching merge.
  - SummaryRanges is closed integers: 3 joins [1, 2] and [4, 6] into [1, 6].
  - Duplicates in the stream must be no-ops.
  - Many intervals, few queries: just append and merge on read (merging.py).

Run the tests at the bottom with:  python3 intervals/interval_set.py
"""

from bisect import bisect_left, bisect_right


# ---------------------------------------------------------------- implementation


class RangeModule:
    """LC 715. Half-open ranges; boundaries kept as one flat sorted list."""

    def __init__(self):
        self.b = []                            # even index = start, odd = end

    def add_range(self, left, right):
        i, j = bisect_left(self.b, left), bisect_right(self.b, right)
        # keep `left` only if it lands outside a range (even); same for `right`
        self.b[i:j] = [left] * (i % 2 == 0) + [right] * (j % 2 == 0)

    def remove_range(self, left, right):
        i, j = bisect_left(self.b, left), bisect_right(self.b, right)
        # cut points survive only where they land inside a range (odd)
        self.b[i:j] = [left] * (i % 2 == 1) + [right] * (j % 2 == 1)

    def query_range(self, left, right):
        i, j = bisect_right(self.b, left), bisect_left(self.b, right)
        return i == j and i % 2 == 1           # both ends inside the same range

    def intervals(self):
        return [[self.b[k], self.b[k + 1]] for k in range(0, len(self.b), 2)]


class SummaryRanges:
    """LC 352. Integers arrive; keep closed disjoint [lo, hi] runs."""

    def __init__(self):
        self.starts, self.ends = [], []

    def add_num(self, v):
        i = bisect_right(self.starts, v)       # first interval starting after v
        if i > 0 and self.ends[i - 1] >= v:    # already covered
            return
        join_left = i > 0 and self.ends[i - 1] == v - 1
        join_right = i < len(self.starts) and self.starts[i] == v + 1
        if join_left and join_right:           # bridge two intervals
            self.ends[i - 1] = self.ends[i]
            del self.starts[i], self.ends[i]
        elif join_left:
            self.ends[i - 1] = v
        elif join_right:
            self.starts[i] = v
        else:
            self.starts.insert(i, v)
            self.ends.insert(i, v)

    def get_intervals(self):
        return [[s, e] for s, e in zip(self.starts, self.ends)]


# ------------------------------------------------------------------------ tests


def _runs(cells, closed):
    """Sorted covered ints -> intervals. Half-open cells t cover [t, t+1)."""
    out = []
    for x in sorted(cells):
        if out and x == out[-1][1] + (1 if closed else 0):
            out[-1][1] = x if closed else x + 1
        else:
            out.append([x, x] if closed else [x, x + 1])
    return out


def test_examples():
    rm = RangeModule()
    rm.add_range(10, 20)
    rm.remove_range(14, 16)
    assert [rm.query_range(10, 14), rm.query_range(13, 15), rm.query_range(16, 17)] == [
        True, False, True]
    rm.add_range(20, 25)                                           # touching merges
    assert rm.intervals() == [[10, 14], [16, 25]]
    sr = SummaryRanges()
    seen = []
    for v in [1, 3, 7, 2, 6]:
        sr.add_num(v)
        seen.append(sr.get_intervals())
    assert seen[-1] == [[1, 3], [6, 7]]
    assert seen[2] == [[1, 1], [3, 3], [7, 7]]


def test_range_module_matches_cells():
    import random

    rng = random.Random(1)
    for _ in range(300):
        rm, cells = RangeModule(), set()
        for _ in range(rng.randint(1, 15)):
            a = rng.randint(0, 25)
            b = a + rng.randint(1, 8)
            op = rng.randrange(3)
            if op == 0:
                rm.add_range(a, b)
                cells |= set(range(a, b))
            elif op == 1:
                rm.remove_range(a, b)
                cells -= set(range(a, b))
            else:
                assert rm.query_range(a, b) == (set(range(a, b)) <= cells)
            assert rm.intervals() == _runs(cells, closed=False)


def test_summary_ranges_matches_set():
    import random

    rng = random.Random(2)
    for _ in range(300):
        sr, seen = SummaryRanges(), set()
        for _ in range(rng.randint(1, 20)):
            v = rng.randint(0, 20)
            sr.add_num(v)
            seen.add(v)
            assert sr.get_intervals() == _runs(seen, closed=True)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
