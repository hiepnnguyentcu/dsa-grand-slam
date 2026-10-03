"""Counters and rankings — All O(1) (AllOne), leaderboard, running averages.

Signs: "inc/dec a key and return a key with max/min count in O(1)", "top K
       scores", "average travel time between two stations", any live stats.
Approach:
  - AllOne: a doubly linked list of count buckets in increasing order, each
    holding the set of keys with that count, plus key -> bucket. inc moves a
    key to the next bucket (creating count + 1 right after if missing); dec
    moves it back. Empty buckets are unlinked at once, so head.next is the
    min and tail.prev is the max.
  - Leaderboard: dict player -> score, plus a sorted list of all scores.
    Updates bisect out the old score and insort the new one; top(K) sums the
    last K. (Java: TreeMap<score, count>; Python: sortedcontainers if allowed.)
  - Underground: open trips id -> (station, t); finished totals
    (from, to) -> [sum, count]. Average = sum / count; never store each trip.
  - Related: frequency stack is in stacks_heaps/stack_design.py; LFU cache
    (same bucket idea, keyed by use count) is in design/caches.py.
Complexity: AllOne O(1) every op. Leaderboard update O(n) worst (list shift,
            a fast memmove) or O(log n) with a balanced tree; top(K) O(K).
            Underground O(1) per op.
Gotchas:
  - AllOne: new buckets go next to the key's current bucket, never searched
    for; counts only change by one, so the neighbour is the only candidate.
  - AllOne dec to 0 removes the key entirely.
  - Leaderboard: remove the OLD score before inserting the new one, and
    remove one copy (bisect_left + pop), not every equal score.
  - Underground: the pair is ordered — A -> B and B -> A are different routes.

Run the tests at the bottom with:  python3 design/rankings.py
"""

from bisect import bisect_left, insort


# ---------------------------------------------------------------- implementation


class _Bucket:
    __slots__ = ("count", "keys", "prev", "next")

    def __init__(self, count):
        self.count, self.keys = count, set()
        self.prev = self.next = None


class AllOne:
    """LC 432. head(0) <-> buckets by increasing count <-> tail(inf)."""

    def __init__(self):
        self.head, self.tail = _Bucket(0), _Bucket(float("inf"))
        self.head.next, self.tail.prev = self.tail, self.head
        self.where = {}  # key -> its bucket

    def _insert_after(self, node, count):
        b = _Bucket(count)
        b.prev, b.next = node, node.next
        node.next.prev = b
        node.next = b
        return b

    def _discard(self, bucket, key):
        bucket.keys.discard(key)
        if not bucket.keys:
            bucket.prev.next, bucket.next.prev = bucket.next, bucket.prev

    def inc(self, key):
        cur = self.where.get(key, self.head)
        nxt = cur.next
        if nxt.count != cur.count + 1:
            nxt = self._insert_after(cur, cur.count + 1)
        nxt.keys.add(key)
        self.where[key] = nxt
        if cur is not self.head:
            self._discard(cur, key)

    def dec(self, key):
        cur = self.where.get(key)
        if cur is None:
            return
        if cur.count == 1:
            del self.where[key]
        else:
            prv = cur.prev
            if prv.count != cur.count - 1:
                prv = self._insert_after(prv, cur.count - 1)
            prv.keys.add(key)
            self.where[key] = prv
        self._discard(cur, key)

    def get_max_key(self):
        b = self.tail.prev
        return next(iter(b.keys)) if b is not self.head else ""

    def get_min_key(self):
        b = self.head.next
        return next(iter(b.keys)) if b is not self.tail else ""


class Leaderboard:
    """LC 1244. add_score adds to a player's total."""

    def __init__(self):
        self.score = {}
        self.ranked = []  # every current score, ascending

    def _drop(self, s):
        self.ranked.pop(bisect_left(self.ranked, s))

    def add_score(self, player, delta):
        if player in self.score:
            self._drop(self.score[player])
        self.score[player] = self.score.get(player, 0) + delta
        insort(self.ranked, self.score[player])

    def top(self, k):
        return sum(self.ranked[-k:]) if k > 0 else 0

    def reset(self, player):
        if player in self.score:
            self._drop(self.score.pop(player))


class UndergroundSystem:
    """LC 1396."""

    def __init__(self):
        self.open = {}  # card id -> (station, t)
        self.totals = {}  # (from, to) -> [time sum, trips]

    def check_in(self, cid, station, t):
        self.open[cid] = (station, t)

    def check_out(self, cid, station, t):
        start, t0 = self.open.pop(cid)
        tot = self.totals.setdefault((start, station), [0, 0])
        tot[0] += t - t0
        tot[1] += 1

    def get_average_time(self, start, end):
        s, n = self.totals[(start, end)]
        return s / n


