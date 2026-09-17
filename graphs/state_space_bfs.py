"""State-space BFS — when position alone is not enough to describe where you are.

Signs: shortest path where something *besides* location changes what you can do
       next — keys collected, walls you may still break, remaining fuel, which
       nodes you have already visited, whose turn it is.
Approach: the node becomes a tuple (position, extra state). The visited set is
          keyed by the whole tuple, so the same cell can legitimately be entered
          many times, once per distinct state. Everything else is plain BFS.
Complexity: O(positions x states x branching). That product is the thing to
            watch — it is what decides whether the search is feasible.
Gotchas:
  - Keep the state as small as it can be. A set of collected keys belongs in a
    bitmask, not a frozenset.
  - Visiting (cell, state) twice is *correct*, but visiting (cell) twice under
    the same state is a bug that turns BFS exponential.
  - If the extra state is monotone (fuel only decreases), reaching a cell with
    strictly more budget dominates — pruning on that is a big win.

Run the tests at the bottom with:  python3 graphs/state_space_bfs.py
"""

from collections import deque

from modeling import grid_neighbors


# ---------------------------------------------------------------- implementation


def state_bfs(starts, is_goal, neighbors):
    """Generic shortest number of moves over an implicit state space, or -1.

    starts    : iterable of initial states (any hashable)
    is_goal   : state -> bool
    neighbors : state -> iterable of next states

    To recover the path rather than the length, swap `seen` for a dict mapping
    state -> predecessor and walk it backwards, exactly as bfs_shortest_path does.
    """
    q = deque((s, 0) for s in starts)
    seen = {s for s, _ in q}
    while q:
        state, d = q.popleft()
        if is_goal(state):
            return d
        for nxt in neighbors(state):
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, d + 1))
    return -1


def shortest_with_breaks(grid, k):
    """Fewest steps from the top-left to the bottom-right, breaking <= k walls.

    State is (row, col, walls_left). Reaching a cell with more budget left is a
    genuinely different situation, so it gets its own entry in `seen`.
    """
    R, C = len(grid), len(grid[0])
    start_rem = k - grid[0][0]
    if start_rem < 0:
        return -1

    q = deque([(0, 0, start_rem, 0)])
    seen = {(0, 0, start_rem)}
    while q:
        r, c, rem, d = q.popleft()
        if (r, c) == (R - 1, C - 1):
            return d
        for nr, nc in grid_neighbors(r, c, R, C):
            nrem = rem - grid[nr][nc]
            if nrem >= 0 and (nr, nc, nrem) not in seen:
                seen.add((nr, nc, nrem))
                q.append((nr, nc, nrem, d + 1))
    return -1


def visit_all_nodes(g):
    """Shortest walk visiting every node, starting anywhere, revisits allowed.

    State is (current_node, bitmask_of_visited). Every node is a legal start, so
    all n of them are seeded at distance 0 — multi-source BFS over a state space.
    Revisiting a node is fine, which is why the plain "visited nodes" set would
    be wrong here and the mask is doing the real work.
    """
    n = len(g)
    full = (1 << n) - 1
    q = deque((u, 1 << u, 0) for u in range(n))
    seen = {(u, 1 << u) for u in range(n)}
    while q:
        u, mask, d = q.popleft()
        if mask == full:
            return d
        for v in g[u]:
            nm = mask | (1 << v)
            if (v, nm) not in seen:
                seen.add((v, nm))
                q.append((v, nm, d + 1))
    return -1


def open_lock(deadends, target):
    """Fewest turns on a 4-wheel lock from "0000", avoiding the deadends.

    Here the *state is the whole node* — there is no separate position. 10^4
    states, 8 neighbours each, so BFS is trivially affordable.
    """
    dead = set(deadends)
    if "0000" in dead:
        return -1

    def neighbors(s):
        for i in range(4):
            d = int(s[i])
            for nd in ((d + 1) % 10, (d - 1) % 10):
                cand = s[:i] + str(nd) + s[i + 1:]
                if cand not in dead:
                    yield cand

    return state_bfs(["0000"], lambda s: s == target, neighbors)


# ------------------------------------------------------------------------ tests


def test_breaking_walls_opens_a_shortcut():
    grid = [[0, 0, 0], [1, 1, 0], [0, 0, 0], [0, 1, 1], [0, 0, 0]]
    assert shortest_with_breaks(grid, 1) == 6


