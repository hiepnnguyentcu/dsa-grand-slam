"""Construct a tree from two traversals — preorder or postorder, plus inorder.

Signs: "build the tree from its preorder and inorder", or postorder and
       inorder; recovering a tree from two printed orders.
Approach: preorder's first value (postorder's last) is the root. Its position
          in inorder splits the remaining values into left and right
          subtrees. Look positions up in a value -> index map and consume
          preorder with a moving pointer instead of slicing lists.
          The iterative form keeps a stack of nodes still waiting for a right
          child: while the stack top equals the next inorder value, that
          node's left side is finished, so pop it — the last one popped is
          where the next preorder value hangs as a right child.
Complexity: O(n) time and space (slicing makes it O(n^2)).
Gotchas: values must be unique — with duplicates the inorder split is
         ambiguous (see the test). For postorder, consume from the end and
         build the *right* subtree first. Preorder + postorder alone do not
         determine a tree unless it is full. Recursion depth equals the tree
         height (~1000-frame limit); use the stack version for deep trees.

Run the tests at the bottom with:  python3 binary_trees/construct_from_traversals.py
"""

import random

from tree import TreeNode, build, random_tree, skewed, to_list
from iterative_traversals import inorder, postorder, preorder


# ---------------------------------------------------------------- implementation


def build_pre_in(pre, ino):
    idx = {v: i for i, v in enumerate(ino)}
    it = iter(pre)

    def build(lo, hi):
        if lo > hi:
            return None
        v = next(it)
        node = TreeNode(v)
        node.left = build(lo, idx[v] - 1)
        node.right = build(idx[v] + 1, hi)
        return node

    return build(0, len(ino) - 1)


def build_post_in(post, ino):
    """Mirror image of build_pre_in: read postorder backwards, right before left."""
    idx = {v: i for i, v in enumerate(ino)}
    it = reversed(post)

    def build(lo, hi):
        if lo > hi:
            return None
        v = next(it)
        node = TreeNode(v)
        node.right = build(idx[v] + 1, hi)  # reversed postorder is root, right, left
        node.left = build(lo, idx[v] - 1)
        return node

    return build(0, len(ino) - 1)


def build_pre_in_iterative(pre, ino):
    if not pre:
        return None
    root = TreeNode(pre[0])
    st, j = [root], 0
    for v in pre[1:]:
        node, parent = TreeNode(v), None
        while st and st[-1].val == ino[j]:
            parent = st.pop()
            j += 1
        if parent:
            parent.right = node
        else:
            st[-1].left = node
        st.append(node)
    return root


# ------------------------------------------------------------------------ tests


def test_known():
    pre, ino, post = [3, 9, 20, 15, 7], [9, 3, 15, 20, 7], [9, 15, 7, 20, 3]
    want = [3, 9, 20, None, None, 15, 7]
    assert to_list(build_pre_in(pre, ino)) == want
    assert to_list(build_post_in(post, ino)) == want
    assert to_list(build_pre_in_iterative(pre, ino)) == want


def test_round_trip_random_unique_values():
    rng = random.Random(100)
    for _ in range(400):
        n = rng.randint(0, 40)
        t = random_tree(rng, n, values=rng.sample(range(1000), n))
        pre, ino, post = preorder(t), inorder(t), postorder(t)
        want = to_list(t)
        assert to_list(build_pre_in(pre, ino)) == want
        assert to_list(build_post_in(post, ino)) == want
        assert to_list(build_pre_in_iterative(pre, ino)) == want


def test_empty_and_single():
    assert build_pre_in([], []) is None
    assert build_post_in([], []) is None
    assert build_pre_in_iterative([], []) is None
    assert to_list(build_pre_in([1], [1])) == [1]


def test_skewed_both_ways():
    for side in ("left", "right"):
        t = skewed(5, side)
        want = to_list(t)
        assert to_list(build_pre_in(preorder(t), inorder(t))) == want
        assert to_list(build_post_in(postorder(t), inorder(t))) == want
        assert to_list(build_pre_in_iterative(preorder(t), inorder(t))) == want


def test_duplicates_are_ambiguous():
    # 1 with a left child 1, and 1 with a right child 1, print identically
    a, b = build([1, 1]), build([1, None, 1])
    assert preorder(a) == preorder(b) and inorder(a) == inorder(b)
    assert to_list(a) != to_list(b)  # so no builder can recover both


def test_pre_and_post_alone_are_ambiguous():
    a, b = build([1, 2]), build([1, None, 2])
    assert preorder(a) == preorder(b) and postorder(a) == postorder(b)


def test_iterative_survives_deep_tree():
    for side in ("left", "right"):
        t = skewed(10_000, side)
        pre, ino = preorder(t), inorder(t)
        assert to_list(build_pre_in_iterative(pre, ino)) == to_list(t)
    try:
        build_pre_in(pre, ino)
    except RecursionError:
        pass
    else:
        raise AssertionError("expected build_pre_in to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
