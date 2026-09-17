"""Bellman-Ford — shortest paths with negative weights, and edge-count limits.

Signs: negative edge weights, "detect a negative cycle", "cheapest flight with
       at most K stops", any shortest path where Dijkstra's assumption fails.
Approach: relax every edge, V-1 times. After round i, every shortest path using
          at most i edges has been found — and a simple path can use at most
          V-1 edges. If a V-th round still improves something, that improvement
          can only have come from going round a negative cycle.
Complexity: O(V x E). Slow, and deliberately so: it makes no assumption about
            weights at all.
Gotchas:
  - The K-stops variant MUST relax from a snapshot of the previous round.
    Relaxing in place lets one round chain several edges together and quietly
    exceeds the stop limit.
  - Starting from `src` only detects negative cycles reachable from `src`. To
    find any negative cycle anywhere, start with dist = 0 everywhere, which is
    the same as adding a virtual source with a free edge to every node.
  - "Shortest path" stops being meaningful when a negative cycle is reachable —
    you can loop forever and keep improving. Report it, do not return a number.

Run the tests at the bottom with:  python3 graphs/bellman_ford.py
"""

INF = float("inf")


# ---------------------------------------------------------------- implementation


def bellman_ford(n, edges, src):
    """(dist, has_negative_cycle) from src. Edges are (u, v, w), directed.

    The early exit matters in practice: a round that changes nothing means the
    distances have converged and the remaining rounds are pure waste.
    """
    dist = [INF] * n
    dist[src] = 0

    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break

    # one more round: anything that still improves is on a negative cycle
    reachable_negative_cycle = any(
        dist[u] != INF and dist[u] + w < dist[v] for u, v, w in edges
    )
    return dist, reachable_negative_cycle


def has_negative_cycle(n, edges):
    """True if the graph contains a negative cycle anywhere, reachable or not.

    Starting every node at 0 is exactly the "virtual source" trick: it is as if
    a new node had a zero-weight edge into every real one, so no cycle can hide
    behind unreachability.
    """
    dist = [0] * n
    for _ in range(n):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            return False
    return True


def cheapest_within_k_stops(n, edges, src, dst, max_stops):
    """Cheapest src -> dst path using at most max_stops intermediate nodes, or -1.

    max_stops stops means at most max_stops + 1 edges, so that is the number of
    rounds. `prev` is the snapshot that enforces "one more edge per round" — the
    single most commonly botched line in this problem.
    """
    dist = [INF] * n
    dist[src] = 0
    for _ in range(max_stops + 1):
        prev = dist[:]
        for u, v, w in edges:
            if prev[u] != INF and prev[u] + w < dist[v]:
                dist[v] = prev[u] + w
    return dist[dst] if dist[dst] != INF else -1


def shortest_path_bellman_ford(n, edges, src, dst):
    """(cost, path) or (INF, None). Raises if a negative cycle makes it moot."""
    dist = [INF] * n
    dist[src] = 0
    parent = [-1] * n

    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                changed = True
        if not changed:
            break

    if any(dist[u] != INF and dist[u] + w < dist[v] for u, v, w in edges):
        raise ValueError("negative cycle reachable from src — no shortest path")

    if dist[dst] == INF:
        return INF, None
    path, cur = [], dst
    while cur != -1:
        path.append(cur)
        cur = parent[cur]
    return dist[dst], path[::-1]


# ------------------------------------------------------------------------ tests


def brute_force_shortest(n, edges, src):
    """Reference: enumerate every simple path. Exponential, exact, tiny n only."""
    from itertools import permutations

    best = [INF] * n
    best[src] = 0
    for size in range(1, n + 1):
        for seq in permutations(range(n), size):
            if seq[0] != src:
                continue
            cost, ok = 0, True
            for a, b in zip(seq, seq[1:]):
                w = min((w for u, v, w in edges if u == a and v == b), default=None)
                if w is None:
                    ok = False
                    break
                cost += w
            if ok:
                best[seq[-1]] = min(best[seq[-1]], cost)
    return best


