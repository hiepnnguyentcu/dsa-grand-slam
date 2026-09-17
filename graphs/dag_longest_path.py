"""Longest path in a DAG — relax edges in topological order.

Signs: longest chain of dependencies, critical path / project scheduling, max
       weight path, "how long until everything finishes".
Approach: process nodes in topological order. By the time you reach u, every
          route into u has already been considered, so dp[u] is final and can
          be pushed forward: dp[v] = max(dp[v], dp[u] + w).
Complexity: O(V + E).

Why the DAG restriction matters: longest path in a *general* graph is NP-hard
(a Hamiltonian path is just a longest path). Acyclicity is what buys the linear
scan — with a cycle of positive weight the answer is unbounded, which is why
this raises instead of returning nonsense.

Gotchas: dp starts at 0 everywhere, so a path may start at any node, not only
         at a source. Seed dp with -inf except at `src` if the path must start
         somewhere specific. Negative weights are fine — unlike Dijkstra, this
         never revisits a decision.

Run the tests at the bottom with:  python3 graphs/dag_longest_path.py
"""

from collections import deque


# ---------------------------------------------------------------- implementation


def dag_longest_path(n, edges, src=None):
    """(total_weight, path) of the heaviest path. Edges are (u, v, w).

    With src=None the path may start anywhere. Pass src to force a start node,
    in which case nodes unreachable from src are excluded.
    Raises ValueError if the graph has a cycle.
    """
    g = {u: [] for u in range(n)}
    indeg = [0] * n
    for u, v, w in edges:
        g[u].append((v, w))
        indeg[v] += 1

    NEG = float("-inf")
    dp = [0] * n if src is None else [NEG] * n
    if src is not None:
        dp[src] = 0
    parent = [-1] * n

    q = deque(u for u in range(n) if indeg[u] == 0)
    processed = 0
    while q:
        u = q.popleft()
        processed += 1
        for v, w in g[u]:
            if dp[u] != NEG and dp[u] + w > dp[v]:
                dp[v] = dp[u] + w
                parent[v] = u
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

    if processed != n:
        raise ValueError("graph has a cycle — longest path is not well defined")

    end = max(range(n), key=dp.__getitem__)
    path = []
    while end != -1:
        path.append(end)
        end = parent[end]
    return dp[path[0]], path[::-1]


def dag_longest_length(n, edges):
    """Longest path measured in edges, ignoring weights. Edges are (u, v)."""
    weight, path = dag_longest_path(n, [(u, v, 1) for u, v in edges])
    return weight


def dag_shortest_path(n, edges, src):
    """Shortest distances from src over a DAG, negative weights allowed.

    The same scan with min instead of max. This is the one shortest-path
    algorithm that beats Dijkstra on negative weights *and* beats Bellman-Ford
    on speed — it just needs the graph to be acyclic.
    """
    g = {u: [] for u in range(n)}
    indeg = [0] * n
    for u, v, w in edges:
        g[u].append((v, w))
        indeg[v] += 1

    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    q = deque(u for u in range(n) if indeg[u] == 0)
    processed = 0
    while q:
        u = q.popleft()
        processed += 1
        for v, w in g[u]:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

    if processed != n:
        raise ValueError("graph has a cycle — use Bellman-Ford instead")
    return dist


# ------------------------------------------------------------------------ tests


def is_real_path(edges, path, total):
    """Every hop is an edge, and the weights add up to the reported total."""
    weights = {}
    for u, v, w in edges:
        weights[(u, v)] = max(w, weights.get((u, v), float("-inf")))
    if len(path) == 1:
        return total == 0
    if not all((a, b) in weights for a, b in zip(path, path[1:])):
        return False
    return sum(weights[(a, b)] for a, b in zip(path, path[1:])) == total


def test_chain():
    edges = [(0, 1, 1), (1, 2, 1), (2, 3, 1)]
    assert dag_longest_path(4, edges) == (3, [0, 1, 2, 3])


