"""0-1 BFS — Dijkstra's answer at BFS's price, when weights are only 0 or 1.

Signs: every edge costs 0 or 1 — free moves vs costly ones, "minimum obstacles
       to remove", "fewest direction changes", "cheapest with some steps free".
Approach: a deque instead of a heap. Relaxing along a 0-edge keeps you on the
          current distance layer, so push to the *front*; a 1-edge starts the
          next layer, so push to the back. The deque therefore always holds at
          most two distinct distances, in order, and its front is the minimum —
          which is exactly the guarantee a priority queue was buying you.
Complexity: O(V + E). No log factor, because there is no heap.
Gotchas:
  - Only valid for weights in {0, 1}. For {0, k} rescale; for anything else use
    Dijkstra.
  - appendleft vs append is the entire algorithm. Swapping them gives a
    plausible-looking traversal with wrong answers.
  - A node can be popped more than once. That is fine and cheap here, since the
    relaxation check discards the stale visits.

Run the tests at the bottom with:  python3 graphs/zero_one_bfs.py
"""

from collections import deque

from modeling import grid_neighbors

INF = float("inf")


# ---------------------------------------------------------------- implementation


def zero_one_bfs(n, g, src):
    """Shortest distances from src. g[u] = [(v, w), ...] with w in {0, 1}."""
    dist = [INF] * n
    dist[src] = 0
    dq = deque([src])
    while dq:
        u = dq.popleft()
        for v, w in g.get(u, ()):
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd
                if w == 0:
                    dq.appendleft(v)  # same layer -> jump the queue
                else:
                    dq.append(v)      # next layer -> wait your turn
    return dist


def min_obstacles_removal(grid):
    """Fewest 1-cells to clear on a path from the top-left to the bottom-right.

    Entering an empty cell is free, entering an obstacle costs one removal —
    literally a 0/1 weighting of the grid graph.
    """
    R, C = len(grid), len(grid[0])
    dist = [[INF] * C for _ in range(R)]
    dist[0][0] = grid[0][0]
    dq = deque([(0, 0)])
    while dq:
        r, c = dq.popleft()
        for nr, nc in grid_neighbors(r, c, R, C):
            w = grid[nr][nc]
            nd = dist[r][c] + w
            if nd < dist[nr][nc]:
                dist[nr][nc] = nd
                if w == 0:
                    dq.appendleft((nr, nc))
                else:
                    dq.append((nr, nc))
    return dist[R - 1][C - 1]


ARROWS = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}


def min_cost_arrow_grid(grid):
    """Fewest arrows to reorient so a path exists from top-left to bottom-right.

    Each cell points somewhere (1 right, 2 left, 3 down, 4 up). Following the
    arrow is free; any other direction costs one edit. Every cell has four
    outgoing edges, exactly one of which is free.
    """
    R, C = len(grid), len(grid[0])
    dist = [[INF] * C for _ in range(R)]
    dist[0][0] = 0
    dq = deque([(0, 0)])
    while dq:
        r, c = dq.popleft()
        for sign, (dr, dc) in ARROWS.items():
            nr, nc = r + dr, c + dc
            if not (0 <= nr < R and 0 <= nc < C):
                continue
            w = 0 if grid[r][c] == sign else 1
            nd = dist[r][c] + w
            if nd < dist[nr][nc]:
                dist[nr][nc] = nd
                if w == 0:
                    dq.appendleft((nr, nc))
                else:
                    dq.append((nr, nc))
    return dist[R - 1][C - 1]


# ------------------------------------------------------------------------ tests


def test_free_edges_cost_nothing():
    g = {0: [(1, 0), (2, 1)], 1: [(2, 0)], 2: []}
    assert zero_one_bfs(3, g, 0) == [0, 0, 0]  # the 0-0 route beats the direct 1


def test_unreachable():
    assert zero_one_bfs(3, {0: [(1, 1)], 1: [], 2: []}, 0) == [0, 1, INF]


def test_agrees_with_dijkstra_on_random_zero_one_graphs():
    import random

    from dijkstra import dijkstra

    random.seed(47)
    for _ in range(50):
        n = random.randint(2, 15)
        g = {u: [] for u in range(n)}
        for u in range(n):
            for v in range(n):
                if u != v and random.random() < 0.25:
                    g[u].append((v, random.randint(0, 1)))
        assert zero_one_bfs(n, g, 0) == dijkstra(n, g, 0)


def test_long_chain_of_free_edges():
    # 1000 free hops then one paid hop -- the front-loading has to hold up
    n = 1002
    g = {i: [(i + 1, 0)] for i in range(n - 2)}
    g[n - 2] = [(n - 1, 1)]
    g[n - 1] = []
    dist = zero_one_bfs(n, g, 0)
    assert dist[n - 2] == 0
    assert dist[n - 1] == 1


def test_min_obstacles():
    assert min_obstacles_removal([[0, 1, 1], [1, 1, 0], [1, 1, 0]]) == 2


def test_min_obstacles_clear_route_exists():
    assert min_obstacles_removal([[0, 1, 0, 0, 0], [0, 1, 0, 1, 0], [0, 0, 0, 1, 0]]) == 0


def test_min_obstacles_trivial():
    assert min_obstacles_removal([[0]]) == 0
    assert min_obstacles_removal([[0, 0], [0, 0]]) == 0
    assert min_obstacles_removal([[0, 1], [1, 0]]) == 1  # either way round, one wall


def test_min_obstacles_matches_dijkstra():
    import random

    from dijkstra import dijkstra

    random.seed(53)
    for _ in range(25):
        R, C = random.randint(1, 5), random.randint(1, 5)
        grid = [[random.randint(0, 1) for _ in range(C)] for _ in range(R)]
        grid[0][0] = 0

        # the same grid expressed as an explicit weighted graph
        idx = lambda r, c: r * C + c
        g = {idx(r, c): [] for r in range(R) for c in range(C)}
        for r in range(R):
            for c in range(C):
                for nr, nc in grid_neighbors(r, c, R, C):
                    g[idx(r, c)].append((idx(nr, nc), grid[nr][nc]))
        assert min_obstacles_removal(grid) == dijkstra(R * C, g, 0)[idx(R - 1, C - 1)]


def test_arrow_grid():
    assert min_cost_arrow_grid([[1, 1, 1, 1], [2, 2, 2, 2], [1, 1, 1, 1], [2, 2, 2, 2]]) == 3
    assert min_cost_arrow_grid([[1, 1, 3], [3, 2, 2], [1, 1, 4]]) == 0  # already routed
    assert min_cost_arrow_grid([[1, 2], [4, 3]]) == 1


def test_arrow_grid_single_cell():
    assert min_cost_arrow_grid([[1]]) == 0  # already at the destination


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
