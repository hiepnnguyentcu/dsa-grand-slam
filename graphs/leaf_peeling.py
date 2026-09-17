"""Leaf peeling — topological trimming on an undirected tree.

Signs: centres of a tree, minimum-height-tree roots, "remove nodes layer by
       layer from the outside in", anything where the answer lives in the
       middle of a tree.
Approach: Kahn's algorithm with degree 1 standing in for indegree 0. Strip all
          current leaves at once, which exposes a new layer of leaves, and
          repeat. Stop when 2 or fewer nodes remain — those are the centres.
Complexity: O(V) time and space.

Why at most two centres: the centres are the midpoint of the tree's longest
path (its diameter). A path of odd length has one middle node, a path of even
length has two. There is never a third.

Gotchas: this consumes the adjacency structure as it peels, so hand it a copy
         if you still need the tree afterwards. n <= 2 has to be special-cased
         because the loop would never run.

Run the tests at the bottom with:  python3 graphs/leaf_peeling.py
"""


# ---------------------------------------------------------------- implementation


def tree_centers(n, edges):
    """The 1 or 2 centre nodes of a tree. Roots that minimise tree height."""
    if n <= 2:
        return list(range(n))

    g = {u: set() for u in range(n)}
    for u, v in edges:
        g[u].add(v)
        g[v].add(u)

    leaves = [u for u in range(n) if len(g[u]) == 1]
    remaining = n
    while remaining > 2:
        remaining -= len(leaves)
        nxt = []
        for u in leaves:
            v = g[u].pop()        # a leaf has exactly one neighbour
            g[v].discard(u)
            if len(g[v]) == 1:    # that neighbour just became a leaf
                nxt.append(v)
        leaves = nxt
    return sorted(leaves)


def tree_diameter(n, edges):
    """Length of the longest path in the tree, in edges.

    Falls out of the peeling: each round strips one layer, so the diameter is
    twice the number of rounds, plus one more if two centres survived (the
    edge between them).
    """
    if n <= 1:
        return 0
    g = {u: set() for u in range(n)}
    for u, v in edges:
        g[u].add(v)
        g[v].add(u)

    leaves = [u for u in range(n) if len(g[u]) == 1]
    remaining, rounds = n, 0
    while remaining > 2:
        remaining -= len(leaves)
        rounds += 1
        nxt = []
        for u in leaves:
            v = g[u].pop()
            g[v].discard(u)
            if len(g[v]) == 1:
                nxt.append(v)
        leaves = nxt
    return 2 * rounds + (1 if remaining == 2 else 0)


# ------------------------------------------------------------------------ tests


def eccentricities(n, edges):
    """Brute force: the distance from each node to the node furthest from it.

    A centre is a node whose eccentricity is minimal — that is the definition
    tree_centers has to reproduce.
    """
    from bfs import bfs_distances
    from modeling import build_graph

    g = build_graph(n, edges)
    return [max(bfs_distances(g, u).values()) for u in range(n)]


def test_star_has_one_center():
    assert tree_centers(4, [(1, 0), (1, 2), (1, 3)]) == [1]


def test_path_of_even_node_count_has_two_centers():
    assert tree_centers(6, [(3, 0), (3, 1), (3, 2), (3, 4), (5, 4)]) == [3, 4]


def test_tiny_trees():
    assert tree_centers(1, []) == [0]
    assert tree_centers(2, [(0, 1)]) == [0, 1]


def test_straight_paths():
    path = lambda k: [(i, i + 1) for i in range(k - 1)]
    assert tree_centers(5, path(5)) == [2]       # odd -> single middle
    assert tree_centers(4, path(4)) == [1, 2]    # even -> two middles


def test_centers_minimise_height():
    cases = [
        (4, [(1, 0), (1, 2), (1, 3)]),
        (6, [(3, 0), (3, 1), (3, 2), (3, 4), (5, 4)]),
        (7, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]),
        (7, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]),
        (5, [(0, 1), (0, 2), (0, 3), (3, 4)]),
    ]
    for n, edges in cases:
        ecc = eccentricities(n, edges)
        best = min(ecc)
        assert tree_centers(n, edges) == [u for u in range(n) if ecc[u] == best]


def test_there_are_never_more_than_two_centers():
    import random

    random.seed(3)
    for _ in range(40):
        n = random.randint(1, 30)
        # random tree: every new node attaches to an existing one
        edges = [(random.randrange(u), u) for u in range(1, n)]
        assert 1 <= len(tree_centers(n, edges)) <= 2


def test_diameter():
    path = lambda k: [(i, i + 1) for i in range(k - 1)]
    assert tree_diameter(5, path(5)) == 4
    assert tree_diameter(4, path(4)) == 3
    assert tree_diameter(4, [(1, 0), (1, 2), (1, 3)]) == 2
    assert tree_diameter(1, []) == 0


def test_diameter_matches_brute_force():
    import random

    random.seed(5)
    for _ in range(25):
        n = random.randint(2, 25)
        edges = [(random.randrange(u), u) for u in range(1, n)]
        assert tree_diameter(n, edges) == max(eccentricities(n, edges))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