def test_picks_the_heavier_branch_not_the_longer_one():
    #      3          1
    #  0 -----> 1 --------> 3      total 4
    #  0 --> 2 --> 3              total 1 + 5 = 6
    edges = [(0, 1, 3), (1, 3, 1), (0, 2, 1), (2, 3, 5)]
    total, path = dag_longest_path(4, edges)
    assert (total, path) == (6, [0, 2, 3])
    assert is_real_path(edges, path, total)


def test_path_may_start_anywhere():
    # The heavy stretch does not begin at the source.
    edges = [(0, 1, 1), (1, 2, 50), (2, 3, 50)]
    total, path = dag_longest_path(4, edges)
    assert total == 101 and path == [0, 1, 2, 3]

    # ...but here starting at 0 is a handicap: 0 -> 1 is worth nothing.
    edges = [(0, 1, 0), (2, 3, 9)]
    total, path = dag_longest_path(4, edges)
    assert (total, path) == (9, [2, 3])


def test_forced_start_node():
    edges = [(0, 1, 1), (2, 3, 100)]
    assert dag_longest_path(4, edges, src=0) == (1, [0, 1])   # 2->3 is unreachable
    assert dag_longest_path(4, edges)[0] == 100                # free start finds it


def test_isolated_nodes_and_no_edges():
    assert dag_longest_path(3, []) == (0, [0])
    assert dag_longest_path(1, []) == (0, [0])


def test_negative_weights_are_fine():
    edges = [(0, 1, -5), (1, 2, 10), (0, 2, 1)]

    # Free start: skipping the -5 edge entirely and beginning at 1 is best.
    total, path = dag_longest_path(3, edges)
    assert (total, path) == (10, [1, 2])
    assert is_real_path(edges, path, total)

    # Forced to start at 0, paying the -5 still beats the direct edge (1).
    total, path = dag_longest_path(3, edges, src=0)
    assert (total, path) == (5, [0, 1, 2])
    assert is_real_path(edges, path, total)


def test_cycle_is_rejected():
    for fn, args in [
        (dag_longest_path, (3, [(0, 1, 1), (1, 2, 1), (2, 0, 1)])),
        (dag_shortest_path, (3, [(0, 1, 1), (1, 2, 1), (2, 0, 1)], 0)),
    ]:
        try:
            fn(*args)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{fn.__name__} should reject a cyclic graph")


def test_unweighted_length_in_edges():
    assert dag_longest_length(4, [(0, 1), (1, 2), (2, 3), (0, 3)]) == 3


def test_shortest_path_over_a_dag():
    edges = [(0, 1, 5), (0, 2, 3), (1, 3, 1), (2, 3, 1)]
    dist = dag_shortest_path(4, edges, 0)
    assert dist == [0, 5, 3, 4]

    # negative weights, where Dijkstra would be wrong
    edges = [(0, 1, 5), (0, 2, 3), (1, 2, -10)]
    assert dag_shortest_path(3, edges, 0) == [0, 5, -5]


def test_shortest_marks_unreachable_as_inf():
    dist = dag_shortest_path(3, [(0, 1, 1)], 0)
    assert dist[2] == float("inf")


def test_matches_brute_force_on_random_dags():
    import random
    from itertools import permutations

    random.seed(13)
    for _ in range(25):
        n = random.randint(2, 7)
        edges = [
            (u, v, random.randint(-5, 9))
            for u in range(n)
            for v in range(u + 1, n)
            if random.random() < 0.5
        ]
        if not edges:
            continue
        weights = {}
        for u, v, w in edges:
            weights[(u, v)] = max(w, weights.get((u, v), float("-inf")))

        best = 0  # the empty single-node path
        for size in range(2, n + 1):
            for seq in permutations(range(n), size):
                if all((a, b) in weights for a, b in zip(seq, seq[1:])):
                    best = max(best, sum(weights[(a, b)] for a, b in zip(seq, seq[1:])))
        total, path = dag_longest_path(n, edges)
        assert total == best
        assert is_real_path(edges, path, total)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
