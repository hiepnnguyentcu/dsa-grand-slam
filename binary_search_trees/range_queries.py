"""Range sum, range listing, trim — prune subtrees the range cannot reach.

Signs: "range sum of BST", "all values in [lo, hi]", "trim a BST to [lo, hi]",
       count nodes in a range.
Approach: at each node, the order tells you which sides can hold in-range
          values. val < lo: the left subtree is all smaller, skip it, go
          right. val > hi: skip the right. Otherwise count the node and visit
          both. Trim uses the same rule but returns the surviving subtree:
          an out-of-range node is replaced by its trimmed right (val < lo) or
          left (val > hi) child.
Complexity: O(h + m) for listing/sum, m = nodes in range. Trim O(n) worst
            case (it may rewrite many links), O(h) recursion.
Gotchas: the bounds are inclusive here — read the problem. In trim, a node
         below lo may still have in-range nodes in its right subtree, so
         recurse; don't just drop it. Trim reuses nodes, no copies.

Run the tests at the bottom with:  python3 binary_search_trees/range_queries.py
"""

import random

from bst import build, from_values, inorder, is_bst_brute, nodes, random_bst, to_list


# ---------------------------------------------------------------- implementation


def range_sum(root, lo, hi):
    total, st = 0, [root]
    while st:
        n = st.pop()
        if n is None:
            continue
        if n.val < lo:
            st.append(n.right)
        elif n.val > hi:
            st.append(n.left)
        else:
            total += n.val
            st += [n.left, n.right]
    return total


def range_values(root, lo, hi):
    """In-range values in sorted order: a pruned inorder walk."""
    out = []

    def go(n):
        if n is None:
            return
        if n.val > lo:
            go(n.left)
        if lo <= n.val <= hi:
            out.append(n.val)
        if n.val < hi:
            go(n.right)

    go(root)
    return out


def trim(root, lo, hi):
    if root is None:
        return None
    if root.val < lo:
        return trim(root.right, lo, hi)
    if root.val > hi:
        return trim(root.left, lo, hi)
    root.left = trim(root.left, lo, hi)
    root.right = trim(root.right, lo, hi)
    return root


# ------------------------------------------------------------------------ tests


def test_known():
    #       10
    #      /  \
    #     5    15
    #    / \     \
    #   3   7     18
    t = build([10, 5, 15, 3, 7, None, 18])
    assert range_sum(t, 7, 15) == 32
    assert range_values(t, 4, 16) == [5, 7, 10, 15]
    assert to_list(trim(build([3, 0, 4, None, 2, None, None, 1]), 1, 3)) == [3, 2, None, 1]


def test_matches_brute_force():
    rng = random.Random(81)
    for _ in range(300):
        n = rng.randint(0, 25)
        lo = rng.randint(-5, 80)
        hi = lo + rng.randint(-2, 40)  # sometimes empty (hi < lo)
        t = random_bst(rng, n)
        want = [v for v in inorder(t) if lo <= v <= hi]
        assert range_sum(t, lo, hi) == sum(want)
        assert range_values(t, lo, hi) == want
        ids = {id(x) for x in nodes(t)}
        t2 = trim(t, lo, hi)
        assert inorder(t2) == want and is_bst_brute(t2)
        assert all(id(x) in ids for x in nodes(t2))  # nodes reused, not copied


def test_pruning_visits_few_nodes():
    t = from_values(_balanced_order(0, 4094))  # perfect BST, 4095 nodes, h = 11
    visited = 0
    st = [t]
    while st:  # range_sum's loop, counting visits
        n = st.pop()
        if n is None:
            continue
        visited += 1
        if n.val < 100:
            st.append(n.right)
        elif n.val > 110:
            st.append(n.left)
        else:
            st += [n.left, n.right]
    assert range_sum(t, 100, 110) == sum(range(100, 111))
    assert visited < 60  # about 2h + 2m, not 4095


def _balanced_order(lo, hi):
    """Insertion order (midpoints first) that builds a perfect BST."""
    out, q = [], [(lo, hi)]
    while q:
        a, b = q.pop()
        if a <= b:
            m = (a + b) // 2
            out.append(m)
            q += [(a, m - 1), (m + 1, b)]
    return out


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
