"""Level-order BFS — process a tree one row at a time.

Signs: per-level processing — right/left side view, zigzag order, level
       averages or maxima, minimum depth, "connect next-right pointers",
       anything phrased as rows.
Approach: a queue, and at the start of each level snapshot size = len(q).
          Pop exactly that many nodes; everything they enqueue belongs to the
          next level. Side views and zigzag are just post-processing of the
          rows.
Complexity: O(n) time, O(w) space where w is the widest level (up to n/2).
Gotchas: take len(q) *before* the inner loop — reading it live mixes levels.
         Minimum depth wants BFS, not DFS: the first leaf dequeued is the
         answer, and a one-child node is not a leaf. Zigzag should reverse
         the finished row, not the order children are enqueued — flipping the
         enqueue order corrupts the rows after it. No recursion here, so deep
         trees are fine.

Run the tests at the bottom with:  python3 binary_trees/level_order.py
"""

import random
from collections import deque

from tree import bfs_dist, build, nodes, random_tree, skewed, to_graph


# ---------------------------------------------------------------- implementation


def levels(root):
    """Node values grouped by depth, each row left to right."""
    if not root:
        return []
    res, q = [], deque([root])
    while q:
        row = []
        for _ in range(len(q)):
            n = q.popleft()
            row.append(n.val)
            if n.left:
                q.append(n.left)
            if n.right:
                q.append(n.right)
        res.append(row)
    return res


def right_view(root):
    return [row[-1] for row in levels(root)]


def left_view(root):
    return [row[0] for row in levels(root)]


def zigzag(root):
    return [row if i % 2 == 0 else row[::-1] for i, row in enumerate(levels(root))]


def level_averages(root):
    return [sum(row) / len(row) for row in levels(root)]


def min_depth(root):
    """Nodes on the shortest root-to-leaf path. Stops at the first leaf."""
    if not root:
        return 0
    q, depth = deque([root]), 1
    while q:
        for _ in range(len(q)):
            n = q.popleft()
            if not n.left and not n.right:
                return depth
            if n.left:
                q.append(n.left)
            if n.right:
                q.append(n.right)
        depth += 1


# ------------------------------------------------------------------------ tests


def _levels_brute(root):
    """Group nodes by BFS distance; preorder already lists each row left to right."""
    if not root:
        return []
    dist = bfs_dist(to_graph(root), root)
    rows = [[] for _ in range(max(dist.values()) + 1)]
    for n in nodes(root):
        rows[dist[n]].append(n.val)
    return rows


def test_known():
    t = build([3, 9, 20, None, None, 15, 7])
    assert levels(t) == [[3], [9, 20], [15, 7]]
    assert zigzag(t) == [[3], [20, 9], [15, 7]]
    assert level_averages(t) == [3.0, 14.5, 11.0]
    assert min_depth(t) == 2


def test_views_see_past_short_branches():
    #     1
    #    / \
    #   2   3
    #    \
    #     5
    t = build([1, 2, 3, None, 5])
    assert right_view(t) == [1, 3, 5]  # 5 is visible from the right: nothing to its right
    assert left_view(t) == [1, 2, 5]


def test_min_depth_ignores_one_child_nodes():
    # root has only a right child, so the root is not a leaf: answer is 5, not 1
    assert min_depth(build([2, None, 3, None, 4, None, 5, None, 6])) == 5


def test_matches_brute_force_on_random_trees():
    rng = random.Random(50)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 40))
        rows = _levels_brute(t)
        assert levels(t) == rows
        assert right_view(t) == [r[-1] for r in rows]
        assert [r for i, r in enumerate(zigzag(t)) if i % 2] == [r[::-1] for r in rows[1::2]]
        if t:
            dist = bfs_dist(to_graph(t), t)
            leaves = [n for n in nodes(t) if not n.left and not n.right]
            assert min_depth(t) == 1 + min(dist[n] for n in leaves)


def test_empty_and_single():
    assert levels(None) == right_view(None) == zigzag(None) == []
    assert min_depth(None) == 0
    assert levels(build([1])) == [[1]] and min_depth(build([1])) == 1


def test_skewed_both_ways_and_deep():
    assert levels(skewed(3, "left")) == [[1], [2], [3]]
    assert right_view(skewed(3, "left")) == [1, 2, 3]
    assert min_depth(skewed(3, "right")) == 3
    t = skewed(20_000, "right")
    assert len(levels(t)) == min_depth(t) == 20_000


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
