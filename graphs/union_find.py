"""Union-Find (Disjoint Set Union) — plain, dict-keyed, and weighted.

Signs: group elements dynamically, "are x and y connected", merging accounts,
       cycle in an undirected graph, edges arriving over time, Kruskal's MST.
Approach: every set is a tree whose root names the set. `find` walks to the
          root, flattening the path as it goes; `union` hangs the smaller tree
          under the larger one. Those two tricks together give near-constant
          amortised cost.
Complexity: O(alpha(n)) amortised per operation — alpha is the inverse
            Ackermann function, below 5 for any n you will ever see.
Gotchas: DSU only ever *merges*. There is no split, so it cannot handle edge
         deletion — for that you process offline in reverse. Map arbitrary
         keys (strings, coordinates) to ints, or use DictDSU.

Run the tests at the bottom with:  python3 graphs/union_find.py
"""


# ---------------------------------------------------------------- implementation


class DSU:
    """Union-Find over the integers 0..n-1."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.count = n  # number of disjoint sets

    def find(self, x):
        """Root of x's set, flattening the path on the way up.

        This is *path halving*: point each node at its grandparent as we climb.
        One pass, no recursion, and it flattens the tree nearly as well as full
        path compression.
        """
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        """Merge the two sets. Returns False if they were already one set.

        That return value is the whole trick behind cycle detection and
        Kruskal: a "useless" union is exactly an edge that closes a cycle.
        """
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:  # union by size: small under large
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.count -= 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)

    def set_size(self, x):
        return self.size[self.find(x)]

    def groups(self):
        """{root: [members]} — the sets as they currently stand."""
        out = {}
        for x in range(len(self.parent)):
            out.setdefault(self.find(x), []).append(x)
        return out


class DictDSU:
    """Union-Find over arbitrary hashable keys, created on first sight.

    Use when nodes are strings, coordinates or emails and you would otherwise
    write a key -> int index map by hand.
    """

    def __init__(self):
        self.parent = {}
        self.size = {}
        self.count = 0

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.size[x] = 1
            self.count += 1
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.count -= 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)


class RatioDSU:
    """Weighted Union-Find: relations of the form a / b = k.

    Signs: ratios ("a / b = 2.0"), offsets ("x is 3 more than y"), parity
           constraints ("x and y differ").
    Approach: store w[x] = the value of x *relative to its parent*, so the
              invariant is x == w[x] * parent[x]. `find` compresses the path
              and multiplies the weights along it, leaving w[x] relative to the
              root. Two nodes under the same root can then be compared
              directly: a / b == w[a] / w[b].

    Swap multiplication for addition and you get offset constraints; use XOR
    and you get parity ("are these two the same colour").
    """

    def __init__(self):
        self.parent = {}
        self.weight = {}  # x == weight[x] * parent[x]

    def find(self, x):
        if x not in self.parent:
            self.parent[x], self.weight[x] = x, 1.0
        if self.parent[x] != x:
            root = self.find(self.parent[x])          # parent's weight is now
            self.weight[x] *= self.weight[self.parent[x]]  # relative to root
            self.parent[x] = root
        return self.parent[x]

    def union(self, a, b, ratio):
        """Record a / b == ratio."""
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb
            self.weight[ra] = ratio * self.weight[b] / self.weight[a]

    def query(self, a, b):
        """a / b, or -1.0 if unknown (either value unseen, or not related)."""
        if a not in self.parent or b not in self.parent:
            return -1.0
        if self.find(a) != self.find(b):
            return -1.0
        return self.weight[a] / self.weight[b]


# ------------------------------------------------------------------------ tests


def test_starts_fully_disconnected():
    d = DSU(5)
    assert d.count == 5
    assert not d.connected(0, 1)
    assert d.set_size(0) == 1


def test_union_merges_and_counts():
    d = DSU(5)
    assert d.union(0, 1) is True
    assert d.union(1, 2) is True
    assert d.count == 3  # {0,1,2}, {3}, {4}
    assert d.connected(0, 2)
    assert d.set_size(0) == 3


def test_redundant_union_is_rejected():
    d = DSU(3)
    d.union(0, 1)
    d.union(1, 2)
    assert d.union(0, 2) is False  # already connected -> this edge is a cycle
    assert d.count == 1


def test_connectivity_is_transitive_and_symmetric():
    d = DSU(6)
    for a, b in [(0, 1), (2, 3), (4, 5), (1, 3)]:
        d.union(a, b)
    assert d.groups() == {d.find(0): [0, 1, 2, 3], d.find(4): [4, 5]}
    assert d.connected(0, 3) and d.connected(3, 0)
    assert not d.connected(0, 5)


def test_matches_brute_force_on_random_unions():
    import random

    random.seed(7)
    n = 40
    d = DSU(n)
    reference = [{i} for i in range(n)]  # naive set-merging
    for _ in range(80):
        a, b = random.randrange(n), random.randrange(n)
        d.union(a, b)
        sa, sb = reference[a], reference[b]
        if sa is not sb:
            merged = sa | sb
            for x in merged:
                reference[x] = merged
    for a in range(n):
        for b in range(n):
            assert d.connected(a, b) == (b in reference[a])
    assert d.count == len({id(s) for s in reference})


def test_dict_dsu_with_string_keys():
    d = DictDSU()
    d.union("a@x.com", "a@y.com")
    d.union("a@y.com", "a@z.com")
    assert d.connected("a@x.com", "a@z.com")
    assert not d.connected("a@x.com", "b@x.com")
    assert d.count == 2  # the a-cluster, plus b@x.com created by the query above


def test_ratio_chain():
    # a / b = 2, b / c = 3  =>  a / c = 6
    d = RatioDSU()
    d.union("a", "b", 2.0)
    d.union("b", "c", 3.0)
    assert abs(d.query("a", "c") - 6.0) < 1e-9
    assert abs(d.query("c", "a") - 1 / 6) < 1e-9
    assert abs(d.query("b", "a") - 0.5) < 1e-9


def test_ratio_unknowns():
    d = RatioDSU()
    d.union("a", "b", 2.0)
    d.union("x", "y", 5.0)
    assert d.query("a", "x") == -1.0      # known values, unrelated
    assert d.query("a", "nope") == -1.0   # never seen
    assert d.query("a", "a") == 1.0       # anything over itself


def test_ratio_stays_consistent_after_compression():
    d = RatioDSU()
    for i in range(50):
        d.union(f"v{i}", f"v{i + 1}", 2.0)  # each is twice the next
    assert abs(d.query("v0", "v50") - 2.0 ** 50) < 1e-3
    assert abs(d.query("v10", "v13") - 8.0) < 1e-9


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
