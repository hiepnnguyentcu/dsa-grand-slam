"""Dijkstra — shortest paths with non-negative weights, plus its useful mutations.

Signs: minimum cost / time / distance, non-negative weights, "network delay",
       "cheapest route". Also anything where extending a path can only ever make
       it worse.
Approach: a min-heap of (distance, node). Pop the closest unfinished node —
          nothing can improve it any more, because every remaining route to it
          goes through something at least as far away — then relax its edges.
Complexity: O((V + E) log V).
Gotchas:
  - Negative edges break the core argument and silently give wrong answers. Use
    Bellman-Ford instead.
  - Python's heapq has no decrease-key, so improved distances are *pushed*
    rather than updated. That leaves stale entries in the heap; the
    `if d > dist[u]: continue` line is what discards them, and dropping it turns
    a correct algorithm into a slow wrong one.
  - Do not use a "visited" set in place of the stale check unless you are sure
    you mark on pop, not on push.

Dijkstra generalises past addition: it works for any edge operation where
combining can never *improve* a path. Hence the minimax and max-probability
variants below, which are the same loop with a different operator.

Run the tests at the bottom with:  python3 graphs/dijkstra.py
"""

import heapq

from modeling import grid_neighbors

INF = float("inf")


# ---------------------------------------------------------------- implementation


def dijkstra(n, g, src):
    """Shortest distances from src. g[u] = [(v, w), ...] with w >= 0."""
    dist = [INF] * n
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue  # stale entry, already improved on
        for v, w in g.get(u, ()):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def dijkstra_path(n, g, src, dst):
    """(cost, path) or (INF, None)."""
    dist = [INF] * n
    dist[src] = 0
    parent = [-1] * n
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == dst:
            break  # popped means final; nothing later can beat it
        for v, w in g.get(u, ()):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))
    if dist[dst] == INF:
        return INF, None
    path, cur = [], dst
    while cur != -1:
        path.append(cur)
        cur = parent[cur]
    return dist[dst], path[::-1]


def network_delay_time(times, n, src):
    """Time for a signal to reach every node, or -1 if some node cannot be reached.

    The answer is the *maximum* of the shortest distances: the signal travels
    every route in parallel, so the last arrival is what you wait for.
    """
    g = {u: [] for u in range(n)}
    for u, v, w in times:
        g[u].append((v, w))
    dist = dijkstra(n, g, src)
    worst = max(dist)
    return -1 if worst == INF else worst


def min_effort(heights):
    """Minimax path: minimise the *largest single step* from corner to corner.

    The cost of a path is max(edge) rather than sum(edge). Adding an edge can
    only hold the max steady or raise it — never lower it — which is the only
    property Dijkstra actually needs, so the same loop works with `max` in
    place of `+`.
    """
    R, C = len(heights), len(heights[0])
    best = [[INF] * C for _ in range(R)]
    best[0][0] = 0
    pq = [(0, 0, 0)]
    while pq:
        e, r, c = heapq.heappop(pq)
        if (r, c) == (R - 1, C - 1):
            return e
        if e > best[r][c]:
            continue
        for nr, nc in grid_neighbors(r, c, R, C):
            ne = max(e, abs(heights[nr][nc] - heights[r][c]))
            if ne < best[nr][nc]:
                best[nr][nc] = ne
                heapq.heappush(pq, (ne, nr, nc))
    return 0


def max_probability(n, g, src, dst):
    """Most likely path, where edges carry probabilities and combine by product.

    Multiplying by a probability <= 1 can only shrink the result, so "bigger is
    better" behaves exactly like "smaller is better" did. heapq is a min-heap,
    hence the negated keys. g[u] = [(v, p), ...].
    """
    prob = [0.0] * n
    prob[src] = 1.0
    pq = [(-1.0, src)]
    while pq:
        p, u = heapq.heappop(pq)
        p = -p
        if u == dst:
            return p
        if p < prob[u]:
            continue
        for v, pe in g.get(u, ()):
            if p * pe > prob[v]:
                prob[v] = p * pe
                heapq.heappush(pq, (-prob[v], v))
    return 0.0


def dijkstra_with_state(n, g, src, dst, states, start_state, transition):
    """Dijkstra over (node, state) pairs — the generic 'extra baggage' version.

    transition(u, v, w, state) -> (new_state, added_cost) or None if the move is
    not allowed. Costs still have to be non-negative. The heap key is the pair,
    so the same node can be settled once per state.
    """
    dist = {(src, start_state): 0}
    pq = [(0, src, start_state)]
    while pq:
        d, u, st = heapq.heappop(pq)
        if d > dist.get((u, st), INF):
            continue
        if u == dst:
            return d
        for v, w in g.get(u, ()):
            step = transition(u, v, w, st)
            if step is None:
                continue
            nst, add = step
            if nst not in states:
                continue
            nd = d + add
            if nd < dist.get((v, nst), INF):
                dist[(v, nst)] = nd
                heapq.heappush(pq, (nd, v, nst))
    return INF


