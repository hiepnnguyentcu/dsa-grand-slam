"""Bipartite check — 2-colouring by BFS.

Signs: split into two groups with no conflict *inside* a group, "two teams",
       "can these people be seated at two tables", detecting an odd cycle.
Approach: colour a node, then force every neighbour to the opposite colour and
          propagate. A neighbour that already has your own colour is a
          contradiction, and the graph is not bipartite.
Complexity: O(V + E).
Theory worth knowing: a graph is bipartite iff it contains no odd-length cycle.
    An even cycle alternates colours and closes consistently; an odd one cannot.
    That is why the BFS colouring never needs to backtrack — the first
    contradiction it meets is proof, not a wrong guess.
Gotchas:
  - Restart from every uncoloured node. A disconnected graph can hide its odd
    cycle in a later component, and stopping after the first component is the
    usual bug.
  - Which colour you start a component with is arbitrary, so the colouring is
    not unique — test that it is *valid*, not that it equals some fixed answer.

Run the tests at the bottom with:  python3 graphs/bipartite.py
"""

from collections import deque


# ---------------------------------------------------------------- implementation


def two_coloring(n, g):
    """A valid 2-colouring as a list of 0/1, or None if the graph is not bipartite."""
    color = [-1] * n
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in g.get(u, ()):
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return None
    return color


def is_bipartite(n, g):
    return two_coloring(n, g) is not None


def possible_bipartition(n, dislikes):
    """Can n people split into two groups so that no pair who dislike each other share one.

    The classic disguise: "dislikes" are edges, "two groups" is a 2-colouring.
    Recognising that is the whole problem.
    """
    g = {u: [] for u in range(n)}
    for u, v in dislikes:
        g[u].append(v)
        g[v].append(u)
    return is_bipartite(n, g)


# ------------------------------------------------------------------------ tests


def from_edges(n, edges):
    g = {u: [] for u in range(n)}
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    return g


def test_even_cycle_is_bipartite():
    assert is_bipartite(4, from_edges(4, [(0, 1), (1, 2), (2, 3), (3, 0)])) is True


def test_odd_cycle_is_not():
    assert is_bipartite(3, from_edges(3, [(0, 1), (1, 2), (2, 0)])) is False


def test_classic_cases():
    assert is_bipartite(4, {0: [1, 2, 3], 1: [0, 2], 2: [0, 1, 3], 3: [0, 2]}) is False
    assert is_bipartite(4, {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [0, 2]}) is True


def test_trees_and_empty_graphs_are_always_bipartite():
    assert is_bipartite(1, {0: []}) is True
    assert is_bipartite(3, {0: [], 1: [], 2: []}) is True
    assert is_bipartite(5, from_edges(5, [(0, 1), (0, 2), (1, 3), (1, 4)])) is True


def test_must_check_every_component():
    # Component {0,1} is fine; the odd cycle hides in {2,3,4}.
    g = from_edges(5, [(0, 1), (2, 3), (3, 4), (4, 2)])
    assert is_bipartite(5, g) is False


def test_self_loop_is_never_bipartite():
    assert is_bipartite(2, {0: [0], 1: []}) is False


def test_returned_colouring_is_valid():
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 5), (5, 4)]
    g = from_edges(6, edges)
    color = two_coloring(6, g)
    assert color is not None
    assert all(color[u] != color[v] for u, v in edges)


def test_matches_brute_force_over_all_colourings():
    import random
    from itertools import product

    random.seed(79)
    for _ in range(40):
        n = random.randint(1, 8)
        edges = [
            (u, v) for u in range(n) for v in range(u + 1, n) if random.random() < 0.3
        ]
        g = from_edges(n, edges)

        # try literally every assignment of two colours
        brute = any(
            all(c[u] != c[v] for u, v in edges)
            for c in product((0, 1), repeat=n)
        )
        assert is_bipartite(n, g) == brute

        color = two_coloring(n, g)
        if color is not None:
            assert all(color[u] != color[v] for u, v in edges)


def test_odd_cycle_is_exactly_the_obstruction():
    # Even cycles of every size are bipartite, odd ones never are.
    for k in range(3, 10):
        cycle = [(i, (i + 1) % k) for i in range(k)]
        assert is_bipartite(k, from_edges(k, cycle)) is (k % 2 == 0)


def test_possible_bipartition():
    assert possible_bipartition(4, [(0, 1), (1, 2), (2, 3)]) is True
    assert possible_bipartition(3, [(0, 1), (1, 2), (0, 2)]) is False
    assert possible_bipartition(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]) is False
    assert possible_bipartition(4, []) is True


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
