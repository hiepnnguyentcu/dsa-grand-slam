"""Build a BST — from a sorted array/list (balanced) or from a preorder (bounds).

Signs: "convert sorted array/list to a height-balanced BST", "construct BST
       from preorder", "verify preorder sequence of a BST", serialize a BST
       compactly (preorder alone is enough).
Approach: sorted -> balanced: the middle element is the root, recurse on each
          half. A sorted linked list does the same by building in inorder:
          recurse on the left size first, consume the list head as the root,
          then the right — O(n) without random access.
          Preorder -> BST: consume values left to right; a value belongs to
          the current subtree only if it lies inside its (lo, hi) bounds,
          same bounds as validation. Each value is read once.
Complexity: O(n) time for all three; O(log n) recursion for the balanced
            builds, O(h) for preorder.
Gotchas: for an even count either middle works; tests should check balance
         and inorder, not one exact shape. Slicing arrays costs O(n log n) —
         pass indices. Preorder alone fixes a BST because inorder is just
         sorted(preorder); for a general binary tree it does not.

Run the tests at the bottom with:  python3 binary_search_trees/construct_bst.py
"""

import random

from bst import TreeNode, from_values, height, inorder, is_bst_brute, nodes, random_bst, to_list


# ---------------------------------------------------------------- implementation


def sorted_array_to_bst(a):
    def go(lo, hi):  # a[lo..hi]
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        return TreeNode(a[mid], go(lo, mid - 1), go(mid + 1, hi))

    return go(0, len(a) - 1)


class ListNode:
    __slots__ = ("val", "next")

    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt


def sorted_list_to_bst(head):
    """Inorder simulation: build the left subtree, take the head, build the right."""
    n, p = 0, head
    while p:
        n, p = n + 1, p.next
    cur = head

    def go(size):
        nonlocal cur
        if size == 0:
            return None
        left = go(size // 2)
        root = TreeNode(cur.val, left)
        cur = cur.next
        root.right = go(size - size // 2 - 1)
        return root

    return go(n)


def bst_from_preorder(pre):
    i = 0

    def go(lo, hi):
        nonlocal i
        if i == len(pre) or not lo < pre[i] < hi:
            return None
        node = TreeNode(pre[i])
        i += 1
        node.left = go(lo, node.val)
        node.right = go(node.val, hi)
        return node

    return go(float("-inf"), float("inf"))


def is_bst_preorder(pre):
    """Can this sequence be a BST's preorder? Monotonic stack, O(n), no tree built.

    Popping smaller values means we turned right past them; they become a
    lower bound every later value must exceed.
    """
    lo, st = float("-inf"), []
    for v in pre:
        if v < lo:
            return False
        while st and st[-1] < v:
            lo = st.pop()
        st.append(v)
    return True


# ------------------------------------------------------------------------ tests


def _preorder(root):
    return [n.val for n in nodes(root)]


def _is_height_balanced(root):
    return all(abs(height(n.left) - height(n.right)) <= 1 for n in nodes(root))


def _linked(vals):
    head = None
    for v in reversed(vals):
        head = ListNode(v, head)
    return head


def test_known():
    assert to_list(sorted_array_to_bst([-10, -3, 0, 5, 9])) == [0, -10, 5, None, -3, None, 9]
    assert to_list(bst_from_preorder([8, 5, 1, 7, 10, 12])) == [8, 5, 10, 1, 7, None, 12]
    assert sorted_array_to_bst([]) is None and sorted_list_to_bst(None) is None
    assert is_bst_preorder([5, 2, 1, 3, 6]) and not is_bst_preorder([5, 2, 6, 1, 3])


def test_balanced_builds():
    for n in range(0, 70):
        vals = list(range(0, 2 * n, 2))
        for t in (sorted_array_to_bst(vals), sorted_list_to_bst(_linked(vals))):
            assert inorder(t) == vals and is_bst_brute(t)
            assert _is_height_balanced(t)
            assert height(t) == (n.bit_length() - 1 if n else -1)  # minimal height


def test_preorder_round_trip():
    rng = random.Random(91)
    for _ in range(300):
        t = random_bst(rng, rng.randint(0, 30))
        pre = _preorder(t)
        assert to_list(bst_from_preorder(pre)) == to_list(t)
        assert is_bst_preorder(pre)


def test_preorder_check_matches_brute_force():
    # brute force: a sequence is a BST preorder iff inserting it in order
    # gives a tree whose preorder is the same sequence
    rng = random.Random(92)
    hits = 0
    for _ in range(2000):
        seq = rng.sample(range(12), rng.randint(0, 7))
        want = _preorder(from_values(seq)) == seq
        hits += want
        assert is_bst_preorder(seq) == want
    assert 100 < hits < 1900


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
