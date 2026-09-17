"""Minimum spanning tree — Kruskal (edge-driven) and Prim (node-driven).

Signs: connect every node at minimum total cost, "cheapest network / wiring /
       roads", "minimum cost to connect all points".
Approach: both are greedy, and both are correct for the same reason — the cut
          property. For any split of the nodes into two sides, the cheapest edge
          crossing that split belongs to some MST. Kruskal takes cheap edges
          globally and uses DSU to skip the ones that would close a cycle; Prim
          grows one tree and always takes the cheapest edge leaving it.
Complexity: Kruskal O(E log E), dominated by the sort.
            Prim O(E log V) with a heap, or O(V^2) with an array scan.
Which to use: Kruskal when you already hold an edge list, or the graph is
              sparse. Prim when the graph is dense or complete (V^2 edges make
              sorting them wasteful — the array version has no heap at all).
Gotchas:
  - A disconnected graph has no spanning tree. Both versions here report that
    rather than returning a partial forest.
  - An MST is not unique when weights tie, so tests compare *total cost*, not
    the edge set.
  - Maximum spanning tree: negate the weights, nothing else changes.

Run the tests at the bottom with:  python3 graphs/mst.py
"""

import heapq

from union_find import DSU


# ---------------------------------------------------------------- implementation


def kruskal(n, edges):
    """(total_weight, tree_edges), or (-1, []) if the graph is disconnected.

    `d.union` returning False is precisely "this edge closes a cycle", so the
    DSU is doing the cycle check for free as it goes.
    """
    d = DSU(n)
    total, tree = 0, []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if d.union(u, v):
            total += w
            tree.append((u, v, w))
            if len(tree) == n - 1:
                break
    return (total, tree) if len(tree) == n - 1 else (-1, [])


def prim_heap(n, g, start=0):
    """(total_weight, tree_edges) from an adjacency dict g[u] = [(v, w), ...].

    The heap holds candidate edges leaving the tree. Popping one whose endpoint
    is already in the tree means it has been superseded — the same stale-entry
    situation as Dijkstra, handled the same way.
    """
    if n == 1:
        return 0, []
    in_tree = [False] * n
    total, tree = 0, []
    pq = [(0, start, -1)]
    while pq:
        w, u, parent = heapq.heappop(pq)
        if in_tree[u]:
            continue
        in_tree[u] = True
        total += w
        if parent != -1:
            tree.append((parent, u, w))
        for v, wt in g.get(u, ()):
            if not in_tree[v]:
                heapq.heappush(pq, (wt, v, u))
    return (total, tree) if all(in_tree) else (-1, [])


def prim_dense(n, weight):
    """O(V^2) Prim for complete/dense graphs. `weight(u, v)` returns the cost.

    No heap and no edge list: on a complete graph there are V^2 edges, so
    scanning for the cheapest unattached node is the same order of work as
    looking at the edges once, and costs nothing to maintain.
    """
    INF = float("inf")
    in_tree = [False] * n
    best = [INF] * n
    best[0] = 0
    total = 0
    for _ in range(n):
        u = min((i for i in range(n) if not in_tree[i]), key=best.__getitem__)
        if best[u] == INF:
            return -1  # disconnected
        in_tree[u] = True
        total += best[u]
        for v in range(n):
            if not in_tree[v]:
                w = weight(u, v)
                if w < best[v]:
                    best[v] = w
    return total


def min_cost_connect_points(points):
    """Cheapest way to connect all points under Manhattan distance.

    A complete graph on the points, so this is the case prim_dense exists for.
    """
    if len(points) <= 1:
        return 0
    manhattan = lambda u, v: abs(points[u][0] - points[v][0]) + abs(
        points[u][1] - points[v][1]
    )
    return prim_dense(len(points), manhattan)


# ------------------------------------------------------------------------ tests


def as_adjacency(n, edges):
    g = {u: [] for u in range(n)}
    for u, v, w in edges:
        g[u].append((v, w))
        g[v].append((u, w))
    return g


