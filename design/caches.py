"""Caches — LRU (hash map + doubly linked list, or OrderedDict) and LFU.

Signs: "design a cache with capacity k", "evict the least recently used",
       "evict the least frequently used, ties by recency", get/put in O(1).
Approach:
  - LRU: a dict maps key -> node; nodes sit in a doubly linked list ordered by
    recency, most recent next to `head`. get moves the node to the front; put
    inserts at the front and, when over capacity, unlinks the node before
    `tail`. Two sentinel nodes mean no None checks at the ends.
  - LRU in Python: OrderedDict already is that list. move_to_end on a hit,
    popitem(last=False) to evict.
  - LFU: key -> (value, freq), plus freq -> OrderedDict of keys (an LRU list per
    frequency), plus `min_freq`. A hit moves the key from bucket f to f + 1 and
    bumps min_freq if bucket f emptied and was the minimum. A new key always
    resets min_freq to 1, so eviction is popitem(last=False) on bucket min_freq.
Complexity: O(1) per get/put for all three; O(capacity) space.
Gotchas:
  - Unlink before re-linking. Forgetting to delete the evicted key from the
    dict leaves a dangling node that a later get will "find".
  - Store the key in the node: eviction starts from the list and must delete
    the dict entry too.
  - put on an existing key updates the value AND counts as a use.
  - LFU: capacity 0 must reject every put. Never search for the new min_freq —
    it can only rise by one (on a hit) or drop to 1 (on an insert).

Run the tests at the bottom with:  python3 design/caches.py
"""

from collections import OrderedDict, defaultdict


# ---------------------------------------------------------------- implementation


class _Node:
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key=None, val=None):
        self.key, self.val = key, val
        self.prev = self.next = None


