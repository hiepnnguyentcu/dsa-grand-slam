"""Return one thing, record another — the global-best pattern.

Signs: diameter, maximum path sum, longest same-value path — any "best path"
       question where the path may *bend* through a node (down-left, up, down-
       right) but a parent can only extend a *straight* branch.
Approach: at each node compute the best single branch from each child. Use
          *both* branches to update a global answer (the path that bends
          here), but return only the *better* branch upward, because a path
          through the parent cannot use both.
Complexity: O(n) time, O(h) space.
Gotchas: clamp negative branches to 0 for path sums — a branch that loses
         money is simply not taken. Do not clamp the node itself: an all-
         negative tree's answer is its largest single value, so `best` starts
         at -inf, not 0. Know your unit: diameter here counts *edges*.
         Recursive forms hit the ~1000-frame limit; the iterative form folds
         children into parents in reversed preorder.

Run the tests at the bottom with:  python3 binary_trees/global_best.py
"""

import random

from tree import bfs_dist, build, nodes, random_tree, skewed, to_graph


# ---------------------------------------------------------------- implementation


def max_path_sum(root):
    """Largest sum over any non-empty node-to-node path. -inf for an empty tree."""
    best = float("-inf")

    def gain(node):
        nonlocal best
        if not node:
            return 0
        l = max(gain(node.left), 0)
        r = max(gain(node.right), 0)
        best = max(best, node.val + l + r)  # the path that bends here
        return node.val + max(l, r)  # the branch a parent may extend

    gain(root)
    return best


def max_path_sum_iterative(root):
    """max_path_sum without recursion: fold children before parents."""
    best, gain = float("-inf"), {None: 0}
    for n in reversed(nodes(root)):
        l, r = max(gain[n.left], 0), max(gain[n.right], 0)
        best = max(best, n.val + l + r)
        gain[n] = n.val + max(l, r)
    return best


def diameter(root):
    """Number of edges on the longest path between any two nodes."""
    best = 0

    def height(node):
        nonlocal best
        if not node:
            return 0
        l, r = height(node.left), height(node.right)
        best = max(best, l + r)  # l and r are node counts == edges down from here
        return 1 + max(l, r)

    height(root)
    return best


def diameter_iterative(root):
    best, height = 0, {None: 0}
    for n in reversed(nodes(root)):
        l, r = height[n.left], height[n.right]
        best = max(best, l + r)
        height[n] = 1 + max(l, r)
    return best


def longest_univalue_path(root):
    """Edges on the longest path whose nodes all share one value.

    Same shape, one twist: a child's branch only counts if the child has the
    same value, otherwise it contributes 0 — the "clamp" is now a value test.
    """
    best = 0

    def arm(node):
        nonlocal best
        if not node:
            return 0
        l, r = arm(node.left), arm(node.right)
        l = l + 1 if node.left and node.left.val == node.val else 0
        r = r + 1 if node.right and node.right.val == node.val else 0
        best = max(best, l + r)
        return max(l, r)

    arm(root)
    return best


# ------------------------------------------------------------------------ tests


def _brute_paths(root, ok=lambda u, v: True):
    """Yield (edges, value-sum) for every u -> v path whose steps all pass ok.

    Paths in a tree are unique, so BFS from every node enumerates each of
    them exactly (twice, once per direction — harmless for a max).
    """
    g = to_graph(root)
    for u in g:
        acc, hops, q = {u: u.val}, {u: 0}, [u]
        for x in q:
            yield hops[x], acc[x]
            for y in g[x]:
                if y not in acc and ok(x, y):
                    acc[y], hops[y] = acc[x] + y.val, hops[x] + 1
                    q.append(y)


def test_path_sum_known():
    assert max_path_sum(build([1, 2, 3])) == 6
    assert max_path_sum(build([-10, 9, 20, None, None, 15, 7])) == 42
    assert max_path_sum(build([-3])) == -3
    assert max_path_sum(build([-2, -1])) == -1  # all negative: best single node
    assert max_path_sum(build([2, -1])) == 2  # a losing branch is dropped
    assert max_path_sum(None) == float("-inf")


def test_path_sum_matches_brute_force():
    rng = random.Random(20)
    for _ in range(300):
        t = random_tree(rng, rng.randint(1, 25))
        expected = max(s for _, s in _brute_paths(t))
        assert max_path_sum(t) == max_path_sum_iterative(t) == expected


def test_diameter_known():
    assert diameter(build([1, 2, 3, 4, 5])) == 3
    assert diameter(build([1, 2])) == 1
    assert diameter(build([1])) == 0
    assert diameter(None) == 0 == diameter_iterative(None)


def test_diameter_need_not_pass_through_root():
    #       1
    #      /
    #     2
    #    / \
    #   3   4
    #  /     \
    # 5       6
    t = build([1, 2, None, 3, 4, 5, None, None, 6])
    assert diameter(t) == 4  # 5-3-2-4-6, root not involved
    assert max(bfs_dist(to_graph(t), t).values()) == 3  # through-root would give only 3


def test_diameter_matches_brute_force():
    rng = random.Random(21)
    for _ in range(300):
        t = random_tree(rng, rng.randint(1, 30))
        expected = max(h for h, _ in _brute_paths(t))
        assert diameter(t) == diameter_iterative(t) == expected


def test_univalue_known():
    assert longest_univalue_path(build([5, 4, 5, 1, 1, None, 5])) == 2
    assert longest_univalue_path(build([1, 4, 5, 4, 4, None, 5])) == 2
    assert longest_univalue_path(None) == 0


def test_univalue_matches_brute_force():
    rng = random.Random(22)
    for _ in range(300):
        t = random_tree(rng, rng.randint(1, 30), lo=0, hi=2)  # few values -> long runs
        expected = max(h for h, _ in _brute_paths(t, lambda u, v: u.val == v.val))
        assert longest_univalue_path(t) == expected


def test_skewed_both_ways():
    for side in ("left", "right"):
        t = skewed(6, side)  # values 1..6
        assert diameter(t) == diameter_iterative(t) == 5
        assert max_path_sum(t) == max_path_sum_iterative(t) == 21


def test_iterative_survives_deep_tree():
    t = skewed(10_000, "right")
    assert diameter_iterative(t) == 9_999
    assert max_path_sum_iterative(t) == 10_000 * 10_001 // 2
    try:
        diameter(t)
    except RecursionError:
        pass
    else:
        raise AssertionError("expected diameter to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
