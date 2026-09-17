"""Strongly connected components — Kosaraju's two-pass algorithm.

Signs: groups of mutually reachable nodes in a *directed* graph, collapsing a
       graph into a DAG, "which nodes can all reach each other", 2-SAT.
Approach: two DFS passes.
    Pass 1 on the original graph, recording nodes by finish time. Finishing last
    means "nothing above me is unexplored", so the last-finished node lies in a
    source component of the condensation.
    Pass 2 on the *reversed* graph, starting from the latest finisher and
    working back. On the reversed graph you can leave a component only by going
    "upstream", and everything upstream has already been claimed — so each DFS
    tree in pass 2 is exactly one SCC.
Complexity: O(V + E), two passes plus building the reversed graph.

The condensation — one node per SCC — is always a DAG, which is the real payoff:
collapse the cycles and every DAG technique (topological order, DP) applies.

Bonus: pass 2 discovers components in topological order of the condensation, so
the component ids come out already sorted. `test_component_ids_are_topological`
pins that down.

Gotchas: recursive, so the ~1000-frame limit applies. Tarjan's algorithm does
         the same job in one pass; Kosaraju is here because it is far easier to
         remember and to explain under pressure.

Run the tests at the bottom with:  python3 graphs/scc_kosaraju.py
"""


# ---------------------------------------------------------------- implementation


def kosaraju(n, g):
    """(comp, count) — comp[u] is u's component id, ids are 0..count-1."""
    rg = {u: [] for u in range(n)}
    for u in range(n):
        for v in g.get(u, ()):
            rg[v].append(u)

    seen = [False] * n
    order = []

    def dfs1(u):
        seen[u] = True
        for v in g.get(u, ()):
            if not seen[v]:
                dfs1(v)
        order.append(u)  # finish time: appended only once fully explored

    for u in range(n):
        if not seen[u]:
            dfs1(u)

    comp = [-1] * n
    count = 0

    def dfs2(u):
        comp[u] = count
        for v in rg[u]:
            if comp[v] == -1:
                dfs2(v)

    for u in reversed(order):  # latest finisher first
        if comp[u] == -1:
            dfs2(u)
            count += 1
    return comp, count


def scc_groups(n, g):
    """The components themselves, as a list of node lists."""
    comp, count = kosaraju(n, g)
    groups = [[] for _ in range(count)]
    for u in range(n):
        groups[comp[u]].append(u)
    return groups


def condensation(n, g):
    """(comp, count, dag) — the graph with each SCC collapsed to a single node.

    The result is guaranteed acyclic: any cycle between two components would
    have made them one component in the first place.
    """
    comp, count = kosaraju(n, g)
    dag = {c: set() for c in range(count)}
    for u in range(n):
        for v in g.get(u, ()):
            if comp[u] != comp[v]:
                dag[comp[u]].add(comp[v])
    return comp, count, {c: sorted(vs) for c, vs in dag.items()}


# ------------------------------------------------------------------------ tests


#   0 -> 1 -> 2 -> 0        {0,1,2}
#             2 -> 3        {3}
#             3 -> 4 -> 5 -> 6 -> 4   {4,5,6}
#             4 -> 7        {7}
SAMPLE = {0: [1], 1: [2], 2: [0, 3], 3: [4], 4: [5, 7], 5: [6], 6: [4], 7: []}


def test_finds_the_components():
    assert sorted(map(sorted, scc_groups(8, SAMPLE))) == [[0, 1, 2], [3], [4, 5, 6], [7]]


def test_single_cycle_is_one_component():
    assert kosaraju(3, {0: [1], 1: [2], 2: [0]})[1] == 1


def test_dag_has_no_nontrivial_components():
    comp, count = kosaraju(3, {0: [1], 1: [2], 2: []})
    assert count == 3  # every node is its own SCC


def test_isolated_nodes():
    comp, count = kosaraju(3, {0: [], 1: [], 2: []})
    assert count == 3
    assert sorted(comp) == [0, 1, 2]  # ids are arbitrary, but all distinct
    assert kosaraju(1, {0: [0]})[1] == 1  # self-loop, still one component


def test_matches_mutual_reachability():
    from floyd_warshall import transitive_closure

    edges = [(u, v) for u in SAMPLE for v in SAMPLE[u]]
    reach = transitive_closure(8, edges)
    comp, _ = kosaraju(8, SAMPLE)
    for u in range(8):
        for v in range(8):
            mutual = reach[u][v] and reach[v][u]
            assert (comp[u] == comp[v]) == mutual


def test_matches_mutual_reachability_on_random_graphs():
    import random

    from floyd_warshall import transitive_closure

    random.seed(97)
    for _ in range(40):
        n = random.randint(1, 9)
        edges = [
            (u, v) for u in range(n) for v in range(n)
            if u != v and random.random() < 0.25
        ]
        g = {u: [] for u in range(n)}
        for u, v in edges:
            g[u].append(v)
        reach = transitive_closure(n, edges)
        comp, _ = kosaraju(n, g)
        for u in range(n):
            for v in range(n):
                assert (comp[u] == comp[v]) == (reach[u][v] and reach[v][u])


def test_condensation_is_acyclic():
    from cycle_detection import directed_has_cycle

    _, count, dag = condensation(8, SAMPLE)
    assert directed_has_cycle(count, dag) is False


def test_condensation_of_a_cycle_is_a_single_node():
    _, count, dag = condensation(3, {0: [1], 1: [2], 2: [0]})
    assert count == 1
    assert dag == {0: []}  # the internal edges vanish


def test_component_ids_are_topological():
    # Pass 2 discovers source components first, so every cross-component edge
    # points from a lower id to a higher one -- a topological order for free.
    import random

    random.seed(101)
    for _ in range(30):
        n = random.randint(1, 9)
        g = {u: [] for u in range(n)}
        for u in range(n):
            for v in range(n):
                if u != v and random.random() < 0.25:
                    g[u].append(v)
        comp, _ = kosaraju(n, g)
        for u in range(n):
            for v in g[u]:
                if comp[u] != comp[v]:
                    assert comp[u] < comp[v]


def test_every_node_lands_in_exactly_one_component():
    import random

    random.seed(103)
    for _ in range(30):
        n = random.randint(1, 10)
        g = {u: [] for u in range(n)}
        for u in range(n):
            for v in range(n):
                if u != v and random.random() < 0.3:
                    g[u].append(v)
        groups = scc_groups(n, g)
        flat = sorted(u for group in groups for u in group)
        assert flat == list(range(n))
        assert all(groups)  # no empty component ids


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
