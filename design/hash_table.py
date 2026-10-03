"""Hash map / hash set from scratch — separate chaining with resizing.

Signs: "design a HashMap/HashSet without built-in hash tables", "how does a
       dict work", follow-ups on load factor, collisions, rehashing.
Approach: an array of buckets; each bucket is a short list of [key, value]
          pairs (separate chaining). Bucket = hash(key) % capacity. When
          size / capacity passes the load factor (0.75), allocate a bigger
          array and re-insert every pair — positions depend on capacity, so
          they must be recomputed. Capacity grows as 2c + 1 (7, 15, 31, ...).
Complexity: O(1) average per op, O(n) worst case if every key collides.
            Resize is O(n) but happens after n/2 more inserts, so O(1)
            amortised (same argument as a dynamic array). O(n) space.
Gotchas:
  - Rehash on resize: copying buckets by index puts keys in the wrong place.
  - put on an existing key overwrites, it does not append a second pair.
  - Capacity choice: with a power of two, keys that share low bits (all
    multiples of 16) pile into a few buckets. Odd capacities, or mixing the
    hash, spread them. Python's hash(int) is the int itself.
  - Open addressing (linear probing) is the alternative: removal then needs a
    tombstone, or later probes stop early.

Run the tests at the bottom with:  python3 design/hash_table.py
"""


# ---------------------------------------------------------------- implementation


class MyHashMap:
    """LC 706. get returns -1 for a missing key."""

    LOAD = 0.75

    def __init__(self, capacity=7):
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0

    def _bucket(self, key):
        return self.buckets[hash(key) % len(self.buckets)]

    def put(self, key, val):
        b = self._bucket(key)
        for pair in b:
            if pair[0] == key:
                pair[1] = val
                return
        b.append([key, val])
        self.size += 1
        if self.size > self.LOAD * len(self.buckets):
            self._resize(2 * len(self.buckets) + 1)

    def get(self, key):
        for k, v in self._bucket(key):
            if k == key:
                return v
        return -1

    def remove(self, key):
        b = self._bucket(key)
        for i, (k, _) in enumerate(b):
            if k == key:
                b[i] = b[-1]  # swap-pop: order inside a bucket is irrelevant
                b.pop()
                self.size -= 1
                return

    def _resize(self, capacity):
        old = self.buckets
        self.buckets = [[] for _ in range(capacity)]
        for b in old:
            for k, v in b:
                self.buckets[hash(k) % capacity].append([k, v])


class MyHashSet:
    """LC 705. A map whose values do not matter."""

    def __init__(self):
        self.map = MyHashMap()

    def add(self, key):
        self.map.put(key, True)

    def remove(self, key):
        self.map.remove(key)

    def contains(self, key):
        return self.map.get(key) is True


# ------------------------------------------------------------------------ tests


def test_hash_map_example():
    m = MyHashMap()
    m.put(1, 1)
    m.put(2, 2)
    assert m.get(1) == 1 and m.get(3) == -1
    m.put(2, 1)
    assert m.get(2) == 1
    m.remove(2)
    assert m.get(2) == -1


def test_hash_map_matches_dict():
    import random

    rng = random.Random(1)
    for keyspace in (10, 500, 5000):
        m, ref = MyHashMap(), {}
        for _ in range(20000):
            k = rng.randrange(keyspace)
            r = rng.random()
            if r < 0.5:
                v = rng.randrange(10**6)
                m.put(k, v)
                ref[k] = v
            elif r < 0.75:
                m.remove(k)
                ref.pop(k, None)
            else:
                assert m.get(k) == ref.get(k, -1)
            assert m.size == len(ref)
        assert sorted(k for b in m.buckets for k, _ in b) == sorted(ref)


def test_hash_map_string_and_tuple_keys():
    import random

    rng = random.Random(2)
    m, ref = MyHashMap(), {}
    for step in range(5000):
        k = rng.choice(["a", "bb", "", (1, 2), (2, 1), ("x",), str(rng.randrange(200))])
        if rng.random() < 0.7:
            m.put(k, step)
            ref[k] = step
        else:
            m.remove(k)
            ref.pop(k, None)
        assert all(m.get(key) == v for key, v in ref.items())


def test_hash_set_matches_set():
    import random

    rng = random.Random(3)
    s, ref = MyHashSet(), set()
    for _ in range(20000):
        k = rng.randrange(1000)
        r = rng.random()
        if r < 0.5:
            s.add(k)
            ref.add(k)
        elif r < 0.8:
            s.remove(k)
            ref.discard(k)
        else:
            assert s.contains(k) == (k in ref)


def test_load_factor_and_chain_length():
    m = MyHashMap()
    for i in range(0, 16 * 50_000, 16):  # patterned keys: all multiples of 16
        m.put(i, i)
        assert m.size <= MyHashMap.LOAD * len(m.buckets)
    assert max(len(b) for b in m.buckets) <= 2  # odd capacity spreads them


def test_power_of_two_capacity_clusters():
    """Why the gotcha matters: same keys, capacity 1024, no resize."""
    buckets = [0] * 1024
    for i in range(0, 16 * 1000, 16):
        buckets[hash(i) % 1024] += 1
    assert sum(1 for c in buckets if c) == 64  # 1000 keys in 64 of 1024 buckets


def test_hash_map_is_constant_time():
    import time

    n = 200_000
    m = MyHashMap()
    t0 = time.perf_counter()
    for i in range(n):
        m.put(i * 7919, i)
    for i in range(n):
        assert m.get(i * 7919) == i
    assert time.perf_counter() - t0 < 3.0


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