def test_basic_distances():
    edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5)]
    dist, neg = bellman_ford(4, edges, 0)
    assert dist == [0, 3, 1, 4]  # 0->2->1 (3) beats the direct 0->1 (4)
    assert neg is False


def test_negative_edges_are_fine():
    edges = [(0, 1, 5), (0, 2, 4), (1, 2, -3)]
    dist, neg = bellman_ford(3, edges, 0)
    assert dist == [0, 5, 2]  # 5 + (-3) beats the direct 4
    assert neg is False


def test_unreachable_stays_infinite():
    dist, _ = bellman_ford(3, [(0, 1, 1)], 0)
    assert dist == [0, 1, INF]


def test_negative_cycle_detected():
    edges = [(0, 1, 1), (1, 2, -1), (2, 1, -1)]  # cycle 1->2->1 has weight -2
    _, neg = bellman_ford(3, edges, 0)
    assert neg is True
    assert has_negative_cycle(3, edges) is True


def test_unreachable_negative_cycle():
    # The cycle sits in a component src cannot reach.
    edges = [(0, 1, 1), (2, 3, -1), (3, 2, -1)]
    _, neg = bellman_ford(4, edges, 0)
    assert neg is False            # invisible from src...
    assert has_negative_cycle(4, edges) is True  # ...but it is really there


def test_negative_edge_is_not_a_negative_cycle():
    edges = [(0, 1, -5), (1, 2, 1)]
    assert has_negative_cycle(3, edges) is False


def test_matches_brute_force_on_random_graphs():
    import random

    random.seed(41)
    checked = 0
    while checked < 30:
        n = random.randint(2, 6)
        edges = [
            (u, v, random.randint(-3, 9))
            for u in range(n)
            for v in range(n)
            if u != v and random.random() < 0.35
        ]
        if has_negative_cycle(n, edges):
            continue  # "shortest" is undefined; nothing to compare against
        dist, neg = bellman_ford(n, edges, 0)
        assert neg is False
        assert dist == brute_force_shortest(n, edges, 0)
        checked += 1


def test_k_stops():
    flights = [(0, 1, 100), (1, 2, 100), (2, 0, 100), (1, 3, 600), (2, 3, 200)]
    # 0 -> 1 -> 2 -> 3 costs 400 but uses 2 stops; with 1 stop only 0 -> 1 -> 3
    assert cheapest_within_k_stops(4, flights, 0, 3, 1) == 700
    assert cheapest_within_k_stops(4, flights, 0, 3, 2) == 400


def test_k_stops_zero_means_direct_only():
    flights = [(0, 1, 100), (1, 2, 100), (0, 2, 500)]
    assert cheapest_within_k_stops(3, flights, 0, 2, 0) == 500  # must fly direct
    assert cheapest_within_k_stops(3, flights, 0, 2, 1) == 200  # one stop allowed


def test_k_stops_unreachable():
    assert cheapest_within_k_stops(3, [(0, 1, 1)], 0, 2, 5) == -1


def test_k_stops_never_chains_within_a_round():
    # A 4-edge chain must stay invisible until 3 stops are allowed. Relaxing in
    # place instead of from a snapshot would find it on round 1.
    chain = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1)]
    assert [cheapest_within_k_stops(5, chain, 0, 4, k) for k in range(5)] == [
        -1, -1, -1, 4, 4
    ]


def test_path_reconstruction():
    edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1)]
    cost, path = shortest_path_bellman_ford(4, edges, 0, 3)
    assert (cost, path) == (4, [0, 2, 1, 3])
    assert shortest_path_bellman_ford(4, [(0, 1, 1)], 0, 3) == (INF, None)


def test_path_reconstruction_refuses_negative_cycle():
    edges = [(0, 1, 1), (1, 2, -1), (2, 1, -1)]
    try:
        shortest_path_bellman_ford(3, edges, 0, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("expected a refusal on a reachable negative cycle")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
