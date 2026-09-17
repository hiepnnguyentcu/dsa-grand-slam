"""Modelling a problem as a graph — representations and neighbour generation.

Signs: relationships, dependencies, transformations between states, moves on a
       board, "can you get from A to B".
Approach: decide explicitly what a *node* is, what an *edge* is, and whether
          edges are directed and/or weighted. For implicit graphs (grids, word
          transformations, puzzle states) don't build an adjacency structure at
          all — generate neighbours on demand.
Representations:
    adjacency list   — the default. O(V + E) space, O(deg u) to scan a node.
    adjacency matrix — dense graphs, or when you need O(1) "is u-v an edge".
                       O(V^2) space.
    edge list        — what Kruskal and Bellman-Ford actually want.
Gotchas: clarify directed vs undirected, self-loops, duplicate/parallel edges,
         0- vs 1-indexing, and whether the graph is connected. Most graph bugs
         are modelling bugs, not algorithm bugs.

Conventions used throughout this package:
    unweighted adjacency  {u: [v, ...]}
    weighted adjacency    {u: [(v, w), ...]}
    edge list             [(u, v)] or [(u, v, w)]   -- weight always last

Run the tests at the bottom with:  python3 graphs/modeling.py
"""


# ---------------------------------------------------------------- implementation


def build_graph(n, edges, directed=False, weighted=False):
    """Adjacency dict over nodes 0..n-1. Every node gets a key, even if isolated."""
    g = {u: [] for u in range(n)}
    for e in edges:
        u, v = e[0], e[1]
        w = e[2] if weighted else None
        g[u].append((v, w) if weighted else v)
        if not directed:
            g[v].append((u, w) if weighted else u)
    return g


def build_matrix(n, edges, directed=False, weighted=False, absent=0):
    """Adjacency matrix. m[u][v] is the weight (or 1) if the edge exists.

    Parallel edges collapse — the cheapest one wins when weighted, which is
    what shortest-path algorithms want anyway.
    """
    m = [[absent] * n for _ in range(n)]

    def put(u, v, w):
        if m[u][v] == absent or (weighted and w < m[u][v]):
            m[u][v] = w

    for e in edges:
        u, v = e[0], e[1]
        w = e[2] if weighted else 1
        put(u, v, w)
        if not directed:
            put(v, u, w)
    return m


def to_edge_list(g, weighted=False, directed=False):
    """Flatten an adjacency dict back to an edge list.

    For an undirected graph each edge is stored twice in the adjacency dict, so
    only the u < v copy is emitted unless `directed` is set.
    """
    edges = []
    for u, nbrs in g.items():
        for item in nbrs:
            v, w = item if weighted else (item, None)
            if not directed and not u < v:
                continue
            edges.append((u, v, w) if weighted else (u, v))
    return edges


DIRS4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
DIRS8 = DIRS4 + ((-1, -1), (-1, 1), (1, -1), (1, 1))


def grid_neighbors(r, c, R, C, dirs=DIRS4):
    """Yield the in-bounds neighbours of (r, c). The implicit-graph workhorse.

    Nothing is stored: a grid is a graph with R*C nodes and up to 4*R*C edges,
    and materialising that adjacency is pure waste.
    """
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if 0 <= nr < R and 0 <= nc < C:
            yield nr, nc


# ------------------------------------------------------------------------ tests


def test_undirected_edges_go_both_ways():
    g = build_graph(3, [(0, 1), (1, 2)])
    assert g == {0: [1], 1: [0, 2], 2: [1]}


def test_directed_edges_go_one_way():
    g = build_graph(3, [(0, 1), (1, 2)], directed=True)
    assert g == {0: [1], 1: [2], 2: []}


def test_isolated_nodes_still_get_a_key():
    assert build_graph(3, [(0, 1)]) == {0: [1], 1: [0], 2: []}


def test_weighted_adjacency():
    g = build_graph(3, [(0, 1, 5), (1, 2, 7)], directed=True, weighted=True)
    assert g == {0: [(1, 5)], 1: [(2, 7)], 2: []}


def test_matrix_matches_adjacency():
    edges = [(0, 1, 5), (1, 2, 7)]
    m = build_matrix(3, edges, weighted=True)
    assert m[0][1] == m[1][0] == 5
    assert m[1][2] == m[2][1] == 7
    assert m[0][2] == 0  # absent


def test_matrix_keeps_the_cheapest_parallel_edge():
    m = build_matrix(2, [(0, 1, 9), (0, 1, 4)], weighted=True)
    assert m[0][1] == 4


def test_edge_list_round_trip():
    edges = [(0, 1), (1, 2), (0, 2)]
    assert sorted(to_edge_list(build_graph(3, edges))) == sorted(edges)

    wedges = [(0, 1, 5), (1, 2, 7)]
    g = build_graph(3, wedges, weighted=True)
    assert sorted(to_edge_list(g, weighted=True)) == sorted(wedges)


def test_grid_neighbors_bounds():
    assert sorted(grid_neighbors(0, 0, 3, 3)) == [(0, 1), (1, 0)]          # corner
    assert len(list(grid_neighbors(1, 1, 3, 3))) == 4                       # middle
    assert len(list(grid_neighbors(0, 1, 3, 3))) == 3                       # edge
    assert len(list(grid_neighbors(1, 1, 3, 3, DIRS8))) == 8
    assert len(list(grid_neighbors(0, 0, 3, 3, DIRS8))) == 3
    assert list(grid_neighbors(0, 0, 1, 1)) == []                           # 1x1


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
