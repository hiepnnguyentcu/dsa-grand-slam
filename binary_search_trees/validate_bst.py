"""Validate a BST — pass down an open interval, or check inorder is increasing.

Signs: "is this a valid BST", "largest BST subtree", any check that a subtree
       respects an ancestor's value, not just its parent's.
Approach: bounds — every node must lie strictly inside (lo, hi); going left
          tightens hi to node.val, going right tightens lo. Inorder — a BST's
          inorder is strictly increasing, so keep the previous value and fail
          on the first non-increase.
          Largest BST subtree: postorder returning (is_bst, size, min, max);
          a node is a BST root if both children are and left.max < val <
          right.min.
Complexity: O(n) time, O(h) space.
Gotchas: comparing only with the parent is the classic bug — [5, 4, 6, None,
         None, 3, 7] passes it but 3 sits right of 5. Use None (or ±inf) for
         open bounds, not INT_MIN/INT_MAX: node values can equal them.
         Decide whether duplicates are allowed; here they are not (strict).

Run the tests at the bottom with:  python3 binary_search_trees/validate_bst.py
"""

import random

from bst import build, is_bst_brute, nodes, random_bst


# ---------------------------------------------------------------- implementation


def is_valid_bst(root):
    """Bounds check, iterative: each stack entry carries its open interval."""
    st = [(root, None, None)]
    while st:
        n, lo, hi = st.pop()
        if n is None:
            continue
        if (lo is not None and n.val <= lo) or (hi is not None and n.val >= hi):
            return False
        st.append((n.left, lo, n.val))
        st.append((n.right, n.val, hi))
    return True


def is_valid_bst_inorder(root):
    """Inorder must be strictly increasing; stops at the first violation."""
    st, cur, prev = [], root, None
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        if prev is not None and cur.val <= prev:
            return False
        prev = cur.val
        cur = cur.right
    return True


def largest_bst_subtree(root):
    """Node count of the largest subtree that is itself a BST."""
    best = 0

    def go(n):  # -> (is_bst, size, min, max)
        nonlocal best
        if n is None:
            return True, 0, float("inf"), float("-inf")
        lb, ls, lmin, lmax = go(n.left)
        rb, rs, rmin, rmax = go(n.right)
        if lb and rb and lmax < n.val < rmin:
            size = ls + rs + 1
            best = max(best, size)
            return True, size, min(lmin, n.val), max(rmax, n.val)
        return False, 0, 0, 0

    go(root)
    return best


# ------------------------------------------------------------------------ tests


def _parent_only_check(root):
    """The buggy check: each child vs its parent only."""
    for n in nodes(root):
        if n.left and n.left.val >= n.val or n.right and n.right.val <= n.val:
            return False
    return True


def test_known():
    assert is_valid_bst(build([2, 1, 3]))
    assert not is_valid_bst(build([5, 1, 4, None, None, 3, 6]))
    assert is_valid_bst(None) and is_valid_bst(build([1]))
    assert not is_valid_bst(build([1, 1]))  # duplicates rejected


def test_parent_only_check_is_wrong():
    #     5
    #    / \
    #   4   6
    #      / \
    #     3   7     3 < 6 is fine locally, but 3 sits right of 5
    t = build([5, 4, 6, None, None, 3, 7])
    assert _parent_only_check(t)
    assert not is_valid_bst(t) and not is_valid_bst_inorder(t)


def test_extreme_values():
    big = 2**31 - 1
    assert is_valid_bst(build([big])) and is_valid_bst(build([-big - 1, None, big]))


def _perturb(rng, t):
    """Change one node's value to a random one: sometimes still valid, often not."""
    ns = nodes(t)
    rng.choice(ns).val = rng.randint(-5, 3 * len(ns) + 5)
    return t


def test_matches_brute_force():
    rng = random.Random(21)
    seen = {True: 0, False: 0}
    for _ in range(400):
        t = random_bst(rng, rng.randint(1, 15))
        if rng.random() < 0.7:
            _perturb(rng, t)
        want = is_bst_brute(t)
        seen[want] += 1
        assert is_valid_bst(t) == is_valid_bst_inorder(t) == want
    assert min(seen.values()) > 50  # both verdicts well covered


def _largest_brute(root):
    return max((len(nodes(n)) for n in nodes(root) if is_bst_brute(n)), default=0)


def test_largest_bst_subtree():
    assert largest_bst_subtree(build([10, 5, 15, 1, 8, None, 7])) == 3
    assert largest_bst_subtree(None) == 0
    rng = random.Random(22)
    for _ in range(300):
        t = random_bst(rng, rng.randint(1, 15))
        for _ in range(rng.randint(0, 3)):
            _perturb(rng, t)
        assert largest_bst_subtree(t) == _largest_brute(t)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