def test_kruskal_simple():
    edges = [(0, 1, 1), (1, 2, 2), (0, 2, 3)]
    total, tree = kruskal(3, edges)
    assert total == 3                      # drops the 3-weight edge
    assert len(tree) == 2


def test_tree_edges_are_real_and_span_everything():
    edges = [(0, 1, 4), (0, 2, 1), (1, 2, 2), (1, 3, 5), (2, 3, 8)]
    total, tree = kruskal(4, edges)
    assert sum(w for _, _, w in tree) == total
    assert set(tree) <= set(edges)
    d = DSU(4)
    for u, v, _ in tree:
        d.union(u, v)
    assert d.count == 1                    # one component: it spans
    assert len(tree) == 3                  # and it is a tree: n-1 edges


def test_disconnected_has_no_spanning_tree():
    assert kruskal(4, [(0, 1, 1), (2, 3, 1)]) == (-1, [])
    assert prim_heap(4, as_adjacency(4, [(0, 1, 1), (2, 3, 1)])) == (-1, [])


def test_single_node_and_no_edges():
    assert kruskal(1, []) == (0, [])
    assert prim_heap(1, {0: []}) == (0, [])


def test_kruskal_and_prim_agree_on_random_graphs():
    import random

    random.seed(71)
    checked = 0
    while checked < 40:
        n = random.randint(2, 12)
        edges = [
            (u, v, random.randint(1, 30))
            for u in range(n)
            for v in range(u + 1, n)
            if random.random() < 0.4
        ]
        k_total, _ = kruskal(n, edges)
        p_total, _ = prim_heap(n, as_adjacency(n, edges))
        assert k_total == p_total
        if k_total != -1:
            checked += 1


def test_prim_start_node_does_not_change_the_cost():
    edges = [(0, 1, 4), (0, 2, 1), (1, 2, 2), (1, 3, 5), (2, 3, 8)]
    g = as_adjacency(4, edges)
    totals = {prim_heap(4, g, start)[0] for start in range(4)}
    assert len(totals) == 1


def test_matches_brute_force_over_all_spanning_trees():
    from itertools import combinations

    edges = [(0, 1, 4), (0, 2, 1), (1, 2, 2), (1, 3, 5), (2, 3, 8), (0, 3, 7)]
    n = 4
    best = None
    for combo in combinations(edges, n - 1):
        d = DSU(n)
        if all(d.union(u, v) for u, v, _ in combo):  # spans iff no edge wasted
            cost = sum(w for _, _, w in combo)
            best = cost if best is None else min(best, cost)
    assert kruskal(n, edges)[0] == best


def test_ties_may_give_different_trees_but_the_same_cost():
    edges = [(0, 1, 1), (1, 2, 1), (0, 2, 1)]
    assert kruskal(3, edges)[0] == prim_heap(3, as_adjacency(3, edges))[0] == 2


def test_connect_points():
    assert min_cost_connect_points([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]) == 20
    assert min_cost_connect_points([[3, 12], [-2, 5], [-4, 1]]) == 18


def test_connect_points_degenerate():
    assert min_cost_connect_points([]) == 0
    assert min_cost_connect_points([[1, 1]]) == 0
    assert min_cost_connect_points([[0, 0], [0, 5]]) == 5


def test_dense_prim_agrees_with_kruskal():
    import random

    random.seed(73)
    for _ in range(20):
        n = random.randint(2, 9)
        pts = [(random.randint(-20, 20), random.randint(-20, 20)) for _ in range(n)]
        edges = [
            (u, v, abs(pts[u][0] - pts[v][0]) + abs(pts[u][1] - pts[v][1]))
            for u in range(n)
            for v in range(u + 1, n)
        ]
        assert min_cost_connect_points(pts) == kruskal(n, edges)[0]


def test_maximum_spanning_tree_by_negating():
    edges = [(0, 1, 1), (1, 2, 5), (0, 2, 3)]
    total, _ = kruskal(3, [(u, v, -w) for u, v, w in edges])
    assert -total == 8  # 5 + 3, the two heaviest that still form a tree


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