# ------------------------------------------------------------------------ tests


WEIGHTED = {
    0: [(1, 4), (2, 1)],
    1: [(3, 1)],
    2: [(1, 2), (3, 5)],
    3: [],
}


def test_prefers_the_cheaper_detour():
    # 0 -> 2 -> 1 costs 3, the direct 0 -> 1 costs 4
    assert dijkstra(4, WEIGHTED, 0) == [0, 3, 1, 4]


def test_unreachable_is_infinite():
    assert dijkstra(3, {0: [(1, 1)], 1: [], 2: []}, 0) == [0, 1, INF]


def test_path_reconstruction():
    cost, path = dijkstra_path(4, WEIGHTED, 0, 3)
    assert (cost, path) == (4, [0, 2, 1, 3])
    assert all(
        any(v == b and w for v, w in WEIGHTED[a]) for a, b in zip(path, path[1:])
    )
    assert dijkstra_path(4, {0: [], 1: [], 2: [], 3: []}, 0, 3) == (INF, None)


def test_zero_weight_edges():
    g = {0: [(1, 0)], 1: [(2, 0)], 2: []}
    assert dijkstra(3, g, 0) == [0, 0, 0]


def test_agrees_with_bellman_ford_on_random_non_negative_graphs():
    import random

    from bellman_ford import bellman_ford

    random.seed(43)
    for _ in range(40):
        n = random.randint(2, 12)
        edges = [
            (u, v, random.randint(0, 20))
            for u in range(n)
            for v in range(n)
            if u != v and random.random() < 0.3
        ]
        g = {u: [] for u in range(n)}
        for u, v, w in edges:
            g[u].append((v, w))
        want, neg = bellman_ford(n, edges, 0)
        assert neg is False
        assert dijkstra(n, g, 0) == want


def test_stale_heap_entries_do_not_corrupt_the_answer():
    # A long chain of improvements to the same node leaves many stale entries.
    g = {0: [(i, 100 - i) for i in range(1, 20)], **{i: [(19, 1)] for i in range(1, 20)}}
    g[19] = []
    dist = dijkstra(20, g, 0)
    # direct 0 -> 19 costs 81; the best two-hop route is 0 -> 18 -> 19 at 83
    assert dist[19] == 81
    assert dist[1] == 99


def test_network_delay():
    # nodes 0..3, signal starts at 1: reaches 0 and 2 at t=1, then 3 at t=2
    assert network_delay_time([(1, 0, 1), (1, 2, 1), (2, 3, 1)], 4, 1) == 2
    assert network_delay_time([(0, 1, 1)], 2, 0) == 1
    assert network_delay_time([(0, 1, 1)], 3, 0) == -1  # node 2 never hears


def test_min_effort_is_the_worst_step_not_the_total():
    assert min_effort([[1, 2, 2], [3, 8, 2], [5, 3, 5]]) == 2
    assert min_effort([[1, 2, 3], [3, 8, 4], [5, 3, 5]]) == 1
    assert min_effort([[1, 2, 1, 1, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1],
                       [1, 2, 1, 2, 1], [1, 1, 1, 2, 1]]) == 0
    assert min_effort([[7]]) == 0


def test_min_effort_avoids_a_cliff():
    # Straight across the top crosses a step of 99. Down the flat left column
    # and along the bottom never exceeds a step of 1.
    heights = [
        [1, 100, 2],
        [1, 99, 2],
        [1, 2, 2],
    ]
    assert min_effort(heights) == 1


def test_max_probability():
    g = {0: [(1, 0.5), (2, 0.2)], 1: [(0, 0.5), (2, 0.5)], 2: [(0, 0.2), (1, 0.5)]}
    assert abs(max_probability(3, g, 0, 2) - 0.25) < 1e-9  # 0.5 * 0.5 beats 0.2

    g2 = {0: [(1, 0.5), (2, 0.3)], 1: [(0, 0.5)], 2: [(0, 0.3)]}
    assert abs(max_probability(3, g2, 0, 2) - 0.3) < 1e-9

    assert max_probability(3, {0: [(1, 0.5)], 1: [(0, 0.5)], 2: []}, 0, 2) == 0.0


def test_state_dijkstra_matches_plain_dijkstra_with_one_state():
    dist = dijkstra(4, WEIGHTED, 0)
    got = dijkstra_with_state(
        4, WEIGHTED, 0, 3, {None}, None, lambda u, v, w, s: (None, w)
    )
    assert got == dist[3]


def test_state_dijkstra_with_a_budget():
    # Each edge may be taken free at most twice; the third crossing costs full
    # price. State is "free passes remaining".
    g = {0: [(1, 10)], 1: [(2, 10)], 2: [(3, 10)], 3: []}
    got = dijkstra_with_state(
        4, g, 0, 3, set(range(3)), 2,
        lambda u, v, w, s: (s - 1, 0) if s > 0 else (s, w),
    )
    assert got == 10  # two hops free, the third paid


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
