"""Time-based structures — versioned key-value, snapshots, corrected prices, rate limits.

Signs: "get the value at timestamp t", "snapshot id", "price records can be
       corrected later", "print each message at most once every 10 seconds".
Approach:
  - TimeMap: key -> parallel lists (timestamps, values). set timestamps only
    grow, so append keeps them sorted; get bisects for the last ts <= t.
  - SnapshotArray: per index, a list of (snap_id, value) written only when
    the value changes. get bisects for the last write with id <= snap_id.
    snap() is just snap_id += 1 — never copy the array.
  - StockPrice: dict ts -> price for the truth, plus a max-heap and min-heap
    of (price, ts). A correction pushes a new entry; stale entries (price no
    longer matches the dict) are popped only when they reach the top.
  - Logger: dict message -> next allowed time.
  - Last-N-seconds hit counter: see stacks_heaps/queue_design.py
    (RecentCounter). Running median: stacks_heaps/two_heaps.py.
Complexity: TimeMap set O(1), get O(log n). SnapshotArray set/snap O(1),
            get O(log s). StockPrice update O(log n), max/min O(log n)
            amortised. Logger O(1).
Gotchas:
  - bisect_right(ts, t) - 1 is the last ts <= t; -1 means "before any write".
  - SnapshotArray: two sets in the same snap overwrite the last entry, or
    the list grows with every set and get returns a stale duplicate.
  - StockPrice: a lazy heap must check the entry against the dict, not just
    the timestamp — the same ts can be corrected back to an old price.
  - Logger: store the NEXT allowed time and only update it when printing.

Run the tests at the bottom with:  python3 design/time_based.py
"""

import heapq
from bisect import bisect_right
from collections import defaultdict


# ---------------------------------------------------------------- implementation


class TimeMap:
    """LC 981. Timestamps per key strictly increase; missing -> ""."""

    def __init__(self):
        self.ts = defaultdict(list)
        self.vals = defaultdict(list)

    def set(self, key, value, timestamp):
        self.ts[key].append(timestamp)
        self.vals[key].append(value)

    def get(self, key, timestamp):
        i = bisect_right(self.ts.get(key, ()), timestamp) - 1
        return self.vals[key][i] if i >= 0 else ""


class SnapshotArray:
    """LC 1146. Length-n array of zeros; get(index, snap_id)."""

    def __init__(self, n):
        self.hist = [[(-1, 0)] for _ in range(n)]  # (snap_id, value), sorted
        self.snap_id = 0

    def set(self, index, val):
        h = self.hist[index]
        if h[-1][0] == self.snap_id:
            h[-1] = (self.snap_id, val)
        else:
            h.append((self.snap_id, val))

    def snap(self):
        self.snap_id += 1
        return self.snap_id - 1

    def get(self, index, snap_id):
        h = self.hist[index]
        return h[bisect_right(h, (snap_id, float("inf"))) - 1][1]


class StockPrice:
    """LC 2034. update may correct an earlier timestamp."""

    def __init__(self):
        self.price = {}
        self.latest = 0
        self.max_h, self.min_h = [], []

    def update(self, timestamp, price):
        self.price[timestamp] = price
        self.latest = max(self.latest, timestamp)
        heapq.heappush(self.max_h, (-price, timestamp))
        heapq.heappush(self.min_h, (price, timestamp))

    def current(self):
        return self.price[self.latest]

    def maximum(self):
        while self.price[self.max_h[0][1]] != -self.max_h[0][0]:
            heapq.heappop(self.max_h)  # stale: that ts was corrected
        return -self.max_h[0][0]

    def minimum(self):
        while self.price[self.min_h[0][1]] != self.min_h[0][0]:
            heapq.heappop(self.min_h)
        return self.min_h[0][0]


