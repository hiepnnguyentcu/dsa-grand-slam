"""Search, insert, delete — the three BST primitives.

Signs: "search in a BST", "insert into a BST", "delete node in a BST", any
       dynamic sorted set built by hand.
Approach: compare with the current node and go left or right — one path, no
          backtracking. Insert hangs the new node off the first empty slot on
          that path. Delete has three cases: leaf (drop it), one child (splice
          the child up), two children (copy in the inorder successor — the
          leftmost node of the right subtree — then delete that successor,
          which has at most one child).
Complexity: O(h) time per operation, h = height: O(log n) balanced, O(n)
            skewed. O(1) extra space iterative, O(h) recursive.
Gotchas: delete must return the (possibly new) root — deleting the root
         changes it. Copying the successor's value is fine for interview
         problems; if outside code holds node references, relink nodes
         instead. Sorted inserts build a linked list (h = n), so recursive
         versions overflow on adversarial input.

Run the tests at the bottom with:  python3 binary_search_trees/search_insert_delete.py
"""

import random

from bst import TreeNode, build, from_values, inorder, is_bst_brute, to_list


# ---------------------------------------------------------------- implementation


def search(root, target):
    """Node holding target, or None."""
    while root and root.val != target:
        root = root.left if target < root.val else root.right
    return root


def insert(root, val):
    """Insert val (assumed absent); returns the root."""
    node = TreeNode(val)
    if root is None:
        return node
    cur = root
    while True:
        if val < cur.val:
            if cur.left is None:
                cur.left = node
                return root
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = node
                return root
            cur = cur.right


def delete(root, key):
    """Remove key if present; returns the new root."""
    if root is None:
        return None
    if key < root.val:
        root.left = delete(root.left, key)
    elif key > root.val:
        root.right = delete(root.right, key)
    else:
        if root.left is None:          # 0 or 1 child: splice up the other side
            return root.right
        if root.right is None:
            return root.left
        succ = root.right               # 2 children: inorder successor
        while succ.left:
            succ = succ.left
        root.val = succ.val
        root.right = delete(root.right, succ.val)
    return root


def delete_iterative(root, key):
    """Same as delete, no recursion, and relinks nodes instead of copying values."""
    parent, cur = None, root
    while cur and cur.val != key:
        parent, cur = cur, (cur.left if key < cur.val else cur.right)
    if cur is None:
        return root
    if cur.left and cur.right:
        # detach the successor, then put it where cur was
        sp, succ = cur, cur.right
        while succ.left:
            sp, succ = succ, succ.left
        if sp is not cur:
            sp.left = succ.right
            succ.right = cur.right
        succ.left = cur.left
        repl = succ
    else:
        repl = cur.left or cur.right
    if parent is None:
        return repl
    if parent.left is cur:
        parent.left = repl
    else:
        parent.right = repl
    return root


# ------------------------------------------------------------------------ tests


def test_known():
    #       5
    #      / \
    #     3   6
    #    / \   \
    #   2   4   7
    t = build([5, 3, 6, 2, 4, None, 7])
    assert search(t, 4).val == 4 and search(t, 8) is None
    t = delete(t, 3)  # two children: successor 4 moves up
    assert to_list(t) == [5, 4, 6, 2, None, None, 7]
    t = delete(t, 5)  # root
    assert to_list(t) == [6, 4, 7, 2]
    t = insert(t, 5)
    assert to_list(t) == [6, 4, 7, 2, 5]


def test_delete_missing_and_last():
    t = build([2, 1, 3])
    assert to_list(delete(t, 9)) == [2, 1, 3]
    t = build([1])
    assert delete(t, 1) is None and delete_iterative(build([1]), 1) is None
    assert delete(None, 1) is None


def test_matches_sorted_set_on_random_ops():
    rng = random.Random(11)
    for trial in range(60):
        ref, a, b = set(), None, None
        for _ in range(120):
            v = rng.randint(0, 40)
            if rng.random() < 0.55:
                if v not in ref:
                    a, b = insert(a, v), insert(b, v)
                    ref.add(v)
            else:
                a, b = delete(a, v), delete_iterative(b, v)
                ref.discard(v)
            assert (search(a, v) is not None) == (v in ref)
        assert inorder(a) == inorder(b) == sorted(ref)
        assert is_bst_brute(a) and is_bst_brute(b)


def test_iterative_delete_keeps_node_identity():
    t = from_values([50, 30, 70, 60, 80, 65])
    sixty = search(t, 60)
    t = delete_iterative(t, 50)  # successor 60 is relinked, not copied
    assert t is sixty and inorder(t) == [30, 60, 65, 70, 80]


def test_deep_skewed_iterative():
    t = None
    for v in range(20_000):
        t = insert(t, v)
    assert search(t, 19_999).val == 19_999
    for v in range(0, 20_000, 2):
        t = delete_iterative(t, v)
    assert inorder(t) == list(range(1, 20_000, 2))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