def test_budget_changes_the_answer():
    grid = [[0, 1, 1], [1, 1, 1], [1, 0, 0]]
    assert shortest_with_breaks(grid, 1) == -1  # not enough budget to get through
    assert shortest_with_breaks(grid, 2) == 4   # with 2 breaks the diagonal opens


def test_budget_is_part_of_the_state_not_a_global():
    # The short route costs 2 breaks; the long way round costs none. With a
    # budget of 1, the answer has to be the long way -- which only works if
    # arriving at a cell with different budgets is tracked separately.
    grid = [
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
    ]
    assert shortest_with_breaks(grid, 0) == 5  # down, across, up
    assert shortest_with_breaks(grid, 2) == 5  # breaking is no faster here


def test_trivial_grids():
    assert shortest_with_breaks([[0]], 0) == 0
    assert shortest_with_breaks([[1]], 0) == -1  # cannot even stand on the start
    assert shortest_with_breaks([[1]], 1) == 0


def brute_force_visit_all(g):
    """Reference answer by a completely different route.

    An optimal walk visits the nodes in *some* order and travels a shortest
    path between consecutive first-visits, so the answer is the cheapest
    permutation under the all-pairs shortest-path metric. Exponential, but
    exact -- exactly what a test wants.
    """
    from itertools import permutations

    from bfs import bfs_distances

    n = len(g)
    d = [bfs_distances({u: list(g[u]) for u in range(n)}, s) for s in range(n)]
    return min(
        sum(d[a][b] for a, b in zip(order, order[1:]))
        for order in permutations(range(n))
    )


def test_visit_all_nodes():
    star = [[1, 2, 3], [0], [0], [0]]
    assert visit_all_nodes(star) == 4  # 1-0-2-0-3: the hub is crossed twice
    assert visit_all_nodes(star) == brute_force_visit_all(star)

    #  0 - 1 - 2 - 3
    #      |
    #      4
    tree = [[1], [0, 2, 4], [1, 3], [2], [1]]
    assert visit_all_nodes(tree) == 5  # e.g. 0-1-4-1-2-3
    assert visit_all_nodes(tree) == brute_force_visit_all(tree)


def test_visit_all_nodes_matches_brute_force_on_random_graphs():
    import random

    random.seed(23)
    checked = 0
    while checked < 20:
        n = random.randint(2, 6)
        edges = [(u, v) for u in range(n) for v in range(u + 1, n) if random.random() < 0.5]
        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        # the walk only exists if the graph is connected
        if visit_all_nodes(g) == -1:
            continue
        assert visit_all_nodes(g) == brute_force_visit_all(g)
        checked += 1


def test_visit_all_nodes_edge_cases():
    assert visit_all_nodes([[]]) == 0             # single node, already done
    assert visit_all_nodes([[1], [0]]) == 1       # one edge


def test_visit_all_nodes_path_graph():
    # A straight path of n nodes needs n-1 steps: start at one end, walk.
    for n in range(1, 7):
        g = [[j for j in (i - 1, i + 1) if 0 <= j < n] for i in range(n)]
        assert visit_all_nodes(g) == n - 1


def test_open_lock():
    assert open_lock(["0201", "0101", "0102", "1212", "2002"], "0202") == 6
    assert open_lock(["8888"], "0009") == 1
    assert open_lock(["0000"], "8888") == -1  # the start itself is a deadend


def test_open_lock_walled_in():
    # Every one-move neighbour of the start is dead, so nothing is reachable.
    dead = ["1000", "9000", "0100", "0900", "0010", "0090", "0001", "0009"]
    assert open_lock(dead, "8888") == -1
    assert open_lock(dead, "0000") == 0  # ...but we are already there


def test_generic_state_bfs_matches_plain_bfs():
    from bfs import bfs_distances
    from modeling import build_graph

    g = build_graph(6, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5)])
    dist = bfs_distances(g, 0)
    for target in range(6):
        assert state_bfs([0], lambda s, t=target: s == t, lambda s: g[s]) == dist[target]


def test_generic_state_bfs_unreachable():
    assert state_bfs([0], lambda s: s == 99, lambda s: []) == -1


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
