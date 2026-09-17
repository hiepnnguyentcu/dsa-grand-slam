"""Structural comparison — walk two trees (or one tree against itself) in lockstep.

Signs: same tree, symmetric/mirror tree, invert/flip a tree, "is t a subtree
       of s".
Approach: recurse on a *pair* of nodes. Both None: equal. Exactly one None:
          not equal. Otherwise compare values and recurse on corresponding
          children — (left, left) and (right, right) for sameness, (left,
          right) and (right, left) for mirroring. Subtree check: try `same`
          at every node of s, or serialise both trees with null markers and
          search for t's token list inside s's with KMP.
Complexity: O(n) for same / mirror / invert. Subtree: O(m * n) naive,
            O(m + n) with serialisation + KMP.
Gotchas: the serialisation needs explicit null markers (or [1, 2] and
         [1, None, 2] collide) and token boundaries (or value 2 matches
         inside 12) — matching on token lists rather than a joined string
         sidesteps the second. `invert` must swap using the *old* children;
         the tuple assignment does that. Recursive forms are depth-limited
         (~1000 frames); the pair-stack forms are not.

Run the tests at the bottom with:  python3 binary_trees/structural_comparison.py
"""

import random

from tree import build, nodes, random_tree, skewed, to_list


# ---------------------------------------------------------------- implementation


def same(a, b):
    if not a or not b:
        return a is b  # both None -> True; exactly one None -> False
    return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)


def mirror(a, b):
    if not a or not b:
        return a is b
    return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)


def is_symmetric(root):
    return mirror(root, root)


def same_iterative(a, b, mirrored=False):
    """same (or mirror, with mirrored=True) using a stack of node pairs."""
    st = [(a, b)]
    while st:
        x, y = st.pop()
        if not x or not y:
            if x is not y:
                return False
            continue
        if x.val != y.val:
            return False
        if mirrored:
            st += [(x.left, y.right), (x.right, y.left)]
        else:
            st += [(x.left, y.left), (x.right, y.right)]
    return True


def invert(root):
    if root:
        root.left, root.right = invert(root.right), invert(root.left)
    return root


def invert_iterative(root):
    st = [root] if root else []
    while st:
        n = st.pop()
        n.left, n.right = n.right, n.left
        st += [ch for ch in (n.left, n.right) if ch]
    return root


def is_subtree_naive(s, t):
    return any(same(n, t) for n in nodes(s)) if t else True


def _tokens(root):
    """Preorder values with None for every missing child."""
    out, st = [], [root]
    while st:
        n = st.pop()
        if n is None:
            out.append(None)
        else:
            out.append(n.val)
            st += [n.right, n.left]
    return out


def is_subtree(s, t):
    """KMP search for t's token list inside s's.

    A complete preorder-with-nulls run of t can only appear in s's sequence as
    the serialisation of an actual subtree of s: once a token run starts at a
    node, the null markers fix exactly where that node's subtree ends.
    """
    hay, pat = _tokens(s), _tokens(t)
    fail, k = [0] * len(pat), 0
    for i in range(1, len(pat)):
        while k and pat[i] != pat[k]:
            k = fail[k - 1]
        if pat[i] == pat[k]:
            k += 1
        fail[i] = k
    k = 0
    for x in hay:
        while k and x != pat[k]:
            k = fail[k - 1]
        if x == pat[k]:
            k += 1
        if k == len(pat):
            return True
    return False


# ------------------------------------------------------------------------ tests


def _copy(t):
    return build(to_list(t))


def test_same_known():
    assert same(build([1, 2, 3]), build([1, 2, 3]))
    assert not same(build([1, 2]), build([1, None, 2]))  # same values, different shape
    assert not same(build([1, 2, 1]), build([1, 1, 2]))
    assert same(None, None) and not same(build([1]), None)


def test_symmetric_known():
    assert is_symmetric(build([1, 2, 2, 3, 4, 4, 3]))
    assert not is_symmetric(build([1, 2, 2, None, 3, None, 3]))
    assert is_symmetric(None) and is_symmetric(build([1]))


def test_invert_known():
    assert to_list(invert(build([4, 2, 7, 1, 3, 6, 9]))) == [4, 7, 2, 9, 6, 3, 1]
    assert invert(None) is None


def test_random_properties():
    rng = random.Random(70)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 25), lo=0, hi=2)
        u = _copy(t)
        # same agrees with comparing encodings
        assert same(t, u) and same_iterative(t, u)
        other = random_tree(rng, rng.randint(0, 6), lo=0, hi=2)
        expected = to_list(t) == to_list(other)
        assert same(t, other) == same_iterative(t, other) == expected
        # a tree is always the mirror of its inversion, and symmetric exactly
        # when inverting it changes nothing
        inv = invert(_copy(t))
        assert mirror(t, inv) and same_iterative(t, inv, mirrored=True)
        unchanged = to_list(inv) == to_list(t)
        assert is_symmetric(t) == same_iterative(t, t, mirrored=True) == unchanged
        # inverting twice restores; both inverts agree
        assert to_list(invert_iterative(_copy(t))) == to_list(inv)
        assert to_list(invert(inv)) == to_list(t)


def test_symmetric_trees_are_found():
    # random trees are almost never symmetric, so build some on purpose
    rng = random.Random(71)
    for _ in range(100):
        half = random_tree(rng, rng.randint(0, 10), lo=0, hi=1)
        root = build([9])
        root.left, root.right = half, invert(_copy(half))
        assert is_symmetric(root) and same_iterative(root, root, mirrored=True)
        if half and not is_symmetric(half):
            root.right = _copy(half)
            assert not is_symmetric(root)


def test_subtree_known():
    s = build([3, 4, 5, 1, 2])
    assert is_subtree(s, build([4, 1, 2]))
    assert not is_subtree(build([3, 4, 5, 1, 2, None, None, None, None, 0]), build([4, 1, 2]))
    assert is_subtree(s, None) and not is_subtree(None, build([1]))


def test_subtree_token_boundaries():
    # "12" must not match "2" and a left child must not match a right child
    assert not is_subtree(build([12]), build([2]))
    assert not is_subtree(build([1, 2]), build([1, None, 2]))


def test_subtree_matches_naive():
    rng = random.Random(72)
    hits = 0
    for _ in range(500):
        s = random_tree(rng, rng.randint(0, 20), lo=0, hi=1)
        t = random_tree(rng, rng.randint(0, 4), lo=0, hi=1)
        expected = any(to_list(n) == to_list(t) for n in nodes(s)) if t else True
        hits += expected
        assert is_subtree(s, t) == is_subtree_naive(s, t) == expected
    assert 50 < hits < 450


def test_skewed_both_ways():
    left, right = skewed(4, "left"), skewed(4, "right")
    assert not same(left, right) and mirror(left, right)
    assert to_list(invert(_copy(left))) == to_list(right)
    assert is_subtree(left, skewed(2, "left", start=3))
    assert not is_subtree(left, skewed(2, "right", start=3))


def test_iterative_survives_deep_trees():
    n = 10_000
    a, b = skewed(n, "left"), skewed(n, "right")
    assert same_iterative(a, _copy(a))
    assert same_iterative(a, b, mirrored=True)
    assert to_list(invert_iterative(a))[-1] == n
    assert is_subtree(b, skewed(10, "right", start=n - 9))
    try:
        same(b, _copy(b))
    except RecursionError:
        pass
    else:
        raise AssertionError("expected same to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
