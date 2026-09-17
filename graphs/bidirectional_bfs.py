"""Bidirectional BFS — search from both ends and meet in the middle.

Signs: both the start and the target are known, the branching factor is high,
       and you only need the shortest *distance* (or one shortest path).
Approach: keep a frontier at each end and always expand the smaller one. A
          one-sided search at depth d touches about b^d nodes; two searches
          that meet halfway touch about 2 x b^(d/2). For b = 10 and d = 6 that
          is 10^6 versus 2000.
Complexity: O(b^(d/2)) instead of O(b^d), same O(V + E) worst case.
Gotchas:
  - You must be able to walk edges *backwards*. On an undirected graph that is
    free; on a directed graph the back search needs the reversed adjacency, and
    passing the forward one silently returns wrong answers.
  - Do not return on the first meeting node found mid-level. Several nodes in
    one expansion can touch the other side at different depths, so the whole
    level has to be scanned and the minimum taken.
  - Not worth it for small graphs — the bookkeeping costs more than it saves.

Run the tests at the bottom with:  python3 graphs/bidirectional_bfs.py
"""


# ---------------------------------------------------------------- implementation


def bidirectional_distance(start, target, neighbors, back_neighbors=None):
    """Shortest distance in edges, or -1.

    neighbors      : state -> iterable of successors
    back_neighbors : predecessors; defaults to `neighbors`, which is only
                     correct when the graph is undirected.

    Each side keeps its own distance map. When an expansion generates a node
    the other side has already reached, the total is this side's depth + 1 plus
    the depth the other side recorded for it.
    """
    if start == target:
        return 0
    back_neighbors = back_neighbors or neighbors

    dist_f, dist_b = {start: 0}, {target: 0}
    front, back = [start], [target]
    step_f, step_b = neighbors, back_neighbors
    df = db = 0

    while front and back:
        if len(front) > len(back):  # always expand the cheaper side
            front, back = back, front
            dist_f, dist_b = dist_b, dist_f
            step_f, step_b = step_b, step_f
            df, db = db, df

        nxt, best = [], None
        for u in front:
            for v in step_f(u):
                if v in dist_b:
                    total = df + 1 + dist_b[v]
                    if best is None or total < best:
                        best = total
                if v not in dist_f:
                    dist_f[v] = df + 1
                    nxt.append(v)
        if best is not None:
            return best
        front = nxt
        df += 1

    return -1


def bidirectional_meeting_node(start, target, neighbors):
    """(distance, meeting_node) on an undirected graph, or (-1, None).

    The meeting node is what you need if you want to rebuild the actual path:
    walk parent links outward from it towards each end.
    """
    if start == target:
        return 0, start

    dist_f, dist_b = {start: 0}, {target: 0}
    front, back = [start], [target]
    df = db = 0

    while front and back:
        if len(front) > len(back):
            front, back = back, front
            dist_f, dist_b = dist_b, dist_f
            df, db = db, df

        nxt, best, meet = [], None, None
        for u in front:
            for v in neighbors(u):
                if v in dist_b:
                    total = df + 1 + dist_b[v]
                    if best is None or total < best:
                        best, meet = total, v
                if v not in dist_f:
                    dist_f[v] = df + 1
                    nxt.append(v)
        if best is not None:
            return best, meet
        front = nxt
        df += 1

    return -1, None


# ------------------------------------------------------------------------ tests


def test_straight_path():
    g = {i: [j for j in (i - 1, i + 1) if 0 <= j < 6] for i in range(6)}
    assert bidirectional_distance(0, 5, lambda u: g[u]) == 5
    assert bidirectional_distance(0, 0, lambda u: g[u]) == 0
    assert bidirectional_distance(2, 3, lambda u: g[u]) == 1


def test_unreachable():
    g = {0: [1], 1: [0], 2: [3], 3: [2]}
    assert bidirectional_distance(0, 3, lambda u: g[u]) == -1


def test_matches_plain_bfs_on_random_undirected_graphs():
    import random

    from bfs import bfs_distances
    from modeling import build_graph

    random.seed(31)
    for _ in range(60):
        n = random.randint(2, 14)
        edges = [
            (u, v) for u in range(n) for v in range(u + 1, n) if random.random() < 0.25
        ]
        g = build_graph(n, edges)
        dist = bfs_distances(g, 0)
        for target in range(n):
            want = dist.get(target, -1)
            assert bidirectional_distance(0, target, lambda u: g[u]) == want


def test_directed_needs_the_reversed_adjacency():
    from modeling import build_graph

    edges = [(0, 1), (1, 2), (2, 3)]
    fwd = build_graph(4, edges, directed=True)
    rev = build_graph(4, [(v, u) for u, v in edges], directed=True)

    assert bidirectional_distance(0, 3, lambda u: fwd[u], lambda u: rev[u]) == 3
    # nothing points back out of 3, so the reverse direction is unreachable
    assert bidirectional_distance(3, 0, lambda u: fwd[u], lambda u: rev[u]) == -1


def test_matches_plain_bfs_on_random_directed_graphs():
    import random

    from bfs import bfs_distances
    from modeling import build_graph

    random.seed(37)
    for _ in range(40):
        n = random.randint(2, 12)
        edges = [
            (u, v)
            for u in range(n)
            for v in range(n)
            if u != v and random.random() < 0.2
        ]
        fwd = build_graph(n, edges, directed=True)
        rev = build_graph(n, [(v, u) for u, v in edges], directed=True)
        dist = bfs_distances(fwd, 0)
        for target in range(n):
            got = bidirectional_distance(0, target, lambda u: fwd[u], lambda u: rev[u])
            assert got == dist.get(target, -1)


def test_meeting_node_is_on_a_shortest_path():
    from bfs import bfs_distances
    from modeling import build_graph

    g = build_graph(7, [(i, i + 1) for i in range(6)])
    d, meet = bidirectional_meeting_node(0, 6, lambda u: g[u])
    assert d == 6
    # the meeting node splits the path: distance through it is the total
    assert bfs_distances(g, 0)[meet] + bfs_distances(g, 6)[meet] == d


def test_pays_off_on_a_high_branching_factor():
    # The 4-wheel lock: 10^4 states, 8 neighbours each. Reaching "9999" from
    # "0000" is 4 moves, and the two-sided search expands far fewer states.
    def neighbors(s):
        for i in range(4):
            d = int(s[i])
            for nd in ((d + 1) % 10, (d - 1) % 10):
                yield s[:i] + str(nd) + s[i + 1:]

    assert bidirectional_distance("0000", "9999", neighbors) == 4
    assert bidirectional_distance("0000", "5555", neighbors) == 20


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
