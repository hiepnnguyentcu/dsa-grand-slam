"""Iterative preorder, inorder and postorder — plus the recursive originals.

Signs: deep trees that would overflow recursion, iterator/generator design
       (BST iterator, "next smallest"), an interviewer saying "without
       recursion", O(1)-space traversal (Morris).
Approach: the explicit stack plays the call stack.
          Preorder: pop, visit, push right then left (so left pops first).
          Inorder: slide left pushing every node; pop, visit, step right.
          Postorder: run a mirrored preorder (root, right, left) and reverse
          it — or, when you need nodes *as* they finish, keep one stack and
          remember the last node emitted to tell "back from the left" from
          "back from the right".
          Morris inorder threads each predecessor's empty right pointer back
          to its successor, so no stack is needed at all.
Complexity: O(n) time; O(h) space (O(1) extra for Morris).
Gotchas: the recursive forms hit CPython's ~1000-frame limit on skewed trees.
         The reverse trick builds the whole answer before emitting anything,
         so it cannot back a lazy postorder iterator. Morris mutates the tree
         while it runs — it restores every thread, but not if you break out
         of the loop early, and not safely under concurrent readers.

Run the tests at the bottom with:  python3 binary_trees/iterative_traversals.py
"""

import random

from tree import build, random_tree, skewed, to_list


# ---------------------------------------------------------------- implementation


def preorder_recursive(root):
    if not root:
        return []
    return [root.val] + preorder_recursive(root.left) + preorder_recursive(root.right)


def inorder_recursive(root):
    if not root:
        return []
    return inorder_recursive(root.left) + [root.val] + inorder_recursive(root.right)


def postorder_recursive(root):
    if not root:
        return []
    return postorder_recursive(root.left) + postorder_recursive(root.right) + [root.val]


def preorder(root):
    res, st = [], [root] if root else []
    while st:
        n = st.pop()
        res.append(n.val)
        if n.right:
            st.append(n.right)
        if n.left:
            st.append(n.left)
    return res


def inorder(root):
    res, st, cur = [], [], root
    while cur or st:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        res.append(cur.val)
        cur = cur.right
    return res


def postorder(root):
    """Reverse of a (root, right, left) preorder — which is exactly postorder."""
    res, st = [], [root] if root else []
    while st:
        n = st.pop()
        res.append(n.val)
        if n.left:
            st.append(n.left)
        if n.right:
            st.append(n.right)
    return res[::-1]


def postorder_one_stack(root):
    """True postorder: each node is emitted the moment it finishes.

    A node on top of the stack is ready only once its right subtree is done.
    That is the case when it has no right child, or when the node we emitted
    last *is* that right child — `prev` tells the two visits apart.
    """
    res, st, cur, prev = [], [], root, None
    while cur or st:
        while cur:
            st.append(cur)
            cur = cur.left
        top = st[-1]
        if top.right and top.right is not prev:
            cur = top.right  # first time back here: go do the right side
        else:
            res.append(top.val)
            prev = st.pop()
    return res


def morris_inorder(root):
    """Inorder in O(1) extra space by temporarily threading the tree."""
    res, cur = [], root
    while cur:
        if not cur.left:
            res.append(cur.val)
            cur = cur.right
            continue
        pred = cur.left
        while pred.right and pred.right is not cur:
            pred = pred.right
        if pred.right is None:
            pred.right = cur  # thread: come back here after the left subtree
            cur = cur.left
        else:
            pred.right = None  # second arrival: left subtree done, unthread
            res.append(cur.val)
            cur = cur.right
    return res


# ------------------------------------------------------------------------ tests

#         1
#        / \
#       2   3
#      / \   \
#     4   5   6
#        /
#       7
T = [1, 2, 3, 4, 5, None, 6, None, None, 7]


def test_known_orders():
    t = build(T)
    assert preorder(t) == [1, 2, 4, 5, 7, 3, 6]
    assert inorder(t) == [4, 2, 7, 5, 1, 3, 6]
    assert postorder(t) == [4, 7, 5, 2, 6, 3, 1]


def test_iterative_matches_recursive_on_random_trees():
    rng = random.Random(40)
    for _ in range(500):
        t = random_tree(rng, rng.randint(0, 40))
        assert preorder(t) == preorder_recursive(t)
        assert inorder(t) == inorder_recursive(t) == morris_inorder(t)
        assert postorder(t) == postorder_one_stack(t) == postorder_recursive(t)


def test_morris_leaves_tree_intact():
    rng = random.Random(41)
    for _ in range(200):
        t = random_tree(rng, rng.randint(0, 30))
        before = to_list(t)
        morris_inorder(t)
        assert to_list(t) == before


def test_empty_and_single():
    for f in (preorder, inorder, postorder, postorder_one_stack, morris_inorder):
        assert f(None) == []
        assert f(build([7])) == [7]


def test_skewed_both_ways():
    left, right = skewed(4, "left"), skewed(4, "right")
    assert preorder(left) == preorder(right) == [1, 2, 3, 4]
    assert inorder(left) == postorder(left) == postorder_one_stack(left) == [4, 3, 2, 1]
    assert inorder(right) == morris_inorder(right) == [1, 2, 3, 4]
    assert postorder(right) == postorder_one_stack(right) == [4, 3, 2, 1]


def test_iterative_survives_deep_trees():
    n = 20_000
    for side in ("left", "right"):
        t = skewed(n, side)
        assert len(preorder(t)) == len(inorder(t)) == len(postorder(t)) == n
        assert postorder_one_stack(t) == postorder(t)
        assert morris_inorder(t) == inorder(t)
    try:
        inorder_recursive(skewed(n, "left"))
    except RecursionError:
        pass
    else:
        raise AssertionError("expected inorder_recursive to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
