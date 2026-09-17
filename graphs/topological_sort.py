"""Topological sort — Kahn's indegree queue and DFS postorder, plus variants.

Signs: ordering with prerequisites, build/compile order, course schedule,
       deriving an order from pairwise constraints, any DP over a DAG.
Approach:
    Kahn  — repeatedly take a node with nothing left pointing at it. Removing
            it frees its successors. If the queue empties before all n nodes
            come out, whatever is left is tangled in a cycle.
    DFS   — append a node once every descendant is finished, then reverse.
            Postorder puts dependencies before dependents by construction.
Complexity: O(V + E) for both.
Gotchas: only DAGs have a topological order, so a "did everything come out"
         check is not optional — it *is* the cycle test. Kahn gives you that
         for free; the DFS version needs the 3-colour marking to notice.

Prefer Kahn when you want level structure, lexicographic order, or uniqueness
checks. Prefer DFS when you are already walking the graph anyway.

Run the tests at the bottom with:  python3 graphs/topological_sort.py
"""

import heapq
from collections import deque

WHITE, GREY, BLACK = 0, 1, 2


# ---------------------------------------------------------------- implementation


def _adjacency(n, edges):
    g = {u: [] for u in range(n)}
    indeg = [0] * n
    for u, v in edges:
        g[u].append(v)
        indeg[v] += 1
    return g, indeg


