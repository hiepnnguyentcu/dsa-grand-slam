"""Online bookings — My Calendar I, II, III.

Signs: requests arrive one at a time, "book(start, end) returns true if it
       doesn't cause a double / triple booking", "after each booking return
       the max overlap so far".
Approach:
  - I (no overlap): keep bookings sorted by start. A new [s, e) can only
    clash with its two neighbours, found with bisect.
  - II (no triple): keep every booking plus every pairwise overlap. Reject if
    the new one hits an overlap; otherwise record its overlaps with bookings.
  - III (max k): a sorted map of +1/-1 deltas; insert two keys and sweep.
Complexity: I O(log n) search + O(n) list insert (a balanced BST or
            sortedcontainers makes it O(log n)). II O(n) per book.
            III O(n) per book; a segment tree with lazy max gets O(log C).
Gotchas:
  - Half-open [s, e): book(10, 20) then book(20, 30) is fine.
  - Two intervals overlap iff max(starts) < min(ends). Derive every check
    from that one line.
  - II: check the overlap list BEFORE adding pairs, or a rejected booking
    leaves junk behind.
  - Generalising II to "at most k" is III's sweep with a rollback.

Run the tests at the bottom with:  python3 intervals/booking.py
"""

from bisect import bisect_right, insort


# ---------------------------------------------------------------- implementation


class MyCalendar:
    """LC 729. Reject any booking that overlaps an existing one."""

    def __init__(self):
        self.starts, self.ends = [], []        # parallel, sorted by start

    def book(self, s, e):
        i = bisect_right(self.starts, s)
        if i > 0 and self.ends[i - 1] > s:     # left neighbour runs into us
            return False
        if i < len(self.starts) and self.starts[i] < e:  # we run into right one
            return False
        self.starts.insert(i, s)
        self.ends.insert(i, e)
        return True


class MyCalendarTwo:
    """LC 731. Reject any booking that would make a triple booking."""

    def __init__(self):
        self.booked, self.overlaps = [], []

    def book(self, s, e):
        for a, b in self.overlaps:
            if max(a, s) < min(b, e):
                return False
        for a, b in self.booked:
            lo, hi = max(a, s), min(b, e)
            if lo < hi:
                self.overlaps.append((lo, hi))
        self.booked.append((s, e))
        return True


class MyCalendarThree:
    """LC 732. Accept everything; return the max overlap after each booking."""

    def __init__(self):
        self.delta, self.keys = {}, []

    def book(self, s, e):
        for t, d in ((s, 1), (e, -1)):
            if t not in self.delta:
                self.delta[t] = 0
                insort(self.keys, t)
            self.delta[t] += d
        best = cur = 0
        for t in self.keys:
            cur += self.delta[t]
            best = max(best, cur)
        return best


# ------------------------------------------------------------------------ tests


def _rand_requests(rng, n, hi=30):
    out = []
    for _ in range(n):
        a = rng.randint(0, hi)
        out.append((a, a + rng.randint(1, 8)))
    return out


def test_examples():
    c = MyCalendar()
    assert [c.book(*r) for r in [(10, 20), (15, 25), (20, 30)]] == [True, False, True]
    c2 = MyCalendarTwo()
    assert [c2.book(*r) for r in [(10, 20), (50, 60), (10, 40), (5, 15), (5, 10), (25, 55)]] == [
        True, True, True, False, True, True]
    c3 = MyCalendarThree()
    assert [c3.book(*r) for r in [(10, 20), (50, 60), (10, 40), (5, 15), (5, 10), (25, 55)]] == [
        1, 1, 2, 3, 3, 3]


def test_calendars_match_timeline():
    import random

    rng = random.Random(1)
    for limit, cls in [(1, MyCalendar), (2, MyCalendarTwo)]:
        for _ in range(300):
            cal, count = cls(), [0] * 40                     # count[t] covers [t, t+1)
            for s, e in _rand_requests(rng, rng.randint(1, 12)):
                ok = all(count[t] < limit for t in range(s, e))
                assert cal.book(s, e) == ok
                if ok:
                    for t in range(s, e):
                        count[t] += 1


def test_calendar_three_matches_timeline():
    import random

    rng = random.Random(2)
    for _ in range(300):
        cal, count = MyCalendarThree(), [0] * 40
        for s, e in _rand_requests(rng, rng.randint(1, 12)):
            for t in range(s, e):
                count[t] += 1
            assert cal.book(s, e) == max(count)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
