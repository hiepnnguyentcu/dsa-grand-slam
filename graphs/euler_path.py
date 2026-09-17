"""Eulerian path — Hierholzer's algorithm, using every EDGE exactly once.

Signs: "use every ticket / road / domino exactly once", reconstruct an
       itinerary, de Bruijn sequences, the Seven Bridges of Konigsberg.
       Note the contrast with Hamiltonian paths (every *node* once), which are
       NP-hard. Edges are easy; nodes are not.
Existence (directed, ignoring nodes with no edges):
    circuit : in-degree == out-degree everywhere, and all edges in one component
    path    : exactly one node with out - in == 1 (the start), exactly one with
              in - out == 1 (the end), everything else balanced
Approach: walk forward consuming edges until stuck. Getting stuck is not a
          failure — it can only happen at the required end node. Then back out,
          and any node still holding unused edges spawns a detour that gets
          spliced in. Appending nodes as you retreat and reversing at the end
          performs that splicing for free.
Complexity: O(E), or O(E log E) if you sort the adjacency for lexicographic order.
Gotchas:
  - Consume each edge (pop it) rather than marking nodes visited. Nodes get
    revisited constantly; edges must not.
  - Check the degree conditions first — Hierholzer will happily return a partial
    walk on a graph that has no Eulerian path at all. The length check
    (len(path) == len(edges) + 1) is the cheap catch-all.
  - Sort the adjacency in *descending* order when popping from the end, so the
    smallest option is taken first.

Run the tests at the bottom with:  python3 graphs/euler_path.py
"""

from collections import defaultdict


# ---------------------------------------------------------------- implementation


def euler_degrees(edges):
    """(out_degree, in_degree) as dicts over every node that appears."""
    out, inn = defaultdict(int), defaultdict(int)
    for u, v in edges:
        out[u] += 1
        inn[v] += 1
    return out, inn


def euler_start_node(edges):
    """Where an Eulerian path must begin, or None if no such path exists.

    Also rejects graphs whose edges sit in more than one component — degrees can
    balance perfectly across two disconnected loops, and a single walk still
    cannot cover both.
    """
    if not edges:
        return None
    out, inn = euler_degrees(edges)
    nodes = set(out) | set(inn)

    start, end, extra = None, None, 0
    for u in nodes:
        diff = out[u] - inn[u]
        if diff == 1:
            if start is not None:
                return None
            start = u
        elif diff == -1:
            if end is not None:
                return None
            end = u
        elif diff != 0:
            return None

    if (start is None) != (end is None):
        return None  # one unbalanced end without the other is impossible

    # all edges must be reachable from the start, ignoring direction
    from union_find import DictDSU

    d = DictDSU()
    for u, v in edges:
        d.union(u, v)
    if len({d.find(u) for u in nodes}) != 1:
        return None

    return start if start is not None else min(nodes)


def has_euler_path(edges):
    return euler_start_node(edges) is not None


def has_euler_circuit(edges):
    """A closed walk: every degree balanced, and all edges in one component."""
    if not edges:
        return False
    out, inn = euler_degrees(edges)
    if any(out[u] != inn[u] for u in set(out) | set(inn)):
        return False
    return euler_start_node(edges) is not None


def euler_path(edges, start=None):
    """The node sequence of an Eulerian path, or None if there is not one.

    Ties are broken lexicographically: the adjacency is sorted descending so
    that popping from the end yields the smallest next node.
    """
    if not edges:
        return None
    if start is None:
        start = euler_start_node(edges)
        if start is None:
            return None

    g = defaultdict(list)
    for u, v in sorted(edges, reverse=True):
        g[u].append(v)  # descending, so pop() gives the smallest

    path, stack = [], [start]
    while stack:
        while g[stack[-1]]:
            stack.append(g[stack[-1]].pop())  # walk until stuck
        path.append(stack.pop())              # retreat, recording as we go

    path.reverse()
    return path if len(path) == len(edges) + 1 else None


def find_itinerary(tickets, start="JFK"):
    """Reconstruct a full itinerary from a pile of one-way tickets.

    Guaranteed to exist in the classic statement, so the start is forced rather
    than derived — which is also why the degree conditions are not checked here.
    """
    return euler_path([tuple(t) for t in tickets], start=start)


# ------------------------------------------------------------------------ tests


def test_itinerary():
    tickets = [("MUC", "LHR"), ("JFK", "MUC"), ("SFO", "SJC"), ("LHR", "SFO")]
    assert find_itinerary(tickets) == ["JFK", "MUC", "LHR", "SFO", "SJC"]


def test_itinerary_prefers_the_smaller_airport():
    tickets = [
        ("JFK", "SFO"), ("JFK", "ATL"), ("SFO", "ATL"),
        ("ATL", "JFK"), ("ATL", "SFO"),
    ]
    # ATL before SFO at the first fork, even though SFO would also work
    assert find_itinerary(tickets) == ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"]


def test_getting_stuck_early_is_not_a_failure():
    # From JFK the smaller choice is ATL, which dead-ends immediately. The
    # detour through SFO has to be spliced in ahead of it.
    tickets = [("JFK", "KUL"), ("JFK", "NRT"), ("NRT", "JFK")]
    assert find_itinerary(tickets) == ["JFK", "NRT", "JFK", "KUL"]


def test_uses_every_edge_exactly_once():
    import random

    random.seed(107)
    for _ in range(40):
        # a random closed walk, so an Eulerian circuit is guaranteed to exist
        n = random.randint(2, 6)
        length = random.randint(2, 12)
        walk = [random.randrange(n) for _ in range(length)]
        edges = list(zip(walk, walk[1:])) + [(walk[-1], walk[0])]

        path = euler_path(edges)
        assert path is not None
        assert len(path) == len(edges) + 1
        used = sorted(zip(path, path[1:]))
        assert used == sorted(edges)  # every edge, with multiplicity


def test_degree_conditions():
    # balanced -> a circuit
    assert has_euler_circuit([(0, 1), (1, 2), (2, 0)]) is True
    assert has_euler_path([(0, 1), (1, 2), (2, 0)]) is True

    # one surplus out and one surplus in -> a path but no circuit
    assert has_euler_path([(0, 1), (1, 2)]) is True
    assert has_euler_circuit([(0, 1), (1, 2)]) is False


def test_rejects_graphs_with_no_euler_path():
    # node 0 has out-degree 3, so three separate walks would be needed
    assert has_euler_path([(0, 1), (0, 2), (0, 3)]) is False
    assert euler_path([(0, 1), (0, 2), (0, 3)]) is None


def test_rejects_disconnected_edges():
    # Degrees balance in each loop separately, but no single walk covers both.
    edges = [(0, 1), (1, 0), (2, 3), (3, 2)]
    assert has_euler_path(edges) is False
    assert euler_path(edges) is None


def test_start_node_is_the_surplus_out_degree():
    assert euler_start_node([(5, 1), (1, 2)]) == 5
    assert euler_start_node([(0, 1), (1, 2), (2, 0)]) == 0  # balanced -> smallest
    assert euler_start_node([]) is None


def test_single_edge_and_self_loop():
    assert euler_path([(0, 1)]) == [0, 1]
    assert euler_path([(0, 0)]) == [0, 0]


def test_path_starts_and_ends_where_the_degrees_say():
    edges = [(0, 1), (1, 2), (2, 1), (1, 3)]
    out, inn = euler_degrees(edges)
    path = euler_path(edges)
    assert path is not None
    assert out[path[0]] - inn[path[0]] == 1
    assert inn[path[-1]] - out[path[-1]] == 1
    assert len(path) == len(edges) + 1


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