def topo_sort_kahn(n, edges):
    """A topological order, or [] if the graph has a cycle. Edges are u -> v."""
    g, indeg = _adjacency(n, edges)
    q = deque(u for u in range(n) if indeg[u] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else []


def topo_sort_dfs(n, g):
    """Reverse DFS postorder, or [] on a cycle.

    A node is appended *after* all of its descendants, so the reversed list
    puts it before them. GREY doubles as the back-edge detector.
    """
    color = [WHITE] * n
    out = []

    def visit(u):
        color[u] = GREY
        for v in g.get(u, ()):
            if color[v] == GREY:
                return False
            if color[v] == WHITE and not visit(v):
                return False
        color[u] = BLACK
        out.append(u)
        return True

    for u in range(n):
        if color[u] == WHITE and not visit(u):
            return []
    return out[::-1]


def topo_sort_lexicographic(n, edges):
    """The alphabetically smallest valid order. Min-heap instead of a queue.

    Any ready node is legal, so taking the smallest ready node at every step
    greedily builds the smallest sequence.
    """
    g, indeg = _adjacency(n, edges)
    heap = [u for u in range(n) if indeg[u] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        u = heapq.heappop(heap)
        order.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)
    return order if len(order) == n else []


def topo_levels(n, edges):
    """Nodes grouped into rounds: everything in a level can be done in parallel.

    len(levels) answers "minimum number of semesters / build rounds". Returns
    [] on a cycle.
    """
    g, indeg = _adjacency(n, edges)
    frontier = [u for u in range(n) if indeg[u] == 0]
    levels, done = [], 0
    while frontier:
        levels.append(frontier)
        done += len(frontier)
        nxt = []
        for u in frontier:
            for v in g[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    nxt.append(v)
        frontier = nxt
    return levels if done == n else []


def has_unique_topo_order(n, edges):
    """True when exactly one valid order exists.

    Whenever two nodes are ready at the same time, either could go first, so
    the order is unique iff the queue holds exactly one node at every step.
    (Equivalently: the order is a Hamiltonian path of the DAG.)
    """
    g, indeg = _adjacency(n, edges)
    q = deque(u for u in range(n) if indeg[u] == 0)
    seen = 0
    while q:
        if len(q) > 1:
            return False
        u = q.popleft()
        seen += 1
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return seen == n


def alien_order(words):
    """Letter order of an alien alphabet, given words sorted in that alphabet.

    The only information a sorted list gives you is at the *first differing
    character* of each adjacent pair — that one comparison is an edge; every
    character after it tells you nothing. If no character differs and the
    longer word comes first, the input is impossible ("abc" can never sort
    after "abcd"). Returns "" when the constraints are contradictory.
    """
    g = {c: set() for w in words for c in w}
    indeg = {c: 0 for c in g}

    for a, b in zip(words, words[1:]):
        for x, y in zip(a, b):
            if x != y:
                if y not in g[x]:
                    g[x].add(y)
                    indeg[y] += 1
                break
        else:
            if len(a) > len(b):
                return ""  # a prefix must come first

    q = deque(c for c in indeg if indeg[c] == 0)
    out = []
    while q:
        c = q.popleft()
        out.append(c)
        for d in g[c]:
            indeg[d] -= 1
            if indeg[d] == 0:
                q.append(d)
    return "".join(out) if len(out) == len(indeg) else ""


# ------------------------------------------------------------------------ tests


def is_valid_topo(n, edges, order):
    """Every edge must point forwards in the order."""
    if sorted(order) != list(range(n)):
        return False
    pos = {u: i for i, u in enumerate(order)}
    return all(pos[u] < pos[v] for u, v in edges)


DIAMOND = (4, [(0, 1), (0, 2), (1, 3), (2, 3)])


def test_kahn_produces_a_valid_order():
    n, edges = DIAMOND
    assert is_valid_topo(n, edges, topo_sort_kahn(n, edges))


def test_dfs_produces_a_valid_order():
    from modeling import build_graph

    n, edges = DIAMOND
    g = build_graph(n, edges, directed=True)
    assert is_valid_topo(n, edges, topo_sort_dfs(n, g))


def test_both_methods_agree_on_validity_over_random_dags():
    import random

    from modeling import build_graph

    random.seed(11)
    for _ in range(30):
        n = random.randint(2, 9)
        # edges only ever point from a lower label to a higher one -> acyclic
        edges = [
            (u, v)
            for u in range(n)
            for v in range(u + 1, n)
            if random.random() < 0.35
        ]
        g = build_graph(n, edges, directed=True)
        for order in (topo_sort_kahn(n, edges), topo_sort_dfs(n, g)):
            assert is_valid_topo(n, edges, order)


def test_cycle_yields_no_order():
    n, edges = 3, [(0, 1), (1, 2), (2, 0)]
    assert topo_sort_kahn(n, edges) == []
    assert topo_sort_lexicographic(n, edges) == []
    assert topo_levels(n, edges) == []
    assert topo_sort_dfs(n, {0: [1], 1: [2], 2: [0]}) == []


def test_partial_cycle_yields_no_order():
    # 0 -> 1 is fine, but 2 <-> 3 is stuck, so nothing can be ordered
    assert topo_sort_kahn(4, [(0, 1), (2, 3), (3, 2)]) == []


def test_no_edges_is_just_the_nodes():
    assert topo_sort_kahn(3, []) == [0, 1, 2]
    assert topo_levels(3, []) == [[0, 1, 2]]  # all at once


def test_lexicographic_picks_the_smallest_ready_node():
    n, edges = 4, [(2, 0), (2, 1)]
    # 2 must come before 0 and 1; 3 is free but larger than both, so it waits
    assert topo_sort_lexicographic(n, edges) == [2, 0, 1, 3]
    assert is_valid_topo(n, edges, topo_sort_lexicographic(n, edges))
    # plain Kahn is also valid here, just not the smallest
    assert topo_sort_kahn(n, edges) == [2, 3, 0, 1]


def test_levels_are_parallel_rounds():
    n, edges = DIAMOND
    assert topo_levels(n, edges) == [[0], [1, 2], [3]]  # 3 rounds, 1 and 2 together
    # a chain cannot be parallelised at all
    assert len(topo_levels(4, [(0, 1), (1, 2), (2, 3)])) == 4


def test_uniqueness():
    assert has_unique_topo_order(4, [(0, 1), (1, 2), (2, 3)]) is True  # a chain
    assert has_unique_topo_order(*DIAMOND) is False  # 1 and 2 can swap
    assert has_unique_topo_order(2, []) is False
    assert has_unique_topo_order(3, [(0, 1), (1, 2), (2, 0)]) is False  # cycle


def test_alien_order():
    assert alien_order(["wrt", "wrf", "er", "ett", "rftt"]) == "wertf"
    assert alien_order(["z", "x"]) == "zx"


def test_alien_order_rejects_contradictions():
    assert alien_order(["z", "x", "z"]) == ""       # cycle: z<x and x<z
    assert alien_order(["abc", "ab"]) == ""         # prefix after longer word


def test_alien_order_with_no_information():
    # Nothing distinguishes the letters, so any order is fine -- just not "".
    assert sorted(alien_order(["ab", "ab"])) == ["a", "b"]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
