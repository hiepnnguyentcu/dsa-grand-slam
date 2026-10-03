"""Randomized set — insert, remove, getRandom in O(1), with and without duplicates.

Signs: "getRandom with equal probability", "insert/delete/getRandom O(1)",
       "random element from a set that changes", sampling a live pool.
Approach:
  - A list gives O(1) random access; a dict val -> index gives O(1) lookup.
  - Remove = swap-with-last: move the last value into the hole, fix its index
    in the dict, pop the list. Order is not kept, and it doesn't need to be.
  - Duplicates (LC 381): the dict maps val -> set of indices. Remove takes any
    index of val, moves the last element there, and updates both index sets.
    getRandom over the list is then weighted by multiplicity for free.
Complexity: O(1) average per op (dict + list append/pop); O(n) space.
Gotchas:
  - Update the moved element's index BEFORE deleting the removed one: when
    the removed value IS the last element, the order decides what survives.
  - Duplicates: discard the old index from the moved value's set and add the
    new one; when val is itself last, idx == last and nothing moves.
  - random.choice on a set is invalid (and O(n) via list()); that is why the
    list exists.

Run the tests at the bottom with:  python3 design/randomized_set.py
"""

import random
from collections import defaultdict


# ---------------------------------------------------------------- implementation


class RandomizedSet:
    """LC 380."""

    def __init__(self, rng=None):
        self.vals = []
        self.pos = {}  # value -> its index in vals
        self.rng = rng or random.Random()

    def insert(self, val):
        if val in self.pos:
            return False
        self.pos[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val):
        if val not in self.pos:
            return False
        i, last = self.pos[val], self.vals[-1]
        self.vals[i] = last
        self.pos[last] = i  # first: covers val == last
        self.vals.pop()
        del self.pos[val]
        return True

    def get_random(self):
        return self.vals[self.rng.randrange(len(self.vals))]


class RandomizedCollection:
    """LC 381. Duplicates allowed; get_random weighted by count."""

    def __init__(self, rng=None):
        self.vals = []
        self.idx = defaultdict(set)  # value -> indices holding it
        self.rng = rng or random.Random()

    def insert(self, val):
        """True if val was not present before."""
        self.idx[val].add(len(self.vals))
        self.vals.append(val)
        return len(self.idx[val]) == 1

    def remove(self, val):
        if not self.idx.get(val):
            return False
        i = self.idx[val].pop()
        last = self.vals[-1]
        j = len(self.vals) - 1
        if i != j:  # move last into the hole
            self.vals[i] = last
            self.idx[last].discard(j)
            self.idx[last].add(i)
        self.vals.pop()
        if not self.idx[val]:
            del self.idx[val]
        return True

    def get_random(self):
        return self.vals[self.rng.randrange(len(self.vals))]


# ------------------------------------------------------------------------ tests


def test_randomized_set_example():
    s = RandomizedSet(random.Random(0))
    assert s.insert(1) and not s.remove(2) and s.insert(2)
    assert s.get_random() in (1, 2)
    assert s.remove(1) and not s.insert(2)
    assert s.get_random() == 2


def test_randomized_set_matches_set():
    rng = random.Random(1)
    s, ref = RandomizedSet(random.Random(2)), set()
    for _ in range(20000):
        x = rng.randrange(30)
        r = rng.random()
        if r < 0.45:
            assert s.insert(x) == (x not in ref)
            ref.add(x)
        elif r < 0.9:
            assert s.remove(x) == (x in ref)
            ref.discard(x)
        elif ref:
            assert s.get_random() in ref
        assert sorted(s.vals) == sorted(ref)
        assert all(s.vals[i] == v for v, i in s.pos.items())


def test_randomized_set_is_uniform():
    s = RandomizedSet(random.Random(3))
    for x in range(10):
        s.insert(x)
    for x in (0, 4, 9):  # holes get filled by swaps
        s.remove(x)
    counts = defaultdict(int)
    draws = 70000
    for _ in range(draws):
        counts[s.get_random()] += 1
    assert set(counts) == {1, 2, 3, 5, 6, 7, 8}
    assert all(abs(c - draws / 7) < 0.05 * draws / 7 for c in counts.values())


def test_randomized_collection_matches_multiset():
    from collections import Counter

    rng = random.Random(4)
    c, ref = RandomizedCollection(random.Random(5)), Counter()
    for _ in range(20000):
        x = rng.randrange(8)
        r = rng.random()
        if r < 0.5:
            assert c.insert(x) == (ref[x] == 0)
            ref[x] += 1
        elif r < 0.9:
            assert c.remove(x) == (ref[x] > 0)
            if ref[x]:
                ref[x] -= 1
        elif +ref:
            assert ref[c.get_random()] > 0
        assert Counter(c.vals) == +ref
        for v, ids in c.idx.items():
            assert ids and all(c.vals[i] == v for i in ids)


def test_randomized_collection_weighted():
    c = RandomizedCollection(random.Random(6))
    for x in [1, 1, 1, 2]:
        c.insert(x)
    draws = 40000
    ones = sum(c.get_random() == 1 for _ in range(draws))
    assert abs(ones / draws - 0.75) < 0.02


def test_remove_is_constant_time():
    import time

    n = 200_000  # list.remove would be O(n) each, ~2e10 steps
    for cls in (RandomizedSet, RandomizedCollection):
        s = cls(random.Random(7))
        t0 = time.perf_counter()
        for i in range(n):
            s.insert(i)
        for i in range(n):
            s.remove(i)  # always from the front: worst case for list.remove
        assert not s.vals and time.perf_counter() - t0 < 3.0, cls.__name__


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
