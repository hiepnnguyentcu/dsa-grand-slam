"""Binary lifting — k-th ancestor and LCA queries in O(log n) each.

Signs: many LCA, k-th ancestor or node-distance queries on a static rooted
       tree, where O(n) per query (lca.py) is too slow.
Approach: up[j][v] is v's 2^j-th ancestor, built level by level:
          up[j][v] = up[j-1][ up[j-1][v] ]. Any jump of k steps is the sum of
          the powers of two in k's binary form. For LCA, lift the deeper node
          to the other's depth, then — from the largest power down — jump
          both nodes whenever their ancestors still differ. They end just
          below the LCA, so one more step up lands on it.
Complexity: O(n log n) time and space to build, O(log n) per query.
Gotchas: point the root at itself so jumps past the top stay at the root
         instead of indexing -1 (then check k > depth before trusting a
         k-th-ancestor answer). LOG must cover the deepest possible jump:
         n.bit_length() bits represent any depth up to n - 1. After equalising
         depths, return immediately if the nodes coincide. The tables are
         built iteratively, so deep trees are fine.

Run the tests at the bottom with:  python3 binary_trees/binary_lifting.py
"""

import random

from tree import nodes, random_tree, set_parents, skewed


# ---------------------------------------------------------------- implementation


class BinaryLifting:
    def __init__(self, n, edges, root=0):
        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        parent, self.depth = [root] * n, [0] * n
        seen, st = {root}, [root]
        while st:
            u = st.pop()
            for v in g[u]:
                if v not in seen:
                    seen.add(v)
                    parent[v], self.depth[v] = u, self.depth[u] + 1
                    st.append(v)
        self.LOG = max(1, n.bit_length())
        self.up = [parent]
        for j in range(1, self.LOG):
            prev = self.up[j - 1]
            self.up.append([prev[prev[v]] for v in range(n)])

    def kth_ancestor(self, v, k):
        """The ancestor k steps above v, or -1 if v is not that deep."""
        if k > self.depth[v]:
            return -1
        for j in range(self.LOG):
            if k >> j & 1:
                v = self.up[j][v]
        return v

    def lca(self, a, b):
        if self.depth[a] < self.depth[b]:
            a, b = b, a
        a = self.kth_ancestor(a, self.depth[a] - self.depth[b])
        if a == b:
            return a
        for j in range(self.LOG - 1, -1, -1):
            if self.up[j][a] != self.up[j][b]:
                a, b = self.up[j][a], self.up[j][b]
        return self.up[0][a]

    def distance(self, a, b):
        return self.depth[a] + self.depth[b] - 2 * self.depth[self.lca(a, b)]


# ------------------------------------------------------------------------ tests


def _from_binary_tree(root):
    """Number a TreeNode tree 0..n-1 (root is 0) and return (nodes, edges)."""
    ns = nodes(set_parents(root))
    idx = {x: i for i, x in enumerate(ns)}
    return ns, [(idx[x], idx[x.parent]) for x in ns if x.parent]


def _chain(ns, i):
    """Brute force: node i and all its ancestors, bottom up, as indices."""
    idx = {x: j for j, x in enumerate(ns)}
    out, x = [], ns[i]
    while x:
        out.append(idx[x])
        x = x.parent
    return out


def test_known():
    #        0
    #       / \
    #      1   2
    #     / \   \
    #    3   4   5
    #   /
    #  6
    bl = BinaryLifting(7, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (3, 6)])
    assert bl.lca(6, 4) == 1 and bl.lca(6, 5) == 0 and bl.lca(3, 6) == 3
    assert bl.kth_ancestor(6, 2) == 1 and bl.kth_ancestor(6, 3) == 0
    assert bl.kth_ancestor(6, 4) == -1 and bl.kth_ancestor(6, 0) == 6
    assert bl.distance(6, 5) == 5


def test_non_zero_root():
    bl = BinaryLifting(3, [(0, 1), (1, 2)], root=2)
    assert bl.depth == [2, 1, 0]
    assert bl.lca(0, 1) == 1 and bl.kth_ancestor(0, 2) == 2


def test_matches_parent_chains_on_random_trees():
    rng = random.Random(150)
    for _ in range(200):
        ns, edges = _from_binary_tree(random_tree(rng, rng.randint(1, 60)))
        n = len(ns)
        bl = BinaryLifting(n, edges)
        chains = [_chain(ns, i) for i in range(n)]
        for _ in range(20):
            a, b, k = rng.randrange(n), rng.randrange(n), rng.randint(0, n)
            ca, cb = chains[a], chains[b]
            want = next(x for x in ca if x in cb)
            assert bl.lca(a, b) == want
            assert bl.kth_ancestor(a, k) == (ca[k] if k < len(ca) else -1)
            assert bl.distance(a, b) == ca.index(want) + cb.index(want)


def test_single_node():
    bl = BinaryLifting(1, [])
    assert bl.lca(0, 0) == 0 and bl.kth_ancestor(0, 1) == -1


def test_skewed_both_ways():
    for side in ("left", "right"):
        ns, edges = _from_binary_tree(skewed(9, side))
        bl = BinaryLifting(len(ns), edges)
        assert bl.kth_ancestor(8, 8) == 0 and bl.kth_ancestor(8, 5) == 3
        assert bl.lca(8, 4) == 4


def test_deep_path():
    # every power of two is exercised on a 2^17-node path
    n = 1 << 17
    bl = BinaryLifting(n, [(i, i + 1) for i in range(n - 1)])
    assert bl.kth_ancestor(n - 1, n - 1) == 0
    assert bl.kth_ancestor(n - 1, 12_345) == n - 1 - 12_345
    assert bl.lca(n - 1, 77_777) == 77_777
    assert bl.distance(3, n - 1) == n - 4


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
