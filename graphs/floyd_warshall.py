"""Floyd-Warshall — all-pairs shortest paths in three nested loops.

Signs: distances between *every* pair, V small (roughly <= 400), transitive
       closure, "the city with the fewest neighbours within distance d", many
       repeated distance queries on a static graph.
Approach: d[i][j] improves by routing through some intermediate node k. Fix the
          set of allowed intermediates to {0..k} and grow it one node at a time:
          after round k, d[i][j] is the best path whose interior nodes all come
          from that set. After the last round the set is every node, so d is
          final.
Complexity: O(V^3) time, O(V^2) space.
Gotchas:
  - `k` MUST be the outermost loop. With k innermost the invariant collapses and
    the answers are silently wrong. This is the single classic bug.
  - Negative edges are fine; negative *cycles* are not. They show up as
    d[i][i] < 0, which is a cheap and worthwhile check.
  - At V = 1000 this is 10^9 operations. Run Dijkstra from each source instead
    (O(V x E log V)) once the graph is sparse.

Run the tests at the bottom with:  python3 graphs/floyd_warshall.py
"""

INF = float("inf")


# ---------------------------------------------------------------- implementation


def floyd_warshall(n, edges, directed=True):
    """All-pairs distance matrix. Edges are (u, v, w); parallel edges collapse."""
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        if w < d[u][v]:
            d[u][v] = w
        if not directed and w < d[v][u]:
            d[v][u] = w

    for k in range(n):          # intermediates allowed so far: {0..k}
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik == INF:
                continue        # i cannot reach k, so k is no help to i
            di = d[i]
            for j in range(n):
                if dik + dk[j] < di[j]:
                    di[j] = dik + dk[j]
    return d


def floyd_warshall_paths(n, edges, directed=True):
    """(dist, nxt) where nxt[i][j] is the first hop on a shortest i -> j path."""
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    nxt = [[None] * n for _ in range(n)]
    for i in range(n):
        nxt[i][i] = i

    def put(u, v, w):
        if w < d[u][v]:
            d[u][v] = w
            nxt[u][v] = v

    for u, v, w in edges:
        put(u, v, w)
        if not directed:
            put(v, u, w)

    for k in range(n):
        for i in range(n):
            if d[i][k] == INF:
                continue
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
                    nxt[i][j] = nxt[i][k]  # same first hop as the route to k
    return d, nxt


def reconstruct_path(nxt, i, j):
    """The node list of a shortest i -> j path, or None if there is none."""
    if nxt[i][j] is None:
        return None
    path = [i]
    while i != j:
        i = nxt[i][j]
        path.append(i)
    return path


def has_negative_cycle(dist):
    """A node cheaper to reach from itself than 0 is sitting on a negative cycle."""
    return any(dist[i][i] < 0 for i in range(len(dist)))


def transitive_closure(n, edges, directed=True):
    """reach[i][j] = can i get to j at all. Floyd-Warshall with OR for +.

    Same three loops, booleans instead of distances — sometimes called Warshall's
    algorithm, and the cheapest way to answer many reachability queries at once.
    """
    reach = [[i == j for j in range(n)] for i in range(n)]
    for u, v in edges:
        reach[u][v] = True
        if not directed:
            reach[v][u] = True

    for k in range(n):
        for i in range(n):
            if not reach[i][k]:
                continue
            rk = reach[k]
            ri = reach[i]
            for j in range(n):
                if rk[j]:
                    ri[j] = True
    return reach


# ------------------------------------------------------------------------ tests


def test_basic_all_pairs():
    edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1)]
    d = floyd_warshall(4, edges)
    assert d[0] == [0, 3, 1, 4]   # 0->2->1 is cheaper than 0->1
    assert d[2] == [INF, 2, 0, 3]
    assert d[3] == [INF, INF, INF, 0]


def test_diagonal_is_zero_and_self_loops_do_not_help():
    d = floyd_warshall(3, [(0, 0, 5), (0, 1, 1)])
    assert [d[i][i] for i in range(3)] == [0, 0, 0]


def test_undirected_is_symmetric():
    d = floyd_warshall(4, [(0, 1, 1), (1, 2, 2), (2, 3, 3)], directed=False)
    assert all(d[i][j] == d[j][i] for i in range(4) for j in range(4))
    assert d[0][3] == 6


