"""Sentinel return values — one return carries both "valid?" and a value.

Signs: a bottom-up check that needs a number from each child *and* a verdict:
       height-balanced (needs heights), valid full/perfect tree (needs sizes),
       "is every subtree X" questions.
Approach: return the value when the subtree is valid and an impossible value
          (-1 for a height) when it is not. A parent that sees the sentinel
          returns it straight away, so the first failure short-circuits the
          rest of the walk. A (ok, value) tuple is the explicit alternative
          when no value is impossible.
Complexity: O(n) time, O(h) space. The naive "is_balanced calls height at
            every node" version is O(n^2) on a skewed tree.
Gotchas: the sentinel must lie outside the value's real range — -1 works for
         heights (>= 0) but not for sums. Check the left result *before*
         recursing right, or you lose the short-circuit. Recursion depth is
         the tree height, so ~1000-deep trees overflow; the iterative form
         folds children into parents in reversed preorder.

Run the tests at the bottom with:  python3 binary_trees/sentinel_returns.py
"""

import random

from tree import build, nodes, random_tree, skewed


# ---------------------------------------------------------------- implementation


def is_balanced(root):
    """Every node's subtrees differ in height by at most 1."""

    def h(node):
        if not node:
            return 0
        l = h(node.left)
        if l < 0:
            return -1
        r = h(node.right)
        if r < 0 or abs(l - r) > 1:
            return -1
        return 1 + max(l, r)

    return h(root) >= 0


def is_balanced_tuple(root):
    """Same check, with an explicit (ok, height) pair instead of a sentinel."""

    def h(node):
        if not node:
            return True, 0
        lok, l = h(node.left)
        if not lok:
            return False, 0
        rok, r = h(node.right)
        return rok and abs(l - r) <= 1, 1 + max(l, r)

    return h(root)[0]


def is_balanced_iterative(root):
    """No recursion. Gives up the short-circuit, keeps O(n)."""
    h = {None: 0}
    for n in reversed(nodes(root)):
        l, r = h[n.left], h[n.right]
        if l < 0 or r < 0 or abs(l - r) > 1:
            h[n] = -1
        else:
            h[n] = 1 + max(l, r)
    return h[root] >= 0


# ------------------------------------------------------------------------ tests


def _height(n):
    return 0 if not n else 1 + max(_height(n.left), _height(n.right))


def _balanced_naive(root):
    """The O(n^2) definition, read straight off the page."""
    return all(abs(_height(n.left) - _height(n.right)) <= 1 for n in nodes(root))


def test_known():
    assert is_balanced(build([3, 9, 20, None, None, 15, 7]))
    assert not is_balanced(build([1, 2, 2, 3, 3, None, None, 4, 4]))
    assert is_balanced(None)
    assert is_balanced(build([1]))
    assert is_balanced(build([1, 2]))


def test_root_balanced_but_child_is_not():
    #        1
    #       / \
    #      2   3
    #     /     \
    #    4       5
    #   /         \
    #  6           7
    # Both root subtrees have height 3, but node 2 is off by two.
    t = build([1, 2, 3, 4, None, None, 5, 6, None, None, 7])
    assert _height(t.left) == _height(t.right)
    assert not is_balanced(t)
    assert not is_balanced_tuple(t)
    assert not is_balanced_iterative(t)


def test_matches_naive_on_random_trees():
    rng = random.Random(30)
    verdicts = set()
    for _ in range(500):
        t = random_tree(rng, rng.randint(0, 15))
        expected = _balanced_naive(t)
        verdicts.add(expected)
        assert is_balanced(t) == is_balanced_tuple(t) == is_balanced_iterative(t) == expected
    assert verdicts == {True, False}  # the sample actually exercised both answers


def test_skewed_both_ways():
    for side in ("left", "right"):
        assert is_balanced(skewed(2, side))
        assert not is_balanced(skewed(3, side))
        assert not is_balanced_iterative(skewed(3, side))


def test_short_circuit_survives_deep_left_spine():
    # The recursive form still has to *descend* the whole left spine before it
    # can see the imbalance, so depth — not the short-circuit — is what kills it.
    t = skewed(10_000, "left")
    assert not is_balanced_iterative(t)
    try:
        is_balanced(t)
    except RecursionError:
        pass
    else:
        raise AssertionError("expected is_balanced to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
