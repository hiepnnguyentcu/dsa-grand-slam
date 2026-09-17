"""Tree DP — per-node state tuples, post-order, and rerooting.

Signs: optimise over a tree where a node's choice is constrained by its parent
       or children — no two adjacent picked (house robber III), cover every
       edge (vertex cover), camera placement, or "answer for every root".
Approach: root the tree, process children before parents, and have each node
          return a small tuple, one value per state:
              take[u] = w[u] + sum(skip[c])
              skip[u] = sum(max(take[c], skip[c]))
          Rerooting ("for every node as root"): one post-order pass for the
          subtree answers, then one pre-order pass that pushes the parent's
          answer down — moving the root across edge (u, c) changes the answer
          by a known amount.
Complexity: O(n * states) time, O(n) space.
Gotchas:
  - Recursive DFS overflows at depth ~1000; a path-shaped tree of 10^5 nodes
    is a normal test case. Build a BFS order and walk it backwards instead.
  - Trees here are adjacency dicts {node: [neighbour, ...]}, undirected, as in
    graphs/. Skip the parent when visiting children, or you loop forever.
  - Rerooting by running the O(n) DP from every root is O(n^2); the second
    pass is what makes it O(n).

Run the tests at the bottom with:  python3 dynamic_programming/tree_dp_problems.py
"""

import random
from collections import deque
from itertools import combinations


# ---------------------------------------------------------------- implementation


def bfs_order(adj, root):
    """(order, parent): nodes so every parent precedes its children."""
    parent = {root: None}
    order = [root]
    q = deque([root])
    while q:
        u = q.popleft()
        for v in adj.get(u, ()):
            if v not in parent:
                parent[v] = u
                order.append(v)
                q.append(v)
    return order, parent


def max_independent_set(adj, weight, root):
    """Max total weight of nodes with no two adjacent (house robber III)."""
    order, parent = bfs_order(adj, root)
    take, skip = {}, {}
    for u in reversed(order):  # children are finished before u
        kids = [v for v in adj.get(u, ()) if v != parent[u]]
        take[u] = weight[u] + sum(skip[c] for c in kids)
        skip[u] = sum(max(take[c], skip[c]) for c in kids)
    return max(take[root], skip[root])


def min_vertex_cover(adj, root):
    """Fewest nodes such that every edge has at least one end chosen.

    If u is not chosen, every child must be (the edge to it needs covering).
    """
    order, parent = bfs_order(adj, root)
    inc, exc = {}, {}
    for u in reversed(order):
        kids = [v for v in adj.get(u, ()) if v != parent[u]]
        inc[u] = 1 + sum(min(inc[c], exc[c]) for c in kids)
        exc[u] = sum(inc[c] for c in kids)
    return min(inc[root], exc[root])


def sum_of_distances(n, edges):
    """ans[u] = sum of distances from u to every node, for every u, in O(n).

    Pass 1 (post-order): size[u] and down[u] = sum of distances into u's
    subtree. Pass 2 (pre-order): moving the root from u to child c brings
    size[c] nodes one step closer and the other n - size[c] one step further:
        ans[c] = ans[u] - size[c] + (n - size[c])
    """
    adj = {i: [] for i in range(n)}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    order, parent = bfs_order(adj, 0)
    size, down = [1] * n, [0] * n
    for u in reversed(order):
        p = parent[u]
        if p is not None:
            size[p] += size[u]
            down[p] += down[u] + size[u]
    ans = [0] * n
    ans[0] = down[0]
    for u in order[1:]:
        ans[u] = ans[parent[u]] - size[u] + (n - size[u])
    return ans


# ------------------------------------------------------------------------ tests


def random_tree(n, rng):
    """Attach each node to a random earlier one — always a tree."""
    edges = [(i, rng.randrange(i)) for i in range(1, n)]
    adj = {i: [] for i in range(n)}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    return adj, edges


def test_house_robber_iii():
    #       3
    #      / \
    #     2   3
    #      \   \
    #       3   1
    adj = {0: [1, 2], 1: [0, 3], 2: [0, 4], 3: [1], 4: [2]}
    w = {0: 3, 1: 2, 2: 3, 3: 3, 4: 1}
    assert max_independent_set(adj, w, 0) == 7
    assert max_independent_set({0: []}, {0: 5}, 0) == 5


def test_independent_set_and_cover_match_brute_force():
    rng = random.Random(120)
    for _ in range(200):
        n = rng.randint(1, 10)
        adj, edges = random_tree(n, rng)
        w = {i: rng.randint(0, 9) for i in range(n)}
        best_is, best_vc = 0, n
        for mask in range(1 << n):
            chosen = {i for i in range(n) if mask >> i & 1}
            if all(not (a in chosen and b in chosen) for a, b in edges):
                best_is = max(best_is, sum(w[i] for i in chosen))
            if all(a in chosen or b in chosen for a, b in edges):
                best_vc = min(best_vc, len(chosen))
        root = rng.randrange(n)  # the answer must not depend on the root
        assert max_independent_set(adj, w, root) == best_is
        assert min_vertex_cover(adj, root) == best_vc


def test_sum_of_distances():
    assert sum_of_distances(6, [(0, 1), (0, 2), (2, 3), (2, 4), (2, 5)]) == [8, 12, 6, 10, 10, 10]
    assert sum_of_distances(1, []) == [0]
    assert sum_of_distances(2, [(1, 0)]) == [1, 1]


def test_rerooting_matches_bfs_from_every_node():
    rng = random.Random(121)
    for _ in range(100):
        n = rng.randint(1, 30)
        adj, edges = random_tree(n, rng)
        expected = []
        for s in range(n):
            dist, q = {s: 0}, deque([s])
            while q:
                u = q.popleft()
                for v in adj[u]:
                    if v not in dist:
                        dist[v] = dist[u] + 1
                        q.append(v)
            expected.append(sum(dist.values()))
        assert sum_of_distances(n, edges) == expected


def test_deep_path_needs_no_recursion():
    n = 100_000
    adj = {i: [] for i in range(n)}
    for i in range(1, n):
        adj[i - 1].append(i)
        adj[i].append(i - 1)
    assert max_independent_set(adj, {i: 1 for i in range(n)}, 0) == n // 2
    assert min_vertex_cover(adj, 0) == n // 2
    ans = sum_of_distances(n, [(i - 1, i) for i in range(1, n)])
    assert ans[0] == n * (n - 1) // 2


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