def test_agrees_with_dijkstra_from_every_source():
    import random

    from dijkstra import dijkstra

    random.seed(59)
    for _ in range(25):
        n = random.randint(2, 10)
        edges = [
            (u, v, random.randint(0, 15))
            for u in range(n)
            for v in range(n)
            if u != v and random.random() < 0.3
        ]
        g = {u: [] for u in range(n)}
        for u, v, w in edges:
            g[u].append((v, w))
        d = floyd_warshall(n, edges)
        for src in range(n):
            assert d[src] == dijkstra(n, g, src)


def test_negative_edges_without_a_cycle():
    edges = [(0, 1, 5), (1, 2, -3), (0, 2, 4)]
    d = floyd_warshall(3, edges)
    assert d[0][2] == 2  # 5 - 3 beats the direct 4
    assert has_negative_cycle(d) is False


def test_negative_cycle_shows_on_the_diagonal():
    edges = [(0, 1, 1), (1, 2, -1), (2, 1, -1)]
    d = floyd_warshall(3, edges)
    assert has_negative_cycle(d) is True
    assert d[1][1] < 0


def test_k_must_be_the_outer_loop():
    # The same relaxation with k innermost -- the classic bug -- and a graph
    # where it gets the answer wrong.
    def broken(n, edges):
        d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
        for u, v, w in edges:
            d[u][v] = min(d[u][v], w)
        for i in range(n):
            for j in range(n):
                for k in range(n):  # WRONG position
                    if d[i][k] + d[k][j] < d[i][j]:
                        d[i][j] = d[i][k] + d[k][j]
        return d

    # 0 -> 2 -> 3 -> 1. With k innermost, the pair (0, 1) is finalised before
    # d[2][1] has been discovered, so the route through 2 is never seen. Note a
    # simple forward chain would NOT expose this -- the bug needs the useful
    # intermediate to be found after the pair that needs it.
    edges = [(0, 2, 1), (2, 3, 1), (3, 1, 1)]
    assert floyd_warshall(4, edges)[0][1] == 3
    assert broken(4, edges)[0][1] == INF  # silently wrong, no error raised


def test_path_reconstruction():
    edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1)]
    d, nxt = floyd_warshall_paths(4, edges)
    assert d[0][3] == 4
    path = reconstruct_path(nxt, 0, 3)
    assert path == [0, 2, 1, 3]

    weights = {(u, v): w for u, v, w in edges}
    assert sum(weights[(a, b)] for a, b in zip(path, path[1:])) == d[0][3]
    assert reconstruct_path(nxt, 3, 0) is None   # no route back
    assert reconstruct_path(nxt, 2, 2) == [2]    # trivial path


def test_paths_agree_with_plain_distances():
    import random

    random.seed(61)
    for _ in range(20):
        n = random.randint(2, 8)
        edges = [
            (u, v, random.randint(1, 9))
            for u in range(n)
            for v in range(n)
            if u != v and random.random() < 0.3
        ]
        d1 = floyd_warshall(n, edges)
        d2, nxt = floyd_warshall_paths(n, edges)
        assert d1 == d2
        weights = {}
        for u, v, w in edges:
            weights[(u, v)] = min(w, weights.get((u, v), INF))
        for i in range(n):
            for j in range(n):
                path = reconstruct_path(nxt, i, j)
                if d1[i][j] == INF:
                    assert path is None
                else:
                    cost = sum(weights[(a, b)] for a, b in zip(path, path[1:]))
                    assert cost == d1[i][j]


def test_transitive_closure_matches_bfs():
    import random

    from bfs import bfs_distances
    from modeling import build_graph

    random.seed(67)
    for _ in range(25):
        n = random.randint(2, 10)
        edges = [
            (u, v) for u in range(n) for v in range(n)
            if u != v and random.random() < 0.2
        ]
        reach = transitive_closure(n, edges)
        g = build_graph(n, edges, directed=True)
        for i in range(n):
            seen = bfs_distances(g, i)
            for j in range(n):
                assert reach[i][j] == (j in seen)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
