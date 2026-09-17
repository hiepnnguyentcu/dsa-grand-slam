"""Convert a tree to an undirected graph — when movement can go back up.

Signs: "all nodes at distance k from target", time for an infection/fire to
       spread from one node to the whole tree, anything where a step may go to
       the parent as well as to a child.
Approach: one iterative walk records every node's parent. From then on each
          node has up to three neighbours (left, right, parent) and the
          problem is plain BFS from the start node with a visited set.
Complexity: O(n) time and space.
Gotchas: the visited set is mandatory now — without it BFS bounces between a
         node and its parent forever. Stop BFS after k rings rather than
         filtering distances afterwards. If the start is given by *value*,
         find the node during the parent walk (values must then be unique).
         Iterative throughout, so depth is not a concern.

Run the tests at the bottom with:  python3 binary_trees/tree_as_graph.py
"""

import random
from collections import deque

from tree import bfs_dist, build, nodes, random_tree, skewed, to_graph


# ---------------------------------------------------------------- implementation


def _parents(root):
    parent, st = {root: None}, [root] if root else []
    while st:
        n = st.pop()
        for ch in (n.left, n.right):
            if ch:
                parent[ch] = n
                st.append(ch)
    return parent


def distance_k(root, target, k):
    """Values of all nodes exactly k edges from target, in BFS order."""
    parent = _parents(root)
    q, seen = deque([target]), {target}
    for _ in range(k):
        if not q:
            break
        for _ in range(len(q)):
            n = q.popleft()
            for nb in (n.left, n.right, parent[n]):
                if nb and nb not in seen:
                    seen.add(nb)
                    q.append(nb)
    return [n.val for n in q]


def burn_time(root, start_val):
    """Minutes until everything burns when a fire starts at the node valued start_val.

    That is the start node's eccentricity: the number of BFS rings minus one.
    """
    parent = _parents(root)
    start = next(n for n in parent if n and n.val == start_val)
    q, seen, minutes = deque([start]), {start}, -1
    while q:
        minutes += 1
        for _ in range(len(q)):
            n = q.popleft()
            for nb in (n.left, n.right, parent[n]):
                if nb and nb not in seen:
                    seen.add(nb)
                    q.append(nb)
    return minutes


# ------------------------------------------------------------------------ tests


def test_distance_k_known():
    #         3
    #       /   \
    #      5     1
    #     / \   / \
    #    6   2 0   8
    #       / \
    #      7   4
    t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    five = t.left
    assert sorted(distance_k(t, five, 2)) == [1, 4, 7]
    assert distance_k(t, five, 0) == [5]
    assert sorted(distance_k(t, five, 3)) == [0, 8]
    assert distance_k(t, five, 10) == []


def test_burn_time_known():
    #        1
    #       / \
    #      5   3
    #       \  / \
    #        4 10 6
    #       / \
    #      9   2
    t = build([1, 5, 3, None, 4, 10, 6, 9, 2])
    assert burn_time(t, 3) == 4
    assert burn_time(t, 2) == 5  # 2-4-5-1-3-{10,6} is five edges
    assert burn_time(build([1]), 1) == 0


def test_matches_brute_force():
    rng = random.Random(90)
    for _ in range(200):
        n = rng.randint(1, 30)
        t = random_tree(rng, n, values=rng.sample(range(100), n))
        g = to_graph(t)
        for target in rng.sample(nodes(t), min(n, 4)):
            dist = bfs_dist(g, target)
            assert burn_time(t, target.val) == max(dist.values())
            for k in range(0, 6):
                want = sorted(x.val for x, d in dist.items() if d == k)
                assert sorted(distance_k(t, target, k)) == want


def test_skewed_both_ways():
    for side in ("left", "right"):
        t = skewed(7, side)  # 1-2-3-4-5-6-7
        mid = nodes(t)[3]
        assert sorted(distance_k(t, mid, 2)) == [2, 6]
        assert sorted(distance_k(t, mid, 3)) == [1, 7]
        assert burn_time(t, 4) == 3
        assert burn_time(t, 7) == 6


def test_deep_tree():
    t = skewed(20_000, "left")
    assert burn_time(t, 10_000) == 10_000
    assert distance_k(t, nodes(t)[-1], 19_999) == [1]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
