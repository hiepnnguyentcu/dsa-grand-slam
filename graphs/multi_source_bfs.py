"""Multi-source BFS — one sweep answers "distance to the *nearest* source".

Signs: distance to the closest of many sources, simultaneous spreading (fire,
       rot, infection, water), "time until everything is reached", "distance to
       the nearest 0".
Approach: seed the queue with *every* source at distance 0 before the loop
          starts. The rings then expand from all of them at once, so the first
          arrival at a cell necessarily came from its nearest source.
Complexity: O(V + E) total — not O(sources x (V + E)). This is the whole point:
            running a separate BFS per source and taking the min does the same
            job k times slower.
Gotchas: seed them all *before* the first pop. Seeding inside the loop, or one
         source at a time, silently degenerates into single-source BFS.

Run the tests at the bottom with:  python3 graphs/multi_source_bfs.py
"""

from collections import deque

from modeling import grid_neighbors


# ---------------------------------------------------------------- implementation


def multi_source_distances(g, sources):
    """Distance from each node to its nearest source. Unreachable nodes absent."""
    dist = {s: 0 for s in sources}
    q = deque(dist)
    while q:
        u = q.popleft()
        for v in g.get(u, ()):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def multi_source_origin(g, sources):
    """(dist, origin) — also records *which* source each node is nearest to.

    Ties are broken by whichever source's ring got there first, which depends
    on the order `sources` is given in. If ties matter, say so explicitly.
    """
    dist = {s: 0 for s in sources}
    origin = {s: s for s in sources}
    q = deque(dist)
    while q:
        u = q.popleft()
        for v in g.get(u, ()):
            if v not in dist:
                dist[v] = dist[u] + 1
                origin[v] = origin[u]
                q.append(v)
    return dist, origin


def grid_multi_source(grid, is_source, is_blocked):
    """Grid distances to the nearest source cell. -1 where never reached.

    `is_source` and `is_blocked` are predicates on the cell *value*, which
    keeps this reusable across the many problems that are this shape with
    different encodings.
    """
    R, C = len(grid), len(grid[0])
    dist = [[-1] * C for _ in range(R)]
    q = deque()
    for r in range(R):
        for c in range(C):
            if is_source(grid[r][c]):
                dist[r][c] = 0
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for nr, nc in grid_neighbors(r, c, R, C):
            if dist[nr][nc] == -1 and not is_blocked(grid[nr][nc]):
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist


def rotting_oranges(grid):
    """Minutes until no fresh orange remains, or -1. 0 empty, 1 fresh, 2 rotten.

    Every rotten orange spreads at the same time, so this is multi-source BFS
    and the answer is the largest distance any fresh orange ends up at.
    """
    dist = grid_multi_source(grid, lambda v: v == 2, lambda v: v == 0)
    minutes = 0
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == 1:
                if dist[r][c] == -1:
                    return -1  # walled off from every rotten orange
                minutes = max(minutes, dist[r][c])
    return minutes


def nearest_zero(mat):
    """Distance from every cell to the nearest 0. Sources are the zeros."""
    return grid_multi_source(mat, lambda v: v == 0, lambda v: False)


# ------------------------------------------------------------------------ tests


def test_seeding_all_sources_beats_the_nearest_one():
    from bfs import bfs_distances
    from modeling import build_graph

    # 0 -- 1 -- 2 -- 3 -- 4 -- 5, sources at both ends
    g = build_graph(6, [(i, i + 1) for i in range(5)])
    dist = multi_source_distances(g, [0, 5])
    assert dist == {0: 0, 1: 1, 2: 2, 3: 2, 4: 1, 5: 0}

    # equivalently: the min over separate single-source runs, but in one pass
    a, b = bfs_distances(g, 0), bfs_distances(g, 5)
    assert dist == {u: min(a[u], b[u]) for u in g}


def test_matches_min_of_single_source_runs_on_random_graphs():
    import random

    from bfs import bfs_distances
    from modeling import build_graph

    random.seed(17)
    for _ in range(30):
        n = random.randint(2, 12)
        edges = [(u, v) for u in range(n) for v in range(u + 1, n) if random.random() < 0.3]
        g = build_graph(n, edges)
        sources = random.sample(range(n), random.randint(1, n))

        got = multi_source_distances(g, sources)
        runs = [bfs_distances(g, s) for s in sources]
        want = {}
        for run in runs:
            for u, d in run.items():
                want[u] = min(want.get(u, d), d)
        assert got == want


def test_records_which_source_won():
    from modeling import build_graph

    g = build_graph(6, [(i, i + 1) for i in range(5)])
    dist, origin = multi_source_origin(g, [0, 5])
    assert origin[1] == 0 and origin[4] == 5
    assert origin[2] == 0 and origin[3] == 5  # the split happens in the middle


def test_single_source_is_just_bfs():
    from bfs import bfs_distances
    from modeling import build_graph

    g = build_graph(5, [(0, 1), (1, 2), (2, 3), (3, 4)])
    assert multi_source_distances(g, [2]) == bfs_distances(g, 2)


def test_every_node_a_source():
    from modeling import build_graph

    g = build_graph(4, [(0, 1), (1, 2), (2, 3)])
    assert multi_source_distances(g, range(4)) == {0: 0, 1: 0, 2: 0, 3: 0}


def test_rotting_oranges():
    assert rotting_oranges([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4


def test_rotting_oranges_unreachable():
    # the fresh orange at (2,0) is fenced in by empty cells
    assert rotting_oranges([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1


def test_rotting_oranges_nothing_to_do():
    assert rotting_oranges([[0, 2]]) == 0        # no fresh oranges
    assert rotting_oranges([[0, 0]]) == 0        # empty grid
    assert rotting_oranges([[1]]) == -1          # fresh, no source at all


def test_nearest_zero():
    assert nearest_zero([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == [
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 0],
    ]
    assert nearest_zero([[0, 0, 0], [0, 1, 0], [1, 1, 1]]) == [
        [0, 0, 0],
        [0, 1, 0],
        [1, 2, 1],
    ]


def test_blocked_cells_are_never_entered():
    # 1 is a wall; only the left column is reachable from the source at (0,0)
    grid = [[2, 1, 0], [0, 1, 0], [0, 1, 0]]
    dist = grid_multi_source(grid, lambda v: v == 2, lambda v: v == 1)
    assert [row[0] for row in dist] == [0, 1, 2]
    assert [row[1] for row in dist] == [-1, -1, -1]
    assert [row[2] for row in dist] == [-1, -1, -1]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
