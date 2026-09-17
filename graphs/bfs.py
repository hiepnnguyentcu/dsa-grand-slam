"""Breadth-first search — iterative and recursive.

Signs: minimum number of steps/moves/edits, nearest target, level-by-level
       processing, "shortest path" where every edge costs the same.
Approach: expand the graph in rings around the source. Everything at distance
          d is visited before anything at distance d + 1, so the first time a
          node is reached is via a shortest path.
Complexity: O(V + E) time, O(V) space.
Gotchas: mark a node seen when you *enqueue* it, not when you dequeue it —
         otherwise a node reachable from several nodes in the same ring gets
         queued multiple times and the queue blows up.

Graphs are plain adjacency dicts: {node: [neighbour, ...]}. Neighbours are
read with g.get(u, ()) so sink nodes need no entry of their own.

Run the tests at the bottom with:  python3 graphs/bfs.py
"""

from collections import deque


# ---------------------------------------------------------------- implementation


def bfs_iterative(g, start):
    """BFS traversal. Returns nodes in the order they were visited."""
    seen, order, q = {start}, [], deque([start])
    while q:
        u = q.popleft()
        order.append(u)
        for v in g.get(u, ()):
            if v not in seen:
                seen.add(v)
                q.append(v)
    return order


def bfs_recursive(g, start):
    """BFS traversal, recursing one frame per *level* rather than per node.

    BFS has no natural recursive form — its state is a queue, not a stack, so
    the call stack cannot stand in for it the way it does in DFS. What does
    work is recursing on the frontier: given every node at distance d, compute
    every node at distance d + 1 and recurse on that.

    Recursion depth is the eccentricity of `start` (its longest shortest-path
    distance), not V — so this is much harder to overflow than a recursive
    DFS, though a long path graph will still do it.
    """
    seen, order = {start}, []

    def visit(frontier):
        if not frontier:
            return
        nxt = []
        for u in frontier:
            order.append(u)
            for v in g.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    nxt.append(v)
        visit(nxt)

    visit([start])
    return order


def bfs_levels(g, start):
    """Nodes grouped by distance: levels[d] == the nodes at distance d.

    The same frontier expansion as bfs_recursive, kept iterative and with the
    rings preserved instead of flattened. This is the shape you want whenever
    the question is per-level ("how many rounds", "the last row reached").
    """
    seen, levels, frontier = {start}, [], [start]
    while frontier:
        levels.append(frontier)
        nxt = []
        for u in frontier:
            for v in g.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    nxt.append(v)
        frontier = nxt
    return levels


def bfs_distances(g, start):
    """Shortest-path distance in edges from start to every reachable node.

    Unreachable nodes are simply absent from the returned dict.
    """
    dist, q = {start: 0}, deque([start])
    while q:
        u = q.popleft()
        for v in g.get(u, ()):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def bfs_shortest_path(g, src, dst):
    """One shortest src -> dst path as a list of nodes, or None if unreachable.

    Records the node each node was first reached from, then walks those parent
    links back from dst. `parent` doubles as the seen set, so there is no
    second structure to keep in sync.
    """
    parent = {src: None}
    q = deque([src])
    while q:
        u = q.popleft()
        if u == dst:
            path = []
            while u is not None:
                path.append(u)
                u = parent[u]
            return path[::-1]
        for v in g.get(u, ()):
            if v not in parent:
                parent[v] = u
                q.append(v)
    return None


# ------------------------------------------------------------------------ tests

#     3       5           (7 --- 8 is a separate component)
#     |       |
#     0 --- 2 --- 4 --- 6
#     |           |
#     1 ----------+
GRAPH = {
    0: [1, 2, 3],
    1: [0, 4],
    2: [0, 4, 5],
    3: [0],
    4: [1, 2, 6],
    5: [2],
    6: [4],
    7: [8],
    8: [7],
}


def test_visits_ring_by_ring():
    assert bfs_iterative(GRAPH, 0) == [0, 1, 2, 3, 4, 5, 6]


def test_recursive_matches_iterative():
    for start in GRAPH:
        assert bfs_recursive(GRAPH, start) == bfs_iterative(GRAPH, start)


def test_levels_group_by_distance():
    assert bfs_levels(GRAPH, 0) == [[0], [1, 2, 3], [4, 5], [6]]
    # flattening the levels is exactly the traversal order
    assert [u for lvl in bfs_levels(GRAPH, 0) for u in lvl] == bfs_iterative(GRAPH, 0)


def test_distances():
    assert bfs_distances(GRAPH, 0) == {0: 0, 1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3}
    # nodes in the other component never appear
    assert 7 not in bfs_distances(GRAPH, 0)
    # distance d is the index of the level containing the node
    for d, level in enumerate(bfs_levels(GRAPH, 0)):
        for u in level:
            assert bfs_distances(GRAPH, 0)[u] == d


def test_shortest_path():
    path = bfs_shortest_path(GRAPH, 0, 6)
    assert path == [0, 1, 4, 6]
    # it is a real walk, and its length matches the computed distance
    assert all(b in GRAPH[a] for a, b in zip(path, path[1:]))
    assert len(path) - 1 == bfs_distances(GRAPH, 0)[6]


def test_path_to_self_and_to_unreachable():
    assert bfs_shortest_path(GRAPH, 4, 4) == [4]
    assert bfs_shortest_path(GRAPH, 0, 7) is None


def test_isolated_node():
    assert bfs_iterative({0: []}, 0) == [0]
    assert bfs_recursive({}, "lonely") == ["lonely"]  # no adjacency entry at all


def test_directed_edges_are_one_way():
    g = {0: [1], 1: [2], 2: []}
    assert bfs_distances(g, 0) == {0: 0, 1: 1, 2: 2}
    assert bfs_distances(g, 2) == {2: 0}


def test_diamond_takes_the_shorter_side():
    # 0 -> 1 -> 3  (two hops)  vs  0 -> 2 -> 4 -> 3  (three hops)
    g = {0: [2, 1], 1: [3], 2: [4], 3: [], 4: [3]}
    assert bfs_shortest_path(g, 0, 3) == [0, 1, 3]
    assert bfs_distances(g, 0)[3] == 2


def test_iterative_survives_depth_that_overflows_recursion():
    # One level per node, so recursion depth grows with n. Same cliff the
    # recursive DFS hits, just reached only by long-and-thin graphs.
    n = 10_000
    path = {i: [i + 1] for i in range(n - 1)}
    assert len(bfs_iterative(path, 0)) == n
    assert bfs_distances(path, 0)[n - 1] == n - 1

    try:
        bfs_recursive(path, 0)
    except RecursionError:
        pass
    else:
        raise AssertionError("expected bfs_recursive to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