# ------------------------------------------------------------------------ tests


def test_all_one_example():
    a = AllOne()
    a.inc("hello")
    a.inc("hello")
    assert a.get_max_key() == "hello" and a.get_min_key() == "hello"
    a.inc("leet")
    assert a.get_max_key() == "hello" and a.get_min_key() == "leet"
    a.dec("hello")
    a.dec("hello")
    assert a.get_max_key() == "leet" and a.get_min_key() == "leet"
    a.dec("leet")
    assert a.get_max_key() == "" and a.get_min_key() == ""


def test_all_one_matches_counter_recount():
    import random
    from collections import Counter

    rng = random.Random(1)
    a, ref = AllOne(), Counter()
    for _ in range(20000):
        k = rng.choice("abcdefgh")
        if rng.random() < 0.55:
            a.inc(k)
            ref[k] += 1
        else:
            a.dec(k)
            if ref[k]:
                ref[k] -= 1
        ref = +ref
        mx, mn = a.get_max_key(), a.get_min_key()
        if ref:
            assert ref[mx] == max(ref.values()) and ref[mn] == min(ref.values())
        else:
            assert mx == mn == ""


def test_all_one_buckets_stay_sorted_and_nonempty():
    import random

    rng = random.Random(2)
    a = AllOne()
    for _ in range(5000):
        k = rng.randrange(20)
        a.inc(k) if rng.random() < 0.6 else a.dec(k)
        b, last, seen = a.head.next, 0, 0
        while b is not a.tail:
            assert b.keys and b.count > last and b.next.prev is b
            assert all(a.where[k] is b for k in b.keys)
            last, seen, b = b.count, seen + len(b.keys), b.next
        assert seen == len(a.where)


def test_all_one_is_constant_time():
    import time

    a = AllOne()
    n = 100_000  # distinct keys: a max() scan per query would be ~5e9 steps
    t0 = time.perf_counter()
    for i in range(n):
        a.inc(i)
        a.inc(i % 100)
        a.get_max_key()
        a.get_min_key()
    assert a.get_max_key() in range(100)
    assert time.perf_counter() - t0 < 3.0


def test_leaderboard_example():
    lb = Leaderboard()
    for p, s in [(1, 73), (2, 56), (3, 39), (4, 51), (5, 4)]:
        lb.add_score(p, s)
    assert lb.top(1) == 73
    lb.reset(1)
    lb.reset(2)
    lb.add_score(2, 51)
    assert lb.top(3) == 141


def test_leaderboard_matches_full_sort():
    import random

    rng = random.Random(3)
    lb, ref = Leaderboard(), {}
    for _ in range(5000):
        p = rng.randrange(30)
        r = rng.random()
        if r < 0.5:
            d = rng.randint(1, 20)
            lb.add_score(p, d)
            ref[p] = ref.get(p, 0) + d
        elif r < 0.7:
            lb.reset(p)
            ref.pop(p, None)
        else:
            k = rng.randint(1, 10)
            assert lb.top(k) == sum(sorted(ref.values(), reverse=True)[:k])
        assert lb.ranked == sorted(ref.values())


def test_underground_example():
    u = UndergroundSystem()
    u.check_in(45, "Leyton", 3)
    u.check_in(32, "Paradise", 8)
    u.check_out(45, "Waterloo", 15)
    u.check_out(32, "Cambridge", 22)
    u.check_in(10, "Leyton", 24)
    u.check_out(10, "Waterloo", 38)
    assert u.get_average_time("Paradise", "Cambridge") == 14.0
    assert u.get_average_time("Leyton", "Waterloo") == 13.0


def test_underground_matches_trip_log():
    import random

    rng = random.Random(4)
    u, trips, inside, t = UndergroundSystem(), [], {}, 0
    for _ in range(5000):
        t += rng.randint(1, 5)
        cid = rng.randrange(15)
        if cid in inside:
            end = rng.choice("ABC")
            u.check_out(cid, end, t)
            s, t0 = inside.pop(cid)
            trips.append((s, end, t - t0))
        else:
            inside[cid] = (rng.choice("ABC"), t)
            u.check_in(cid, inside[cid][0], t)
        if trips:
            s, e, _ = rng.choice(trips)
            times = [d for a, b, d in trips if (a, b) == (s, e)]
            assert abs(u.get_average_time(s, e) - sum(times) / len(times)) < 1e-9


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
