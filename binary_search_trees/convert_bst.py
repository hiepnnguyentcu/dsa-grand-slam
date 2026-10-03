"""Reshape a BST in place — sorted doubly linked list, greater-sum tree.

Signs: "convert BST to sorted circular doubly linked list", "flatten BST to an
       increasing-order tree", "convert BST to greater sum tree" / "greater
       tree", running totals in sorted or reverse-sorted order.
Approach: all are an inorder walk with a `prev` pointer.
          DLL: link prev.right = cur and cur.left = prev as you visit; at the
          end join head and tail for the circular version.
          Increasing tree: same walk, but set cur.left = None and only the
          right links.
          Greater-sum: reverse inorder (right, node, left) visits values
          largest first; keep a running sum and overwrite each node with it.
Complexity: O(n) time, O(h) space (stack). O(1) extra with Morris.
Gotchas: the DLL reuses left/right as prev/next — the tree is gone after.
         Greater-sum includes the node itself ("greater than or equal");
         some variants want strictly greater — subtract the node's old
         value. Save cur.right before relinking if you change it mid-walk.

Run the tests at the bottom with:  python3 binary_search_trees/convert_bst.py
"""

import random

from bst import TreeNode, build, inorder, nodes, random_bst, to_list


# ---------------------------------------------------------------- implementation


def _inorder_nodes(root, reverse=False):
    st, cur = [], root
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur.right if reverse else cur.left
        cur = st.pop()
        yield cur
        cur = cur.left if reverse else cur.right


def to_circular_dll(root):
    """Head (smallest) of a circular list; left = prev, right = next."""
    head = prev = None
    for cur in _inorder_nodes(root):
        if prev:
            prev.right, cur.left = cur, prev
        else:
            head = cur
        prev = cur
    if head:
        head.left, prev.right = prev, head
    return head


def increasing_bst(root):
    """Right-only chain in sorted order; returns the new root."""
    dummy = prev = TreeNode(0)
    # safe to relink during the walk: cur.left is already explored, and
    # prev.right is only rewritten after the walk has read it
    for cur in _inorder_nodes(root):
        cur.left = None
        prev.right = cur
        prev = cur
    return dummy.right


def greater_sum_tree(root):
    """Each value becomes the sum of all values >= it."""
    running = 0
    for cur in _inorder_nodes(root, reverse=True):
        running += cur.val
        cur.val = running
    return root


# ------------------------------------------------------------------------ tests


def _walk_dll(head):
    fwd, n = [], head
    while True:
        fwd.append(n.val)
        n = n.right
        if n is head:
            break
    back, n = [], head.left
    while True:
        back.append(n.val)
        n = n.left
        if n is head.left:
            break
    return fwd, back


def test_known():
    head = to_circular_dll(build([4, 2, 5, 1, 3]))
    assert _walk_dll(head) == ([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert to_list(increasing_bst(build([5, 3, 6, 2, 4, None, 8]))) == \
        [2, None, 3, None, 4, None, 5, None, 6, None, 8]
    t = greater_sum_tree(build([4, 1, 6, 0, 2, 5, 7, None, None, None, 3, None, None, None, 8]))
    assert to_list(t) == [30, 36, 21, 36, 35, 26, 15, None, None, None, 33, None, None, None, 8]
    assert to_circular_dll(None) is None


def test_matches_sorted_list():
    rng = random.Random(101)
    for _ in range(300):
        n = rng.randint(1, 30)
        vals = inorder(t := random_bst(rng, n))
        assert _walk_dll(to_circular_dll(t)) == (vals, vals[::-1])

        chain = increasing_bst(random_bst(random.Random(n), n))
        got, c = [], chain
        while c:
            assert c.left is None
            got.append(c.val)
            c = c.right
        assert got == sorted(got) and len(got) == n

        t = random_bst(rng, n, lo=-20)
        before = {id(x): x.val for x in nodes(t)}
        allv = list(before.values())
        greater_sum_tree(t)
        for x in nodes(t):
            assert x.val == sum(v for v in allv if v >= before[id(x)])


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