class LRUCache:
    """LC 146. head <-> most recent ... least recent <-> tail."""

    def __init__(self, capacity):
        self.cap = capacity
        self.map = {}
        self.head, self.tail = _Node(), _Node()  # sentinels, never removed
        self.head.next, self.tail.prev = self.tail, self.head

    def _unlink(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _push_front(self, node):
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        node = self.map.get(key)
        if node is None:
            return -1
        self._unlink(node)
        self._push_front(node)
        return node.val

    def put(self, key, val):
        if self.cap <= 0:
            return
        node = self.map.get(key)
        if node:
            node.val = val
            self._unlink(node)
        else:
            if len(self.map) == self.cap:
                lru = self.tail.prev
                self._unlink(lru)
                del self.map[lru.key]  # why the node stores its key
            node = self.map[key] = _Node(key, val)
        self._push_front(node)


class LRUCacheOD:
    """Same contract on OrderedDict: the end is most recent."""

    def __init__(self, capacity):
        self.cap = capacity
        self.od = OrderedDict()

    def get(self, key):
        if key not in self.od:
            return -1
        self.od.move_to_end(key)
        return self.od[key]

    def put(self, key, val):
        if self.cap <= 0:
            return
        if key in self.od:
            self.od.move_to_end(key)
        self.od[key] = val
        if len(self.od) > self.cap:
            self.od.popitem(last=False)


class LFUCache:
    """LC 460. Evict the lowest frequency; ties go to the least recent."""

    def __init__(self, capacity):
        self.cap = capacity
        self.vals = {}  # key -> value
        self.freq = {}  # key -> use count
        self.buckets = defaultdict(OrderedDict)  # count -> keys, oldest first
        self.min_freq = 0

    def _touch(self, key):
        f = self.freq[key]
        del self.buckets[f][key]
        if not self.buckets[f]:
            del self.buckets[f]
            if self.min_freq == f:
                self.min_freq = f + 1
        self.freq[key] = f + 1
        self.buckets[f + 1][key] = None

    def get(self, key):
        if key not in self.vals:
            return -1
        self._touch(key)
        return self.vals[key]

    def put(self, key, val):
        if self.cap <= 0:
            return
        if key in self.vals:
            self.vals[key] = val
            self._touch(key)
            return
        if len(self.vals) == self.cap:
            old, _ = self.buckets[self.min_freq].popitem(last=False)
            if not self.buckets[self.min_freq]:
                del self.buckets[self.min_freq]
            del self.vals[old], self.freq[old]
        self.vals[key], self.freq[key] = val, 1
        self.buckets[1][key] = None
        self.min_freq = 1


# ------------------------------------------------------------------------ tests


class _NaiveLRU:
    """List in recency order, least recent first. O(n) per op."""

    def __init__(self, capacity):
        self.cap, self.items = capacity, []

    def get(self, key):
        for i, (k, v) in enumerate(self.items):
            if k == key:
                self.items.append(self.items.pop(i))
                return v
        return -1

    def put(self, key, val):
        if self.cap <= 0:
            return
        self.items = [(k, v) for k, v in self.items if k != key]
        self.items.append((key, val))
        if len(self.items) > self.cap:
            self.items.pop(0)


class _NaiveLFU:
    """Store (value, freq, last_tick); evict min (freq, last_tick) by scan."""

    def __init__(self, capacity):
        self.cap, self.d, self.tick = capacity, {}, 0

    def get(self, key):
        if key not in self.d:
            return -1
        v, f, _ = self.d[key]
        self.tick += 1
        self.d[key] = (v, f + 1, self.tick)
        return v

    def put(self, key, val):
        if self.cap <= 0:
            return
        self.tick += 1
        if key in self.d:
            _, f, _ = self.d[key]
            self.d[key] = (val, f + 1, self.tick)
            return
        if len(self.d) == self.cap:
            victim = min(self.d, key=lambda k: (self.d[k][1], self.d[k][2]))
            del self.d[victim]
        self.d[key] = (val, 1, self.tick)


def _drive(make, make_ref, seed, caps, ops=4000, keys=12):
    import random

    rng = random.Random(seed)
    for cap in caps:
        c, ref = make(cap), make_ref(cap)
        for _ in range(ops):
            k = rng.randrange(keys)
            if rng.random() < 0.5:
                assert c.get(k) == ref.get(k)
            else:
                v = rng.randrange(1000)
                c.put(k, v)
                ref.put(k, v)


def test_lru_example():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1
    c.put(3, 3)  # evicts 2
    assert c.get(2) == -1
    c.put(4, 4)  # evicts 1
    assert [c.get(1), c.get(3), c.get(4)] == [-1, 3, 4]


def test_lru_matches_naive():
    _drive(LRUCache, _NaiveLRU, 1, caps=(0, 1, 2, 5, 11))


def test_lru_ordereddict_matches_naive():
    _drive(LRUCacheOD, _NaiveLRU, 2, caps=(0, 1, 3, 8))


def test_lru_map_and_list_agree():
    import random

    rng = random.Random(3)
    c = LRUCache(6)
    for _ in range(3000):
        c.put(rng.randrange(20), 0) if rng.random() < 0.6 else c.get(rng.randrange(20))
        keys, node = [], c.head.next
        while node is not c.tail:
            assert node.next.prev is node
            keys.append(node.key)
            node = node.next
        assert len(keys) == len(set(keys)) == len(c.map) <= 6
        assert set(keys) == set(c.map)


def test_lfu_example():
    c = LFUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1
    c.put(3, 3)  # 2 has freq 1, evicted
    assert c.get(2) == -1 and c.get(3) == 3
    c.put(4, 4)  # 1 and 3 both freq 2; 1 is older
    assert [c.get(1), c.get(3), c.get(4)] == [-1, 3, 4]


def test_lfu_matches_naive():
    _drive(LFUCache, _NaiveLFU, 4, caps=(0, 1, 2, 4, 9))


def test_lfu_min_freq_is_true_minimum():
    import random

    rng = random.Random(5)
    c = LFUCache(5)
    for _ in range(3000):
        c.put(rng.randrange(15), 0) if rng.random() < 0.5 else c.get(rng.randrange(15))
        if c.freq:
            assert c.min_freq == min(c.freq.values())
            assert all(c.buckets.values())  # no empty buckets left behind


def test_caches_are_constant_time():
    import time

    n = 100_000
    for cls in (LRUCache, LRUCacheOD, LFUCache):
        c = cls(n // 2)  # naive list scan would be ~n^2/4 = 2.5e9 steps
        t0 = time.perf_counter()
        for i in range(n):
            c.put(i, i)
            c.get(i // 2)
        assert time.perf_counter() - t0 < 3.0, cls.__name__


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