class Logger:
    """LC 359. Each message prints at most once per `window` seconds."""

    def __init__(self, window=10):
        self.window = window
        self.next_ok = {}

    def should_print(self, timestamp, message):
        if timestamp < self.next_ok.get(message, timestamp):
            return False
        self.next_ok[message] = timestamp + self.window
        return True


# ------------------------------------------------------------------------ tests


def test_time_map_example():
    m = TimeMap()
    m.set("foo", "bar", 1)
    assert m.get("foo", 1) == "bar" and m.get("foo", 3) == "bar"
    m.set("foo", "bar2", 4)
    assert m.get("foo", 4) == "bar2" and m.get("foo", 5) == "bar2"
    assert m.get("foo", 0) == "" and m.get("nope", 9) == ""


def test_time_map_matches_scan():
    import random

    rng = random.Random(1)
    m, log, t = TimeMap(), [], 0
    for _ in range(4000):
        k = rng.choice("abcd")
        if rng.random() < 0.4:
            t += rng.randint(1, 5)
            v = str(rng.randrange(100))
            m.set(k, v, t)
            log.append((k, t, v))
        else:
            q = rng.randint(0, t + 3)
            hits = [v for key, ts, v in log if key == k and ts <= q]
            assert m.get(k, q) == (hits[-1] if hits else "")


def test_snapshot_array_example():
    a = SnapshotArray(3)
    a.set(0, 5)
    assert a.snap() == 0
    a.set(0, 6)
    assert a.get(0, 0) == 5 and a.get(0, 1) == 6 and a.get(2, 0) == 0


def test_snapshot_array_matches_full_copies():
    import random

    rng = random.Random(2)
    n = 6
    a, cur, snaps = SnapshotArray(n), [0] * n, []
    for _ in range(5000):
        r = rng.random()
        if r < 0.5:
            i, v = rng.randrange(n), rng.randrange(50)
            a.set(i, v)
            cur[i] = v
        elif r < 0.65:
            assert a.snap() == len(snaps)
            snaps.append(cur[:])
        elif snaps:
            s, i = rng.randrange(len(snaps)), rng.randrange(n)
            assert a.get(i, s) == snaps[s][i]


def test_snapshot_array_memory_tracks_writes_not_snaps():
    a = SnapshotArray(10_000)
    for _ in range(10_000):
        a.snap()  # full copies would be 10^8 cells
    a.set(7, 1)
    a.set(7, 2)  # same snap: overwrite, not append
    assert sum(len(h) for h in a.hist) == 10_001
    assert a.get(7, 9_999) == 0 and a.get(7, 10_000) == 2


def test_stock_price_example():
    s = StockPrice()
    s.update(1, 10)
    s.update(2, 5)
    assert s.current() == 5 and s.maximum() == 10
    s.update(1, 3)
    assert s.maximum() == 5
    s.update(4, 2)
    assert s.minimum() == 2


def test_stock_price_matches_dict_scan():
    import random

    rng = random.Random(3)
    s, ref = StockPrice(), {}
    for _ in range(5000):
        ts, p = rng.randint(1, 40), rng.randint(1, 30)  # many corrections
        s.update(ts, p)
        ref[ts] = p
        assert s.current() == ref[max(ref)]
        assert s.maximum() == max(ref.values())
        assert s.minimum() == min(ref.values())


def test_logger_example():
    lg = Logger()
    got = [lg.should_print(t, m) for t, m in [(1, "foo"), (2, "bar"), (3, "foo"), (8, "bar"), (10, "foo"), (11, "foo")]]
    assert got == [True, True, False, False, False, True]


def test_logger_matches_history_scan():
    import random

    rng = random.Random(4)
    lg, printed, t = Logger(7), [], 0
    for _ in range(4000):
        t += rng.randint(0, 3)
        m = rng.choice("xyz")
        expect = all(not (pm == m and t - pt < 7) for pt, pm in printed)
        assert lg.should_print(t, m) == expect
        if expect:
            printed.append((t, m))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
