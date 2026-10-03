"""Recover a BST whose two nodes were swapped — find the inversions in inorder.

Signs: "two nodes swapped by mistake", "fix the BST without changing its
       structure", "sorted array with two elements swapped".
Approach: walk inorder keeping the previous node. A drop (prev > cur) marks an
          inversion. Adjacent swap: one drop, swap its two nodes. Distant
          swap: two drops; the bad nodes are the first drop's prev and the
          second drop's cur. Record first = prev at the first drop and
          second = cur at every drop, then swap their values.
          Morris traversal does the same walk in O(1) space by threading
          right pointers to the inorder successor and unthreading on return.
Complexity: O(n) time; O(h) space with a stack, O(1) with Morris.
Gotchas: overwrite `second` on every drop — the adjacent case has only one.
         Swap values, not nodes; the shape must stay. Morris must fully
         unthread or the tree is left corrupted, so never return mid-walk.

Run the tests at the bottom with:  python3 binary_search_trees/recover_bst.py
"""

import random

from bst import build, inorder, nodes, random_bst, to_list


# ---------------------------------------------------------------- implementation


def recover_tree(root):
    first = second = prev = None
    st, cur = [], root
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        if prev and prev.val > cur.val:
            if first is None:
                first = prev
            second = cur
        prev, cur = cur, cur.right
    first.val, second.val = second.val, first.val


def recover_tree_morris(root):
    first = second = prev = None
    cur = root
    while cur:
        if cur.left:
            pred = cur.left
            while pred.right and pred.right is not cur:
                pred = pred.right
            if pred.right is None:      # first visit: thread and go left
                pred.right = cur
                cur = cur.left
                continue
            pred.right = None           # second visit: unthread, then visit cur
        if prev and prev.val > cur.val:
            if first is None:
                first = prev
            second = cur
        prev, cur = cur, cur.right
    first.val, second.val = second.val, first.val


# ------------------------------------------------------------------------ tests


def test_known():
    t = build([1, 3, None, None, 2])     # 1 and 3 swapped (adjacent in inorder)
    recover_tree(t)
    assert to_list(t) == [3, 1, None, None, 2]
    t = build([3, 1, 4, None, None, 2])  # 2 and 3 swapped (distant)
    recover_tree_morris(t)
    assert to_list(t) == [2, 1, 4, None, None, 3]


def test_matches_original_on_random_swaps():
    rng = random.Random(51)
    for _ in range(400):
        n = rng.randint(2, 30)
        for fix in (recover_tree, recover_tree_morris):
            t = random_bst(rng, n)
            want = to_list(t)
            a, b = rng.sample(nodes(t), 2)
            a.val, b.val = b.val, a.val
            fix(t)
            assert to_list(t) == want  # same shape, values back in place


def test_morris_leaves_no_threads():
    rng = random.Random(52)
    t = random_bst(rng, 40)
    shape_before = [(id(n.left), id(n.right)) for n in nodes(t)]
    a, b = rng.sample(nodes(t), 2)
    a.val, b.val = b.val, a.val
    recover_tree_morris(t)
    assert [(id(n.left), id(n.right)) for n in nodes(t)] == shape_before
    assert inorder(t) == sorted(inorder(t))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
