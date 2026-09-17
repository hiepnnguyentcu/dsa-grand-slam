"""Bridges and articulation points — Tarjan's low-link DFS.

Signs: "critical connections", single points of failure, an edge or node whose
       removal disconnects the network, finding 2-edge-connected components.
Approach: DFS numbers each node with a discovery time disc[u]. low[u] is the
          smallest discovery time reachable from u's subtree using tree edges
          plus at most one back edge — in other words, how far back up the tree
          the subtree can escape to without going through u.
    bridge:             tree edge (u, v) where low[v] >  disc[u]
                        (v's subtree has no way back past u -- cut it and v's
                         side is stranded)
    articulation point: non-root u with a child v where low[v] >= disc[u]
                        (v's subtree can reach u at best, never above it)
                        root u: an articulation point iff it has >= 2 children
Complexity: O(V + E).
Gotchas:
  - The >= vs > distinction is the whole difference between the two answers.
    Equality means the subtree can reach *u itself* but no higher: removing the
    node disconnects it, removing the edge does not.
  - Skipping "the parent" by node id breaks with parallel edges — two edges
    between u and v mean neither is a bridge. Track the parent *edge id*, which
    is what the bridge code below does.
  - The root is special-cased for articulation points and only for those.
  - Recursive, so it inherits Python's ~1000-frame limit.

Run the tests at the bottom with:  python3 graphs/bridges_articulation.py
"""


# ---------------------------------------------------------------- implementation


def bridges(n, edges):
    """Edges whose removal increases the number of connected components."""
    g = {u: [] for u in range(n)}
    for i, (u, v) in enumerate(edges):
        g[u].append((v, i))
        g[v].append((u, i))

    disc, low = [-1] * n, [0] * n
    timer = [0]
    out = []

    def dfs(u, parent_edge):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        for v, eid in g[u]:
            if eid == parent_edge:
                continue  # by edge id, so parallel edges are not skipped
            if disc[v] == -1:
                dfs(v, eid)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    out.append(edges[eid])
            else:
                low[u] = min(low[u], disc[v])

    for u in range(n):
        if disc[u] == -1:
            dfs(u, -1)
    return out


def articulation_points(n, edges):
    """Nodes whose removal increases the number of connected components."""
    g = {u: [] for u in range(n)}
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)

    disc, low = [-1] * n, [0] * n
    timer = [0]
    out = set()

    def dfs(u, parent):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        children = 0
        for v in g[u]:
            if v == parent:
                continue
            if disc[v] == -1:
                children += 1
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if parent != -1 and low[v] >= disc[u]:
                    out.add(u)
            else:
                low[u] = min(low[u], disc[v])
        if parent == -1 and children > 1:
            out.add(u)  # the root only qualifies with two independent subtrees

    for u in range(n):
        if disc[u] == -1:
            dfs(u, -1)
    return sorted(out)


# ------------------------------------------------------------------------ tests


def components(n, edges):
    """Reference count of connected components, via DSU."""
    from union_find import DSU

    d = DSU(n)
    for u, v in edges:
        d.union(u, v)
    return d.count


def brute_force_bridges(n, edges):
    """Remove each edge and see whether the graph falls apart."""
    base = components(n, edges)
    return [
        e for i, e in enumerate(edges)
        if components(n, edges[:i] + edges[i + 1:]) > base
    ]


def brute_force_articulation(n, edges):
    """Remove each node and see whether the rest falls apart.

    Deleting x drops its own component and replaces it with however many pieces
    it was holding together, so the count rises iff that number is 2 or more.
    """
    base = components(n, edges)
    out = []
    for x in range(n):
        rest = [u for u in range(n) if u != x]
        index = {u: i for i, u in enumerate(rest)}
        kept = [(index[u], index[v]) for u, v in edges if u != x and v != x]
        if components(len(rest), kept) > base:
            out.append(x)
    return out


def test_critical_connection():
    n, edges = 4, [(0, 1), (1, 2), (2, 0), (1, 3)]
    assert bridges(n, edges) == [(1, 3)]         # the triangle has no bridge
    assert articulation_points(n, edges) == [1]


def test_chain_is_all_bridges():
    edges = [(0, 1), (1, 2), (2, 3)]
    assert sorted(bridges(4, edges)) == sorted(edges)
    assert articulation_points(4, edges) == [1, 2]  # not the two endpoints


def test_cycle_has_neither():
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    assert bridges(4, edges) == []
    assert articulation_points(4, edges) == []


def test_single_edge():
    assert bridges(2, [(0, 1)]) == [(0, 1)]
    assert articulation_points(2, [(0, 1)]) == []  # removing either leaves one node


def test_no_edges():
    assert bridges(3, []) == []
    assert articulation_points(3, []) == []


def test_parallel_edges_are_not_bridges():
    # Two separate roads between the same pair: losing one changes nothing.
    assert bridges(2, [(0, 1), (0, 1)]) == []
    assert bridges(2, [(0, 1)]) == [(0, 1)]


def test_root_needs_two_children():
    # 0 is the DFS root but has a single subtree hanging off it, so it is not
    # an articulation point; 1 is.
    edges = [(0, 1), (1, 2), (1, 3)]
    assert articulation_points(4, edges) == [1]
    # now the root really does hold two halves together
    assert articulation_points(3, [(1, 0), (0, 2)]) == [0]


def test_articulation_without_a_bridge():
    # Two triangles sharing node 2: removing the node splits them, but every
    # edge sits on a cycle so nothing is a bridge. This is the >= vs > case.
    edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 2)]
    assert bridges(5, edges) == []
    assert articulation_points(5, edges) == [2]


def test_disconnected_components_handled_separately():
    edges = [(0, 1), (1, 2), (3, 4)]
    assert sorted(bridges(5, edges)) == [(0, 1), (1, 2), (3, 4)]
    assert articulation_points(5, edges) == [1]


def test_matches_brute_force_on_random_graphs():
    import random

    random.seed(89)
    for _ in range(60):
        n = random.randint(2, 9)
        edges = [
            (u, v) for u in range(n) for v in range(u + 1, n) if random.random() < 0.3
        ]
        assert sorted(bridges(n, edges)) == sorted(brute_force_bridges(n, edges))
        assert articulation_points(n, edges) == brute_force_articulation(n, edges)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
