"""Top-down vs bottom-up recursion — the two directions information can flow.

Signs: top-down — the answer at a node depends on its *ancestors* (depth, the
       number spelled so far, the max value on the path, allowed bounds).
       Bottom-up — the answer at a node depends on its *children* (height,
       size, subtree sums, balanced).
Approach: top-down passes state down as parameters and finishes at the
          leaves; bottom-up returns values and finishes at the root. Many
          problems do both at once. Each has an iterative twin: top-down
          becomes a stack of (node, state) pairs; bottom-up becomes a
          post-order walk (or reversed preorder) that fills a dict.
Complexity: O(n) time, O(h) space — h is n for a skewed tree.
Gotchas: CPython's recursion limit is ~1000 frames, so a 10^4-node path
         overflows the recursive forms. Decide what an empty tree means up
         front (depth 0, no numbers) and what a *leaf* is (both children
         missing) — a node with one child is not a leaf, which is the classic
         min-depth / path-sum bug.

Run the tests at the bottom with:  python3 binary_trees/top_down_bottom_up.py
"""

import random

from tree import bfs_dist, build, nodes, random_tree, set_parents, skewed, to_graph


# ---------------------------------------------------------------- implementation


def max_depth(root):
    """Bottom-up: a node's depth is one more than its deeper child's."""
    return 0 if not root else 1 + max(max_depth(root.left), max_depth(root.right))


def max_depth_iterative(root):
    """Top-down twin of max_depth: carry the depth down on the stack.

    Depth is a fact about the path from the root, so it can be pushed down as
    easily as it can be returned up — and pushing it down needs no post-order
    bookkeeping.
    """
    best, st = 0, [(root, 1)] if root else []
    while st:
        n, d = st.pop()
        best = max(best, d)
        for ch in (n.left, n.right):
            if ch:
                st.append((ch, d + 1))
    return best


def subtree_sums(root):
    """Bottom-up, iteratively: {node: sum of its subtree}.

    Reversed preorder visits every child before its parent, which is all a
    bottom-up fold needs — no true post-order stack juggling required.
    """
    total = {}
    for n in reversed(nodes(root)):
        total[n] = n.val + total.get(n.left, 0) + total.get(n.right, 0)
    return total


def root_to_leaf_numbers(root):
    """Top-down: each root-to-leaf path of digits spells a number; list them.

    The number so far is the parameter. It is only *recorded* at a leaf —
    recording at None would count each leaf twice and count one-child nodes
    as path ends.
    """
    res = []

    def dfs(node, acc):
        if not node:
            return
        acc = acc * 10 + node.val
        if not node.left and not node.right:
            res.append(acc)
        dfs(node.left, acc)
        dfs(node.right, acc)

    dfs(root, 0)
    return res


def root_to_leaf_numbers_iterative(root):
    """Same numbers, same (left-to-right) order, with an explicit stack."""
    res, st = [], [(root, 0)] if root else []
    while st:
        n, acc = st.pop()
        acc = acc * 10 + n.val
        if not n.left and not n.right:
            res.append(acc)
        if n.right:
            st.append((n.right, acc))
        if n.left:
            st.append((n.left, acc))
    return res


def good_nodes(root):
    """Top-down: count nodes with no strictly larger value above them."""

    def dfs(node, hi):
        if not node:
            return 0
        here = node.val >= hi
        hi = max(hi, node.val)
        return here + dfs(node.left, hi) + dfs(node.right, hi)

    return dfs(root, float("-inf"))


# ------------------------------------------------------------------------ tests


def _paths(root):
    """Brute force: every root-to-leaf path as a list of nodes, left to right."""
    out = []
    for leaf in nodes(set_parents(root)):
        if not leaf.left and not leaf.right:
            path = [leaf]
            while path[-1].parent:
                path.append(path[-1].parent)
            out.append(path[::-1])
    return out


def test_depth_known():
    assert max_depth(build([3, 9, 20, None, None, 15, 7])) == 3
    assert max_depth(None) == 0
    assert max_depth(build([1])) == 1
    assert max_depth(build([1, None, 2])) == 2


def test_depth_matches_brute_force():
    rng = random.Random(10)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 30))
        expected = 1 + max(bfs_dist(to_graph(t), t).values()) if t else 0
        assert max_depth(t) == max_depth_iterative(t) == expected


def test_subtree_sums_match_brute_force():
    rng = random.Random(11)
    for _ in range(200):
        t = random_tree(rng, rng.randint(1, 25))
        sums = subtree_sums(t)
        for n in nodes(t):
            assert sums[n] == sum(x.val for x in nodes(n))


def test_numbers_known():
    #     4
    #    / \
    #   9   0
    #  / \
    # 5   1
    t = build([4, 9, 0, 5, 1])
    assert root_to_leaf_numbers(t) == [495, 491, 40]
    assert sum(root_to_leaf_numbers(t)) == 1026
    assert root_to_leaf_numbers(None) == []


def test_one_child_node_is_not_a_leaf():
    # 1 -> 2 (left only). The only path is 12; stopping at the missing right
    # child of 1 would wrongly add 1.
    assert root_to_leaf_numbers(build([1, 2])) == [12]


def test_numbers_match_brute_force():
    rng = random.Random(12)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 20), lo=0, hi=9)
        expected = [int("".join(str(x.val) for x in p)) for p in _paths(t)]
        assert root_to_leaf_numbers(t) == root_to_leaf_numbers_iterative(t) == expected


def test_good_nodes():
    assert good_nodes(build([3, 1, 4, 3, None, 1, 5])) == 4
    assert good_nodes(build([3, 3, None, 4, 2])) == 3
    assert good_nodes(None) == 0
    rng = random.Random(13)
    for _ in range(200):
        t = random_tree(rng, rng.randint(1, 20))
        seen = set()
        for p in _paths(t):
            for i, x in enumerate(p):
                if all(y.val <= x.val for y in p[:i]):
                    seen.add(x)
        assert good_nodes(t) == len(seen)


def test_skewed_both_ways():
    for side in ("left", "right"):
        t = skewed(5, side)
        assert max_depth(t) == max_depth_iterative(t) == 5
        assert root_to_leaf_numbers(t) == root_to_leaf_numbers_iterative(t) == [12345]
        assert good_nodes(t) == 5


def test_iterative_survives_deep_tree():
    t = skewed(10_000, "left")
    assert max_depth_iterative(t) == 10_000
    assert subtree_sums(t)[t] == 10_000 * 10_001 // 2
    try:
        max_depth(t)
    except RecursionError:
        pass
    else:
        raise AssertionError("expected max_depth to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
