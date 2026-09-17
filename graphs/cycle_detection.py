"""Cycle detection — undirected (DSU or parent-aware DFS) and directed (3-colour).

The two cases are genuinely different problems, which is why both live here:

Undirected
    Signs: "is this a tree", redundant connection, detect any cycle.
    Approach: an edge joining two already-connected nodes closes a cycle (DSU),
              or in DFS terms, reaching an already-seen node that is not the
              one you came from.
    Tree test: connected and E == V - 1. Either alone is not enough.

Directed
    Signs: are these prerequisites satisfiable, deadlock, dependency loop,
           "which nodes never lead into a cycle".
    Approach: 3-colour DFS. WHITE unvisited, GREY on the current path, BLACK
              finished. An edge into a GREY node is a back edge -> cycle. An
              edge into a BLACK node is fine — that subtree is already known to
              be clean.

Complexity: O(V + E) for all of them.
Gotchas: the undirected "skip the parent" rule breaks on parallel edges (u-v
         twice IS a cycle) — track edge ids instead if those are possible. A
         self-loop is always a cycle. The directed recursion inherits Python's
         ~1000-frame limit.

Run the tests at the bottom with:  python3 graphs/cycle_detection.py
"""

from union_find import DSU

WHITE, GREY, BLACK = 0, 1, 2


# -------------------------------------------------------------------- undirected


def undirected_has_cycle(n, edges):
    """DSU version. An edge that fails to union is an edge that closes a cycle."""
    d = DSU(n)
    return any(not d.union(u, v) for u, v in edges)


def undirected_has_cycle_dfs(n, g):
    """DFS version, iterative so deep graphs are safe.

    Carries the node each node was reached from, and ignores exactly that one
    step back. Any *other* seen neighbour means a second route in — a cycle.
    """
    seen = set()
    for s in range(n):
        if s in seen:
            continue
        seen.add(s)
        stack = [(s, -1)]
        while stack:
            u, parent = stack.pop()
            for v in g.get(u, ()):
                if v == parent:
                    parent = -1  # consume the back-edge to the parent just once
                elif v in seen:
                    return True
                else:
                    seen.add(v)
                    stack.append((v, u))
    return False


def redundant_connection(n, edges):
    """The first edge that closes a cycle, or None. Classic 'remove one edge'."""
    d = DSU(n)
    for u, v in edges:
        if not d.union(u, v):
            return (u, v)
    return None


def is_tree(n, edges):
    """A tree is acyclic AND connected: exactly n-1 edges that all do work."""
    if len(edges) != n - 1:
        return False
    d = DSU(n)
    return all(d.union(u, v) for u, v in edges)


# ---------------------------------------------------------------------- directed


def directed_has_cycle(n, g):
    """3-colour DFS. True if any back edge exists."""
    color = [WHITE] * n

    def visit(u):
        color[u] = GREY
        for v in g.get(u, ()):
            if color[v] == GREY:
                return True
            if color[v] == WHITE and visit(v):
                return True
        color[u] = BLACK
        return False

    return any(color[u] == WHITE and visit(u) for u in range(n))


def find_directed_cycle(n, g):
    """One cycle as a node list (first node not repeated at the end), or None.

    Same 3-colour walk, but keeping the current path so the cycle can be cut
    out of it when the back edge is found.
    """
    color = [WHITE] * n
    path, found = [], []

    def visit(u):
        color[u] = GREY
        path.append(u)
        for v in g.get(u, ()):
            if color[v] == GREY:
                found.extend(path[path.index(v):])
                return True
            if color[v] == WHITE and visit(v):
                return True
        color[u] = BLACK
        path.pop()
        return False

    for u in range(n):
        if color[u] == WHITE and visit(u):
            return found
    return None


def eventual_safe_nodes(n, g):
    """Nodes from which *every* path reaches a dead end — no cycle downstream.

    BLACK comes to mean "proven safe", so the colour array doubles as the memo.
    """
    color = [WHITE] * n

    def safe(u):
        if color[u] != WHITE:
            return color[u] == BLACK  # GREY means we looped back into the path
        color[u] = GREY
        for v in g.get(u, ()):
            if not safe(v):
                return False
        color[u] = BLACK
        return True

    return [u for u in range(n) if safe(u)]


# ------------------------------------------------------------------------ tests


def test_undirected_tree_has_no_cycle():
    edges = [(0, 1), (1, 2), (1, 3)]
    assert undirected_has_cycle(4, edges) is False
    assert is_tree(4, edges) is True


def test_undirected_cycle_found():
    edges = [(0, 1), (1, 2), (2, 0)]
    assert undirected_has_cycle(3, edges) is True
    assert is_tree(3, edges) is False
    assert redundant_connection(3, edges) == (2, 0)


def test_not_a_tree_if_disconnected_even_without_a_cycle():
    # 4 nodes, 3 edges, no cycle -- but node 3 is off on its own
    edges = [(0, 1), (1, 2), (0, 2)]
    assert len(edges) == 3
    assert is_tree(4, edges) is False


def test_undirected_dfs_agrees_with_dsu():
    from modeling import build_graph

    cases = [
        (4, [(0, 1), (1, 2), (1, 3)]),            # tree
        (3, [(0, 1), (1, 2), (2, 0)]),            # triangle
        (5, [(0, 1), (2, 3), (3, 4), (4, 2)]),    # cycle in second component
        (2, []),                                   # no edges
        (4, [(0, 1), (2, 3)]),                     # forest
    ]
    for n, edges in cases:
        g = build_graph(n, edges)
        assert undirected_has_cycle_dfs(n, g) == undirected_has_cycle(n, edges)


def test_directed_cycle():
    assert directed_has_cycle(3, {0: [1], 1: [2], 2: [0]}) is True
    assert directed_has_cycle(3, {0: [1], 1: [2], 2: []}) is False


def test_directed_revisit_is_not_a_cycle():
    # Diamond: 3 is reached twice, but never while it is on the current path.
    g = {0: [1, 2], 1: [3], 2: [3], 3: []}
    assert directed_has_cycle(4, g) is False


def test_the_same_edges_undirected_would_be_a_cycle():
    # Direction is the whole story: as an undirected graph the diamond loops.
    from modeling import build_graph

    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
    assert directed_has_cycle(4, build_graph(4, edges, directed=True)) is False
    assert undirected_has_cycle(4, edges) is True


def test_self_loop():
    assert directed_has_cycle(1, {0: [0]}) is True


def test_extract_the_cycle():
    g = {0: [1], 1: [2], 2: [3], 3: [1], 4: [0]}
    cycle = find_directed_cycle(5, g)
    assert cycle == [1, 2, 3]
    # every consecutive pair is a real edge, and it closes back on itself
    assert all(b in g[a] for a, b in zip(cycle, cycle[1:]))
    assert cycle[0] in g[cycle[-1]]
    assert find_directed_cycle(3, {0: [1], 1: [2], 2: []}) is None


def test_safe_nodes():
    g = {0: [1, 2], 1: [2, 3], 2: [5], 3: [0], 4: [5], 5: [], 6: []}
    assert eventual_safe_nodes(7, g) == [2, 4, 5, 6]
    # a graph with no cycles at all: everything is safe
    assert eventual_safe_nodes(3, {0: [1], 1: [2], 2: []}) == [0, 1, 2]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
