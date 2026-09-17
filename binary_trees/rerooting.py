"""Rerooting DP — an answer for every node as if it were the root, in O(n).

Signs: "for each node, compute ..." where the quantity depends on the whole
       tree seen from that node — sum of distances to all nodes, farthest
       node (eccentricity), number of nodes on each side of an edge.
Approach: pass 1 (post-order from an arbitrary root) computes subtree
          aggregates and the answer for that root. Pass 2 (pre-order) moves
          the root from parent p to child c and fixes the answer in O(1):
          for distance sums, the size[c] nodes under c get one step closer
          and the other n - size[c] get one step farther, so
              ans[c] = ans[p] - size[c] + (n - size[c]).
          When the aggregate is a max rather than a sum, "everything except
          c" cannot be undone by subtraction — keep the best *two* child
          values so the parent can hand c the best one that isn't c's own.
Complexity: O(n) time and space.
Gotchas: works on general trees given as n and an edge list, so nodes are
         0..n-1 and adjacency is built first. Both passes reuse one explicit-
         stack DFS order, so no recursion limit applies. A forest or a graph
         with a cycle breaks the formula silently — check len(edges) == n - 1.

Run the tests at the bottom with:  python3 binary_trees/rerooting.py
"""

import random
from collections import deque

from tree import random_tree, to_graph


# ---------------------------------------------------------------- implementation


def _rooted(n, edges):
    """Adjacency, parent array and a parents-before-children order from node 0."""
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    parent, order, seen = [-1] * n, [], [False] * n
    st, seen[0] = [0], True
    while st:
        u = st.pop()
        order.append(u)
        for v in g[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                st.append(v)
    return g, parent, order


def sum_of_distances(n, edges):
    """ans[i] = sum of edge distances from i to every other node."""
    g, parent, order = _rooted(n, edges)
    size, ans = [1] * n, [0] * n
    for u in reversed(order):  # children before parents
        for v in g[u]:
            if v != parent[u]:
                size[u] += size[v]
                ans[u] += ans[v] + size[v]
    # ans[0] is now right; every other ans[] entry is a subtree-only partial
    for u in order:  # parents before children
        for v in g[u]:
            if v != parent[u]:
                ans[v] = ans[u] - size[v] + (n - size[v])
    return ans


def eccentricities(n, edges):
    """ecc[i] = edges from i to the node farthest from it."""
    g, parent, order = _rooted(n, edges)
    down1, down2, best_child = [0] * n, [0] * n, [-1] * n
    for u in reversed(order):
        for v in g[u]:
            if v == parent[u]:
                continue
            h = down1[v] + 1
            if h > down1[u]:
                down1[u], down2[u], best_child[u] = h, down1[u], v
            elif h > down2[u]:
                down2[u] = h
    up = [0] * n  # longest path that leaves the node through its parent
    for u in order:
        for v in g[u]:
            if v != parent[u]:
                sideways = down2[u] if best_child[u] == v else down1[u]
                up[v] = 1 + max(up[u], sideways)
    return [max(down1[i], up[i]) for i in range(n)]


# ------------------------------------------------------------------------ tests


def _brute(n, edges):
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    sums, ecc = [], []
    for s in range(n):
        dist, q = {s: 0}, deque([s])
        while q:
            u = q.popleft()
            for v in g[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        sums.append(sum(dist.values()))
        ecc.append(max(dist.values()))
    return sums, ecc


def _random_edges(rng, n):
    """A random labelled tree: node i attaches to an earlier node, then relabel."""
    label = list(range(n))
    rng.shuffle(label)
    return [(label[i], label[rng.randrange(i)]) for i in range(1, n)]


def test_known():
    edges = [(0, 1), (0, 2), (2, 3), (2, 4), (2, 5)]
    assert sum_of_distances(6, edges) == [8, 12, 6, 10, 10, 10]
    assert eccentricities(6, edges) == [2, 3, 2, 3, 3, 3]


def test_single_and_pair():
    assert sum_of_distances(1, []) == [0] and eccentricities(1, []) == [0]
    assert sum_of_distances(2, [(1, 0)]) == [1, 1] and eccentricities(2, [(0, 1)]) == [1, 1]


def test_matches_bfs_from_every_node():
    rng = random.Random(140)
    for _ in range(300):
        n = rng.randint(1, 40)
        edges = _random_edges(rng, n)
        sums, ecc = _brute(n, edges)
        assert sum_of_distances(n, edges) == sums
        assert eccentricities(n, edges) == ecc


def test_binary_trees_via_graph():
    # the section's trees, turned into an edge list over indices
    rng = random.Random(141)
    for _ in range(100):
        t = random_tree(rng, rng.randint(1, 30))
        g = to_graph(t)
        idx = {node: i for i, node in enumerate(g)}
        edges = [(idx[a], idx[b]) for a in g for b in g[a] if idx[a] < idx[b]]
        n = len(g)
        assert (sum_of_distances(n, edges), eccentricities(n, edges)) == _brute(n, edges)


def test_path_both_directions_and_deep():
    # a path is the "skewed tree" of the edge-list world: rooted at node 0 it
    # is one long chain; labelled 2-0-4-1-3, node 0 roots it off-centre
    assert sum_of_distances(5, [(i, i + 1) for i in range(4)]) == [10, 7, 6, 7, 10]
    assert eccentricities(5, [(i, i + 1) for i in range(4)]) == [4, 3, 2, 3, 4]
    mixed = [(2, 0), (0, 4), (4, 1), (1, 3)]
    assert sum_of_distances(5, mixed) == [7, 7, 10, 10, 6]
    assert eccentricities(5, mixed) == [3, 3, 4, 4, 2]
    # a 10^5-node path: node i is 1..i away on one side, 1..n-1-i on the other
    n = 100_000
    edges = [(i, i + 1) for i in range(n - 1)]
    tri = lambda m: m * (m + 1) // 2
    assert sum_of_distances(n, edges) == [tri(i) + tri(n - 1 - i) for i in range(n)]
    assert eccentricities(n, edges) == [max(i, n - 1 - i) for i in range(n)]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
