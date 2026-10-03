"""Inorder is sorted — k-th smallest, BST iterator, inorder successor.

Signs: "k-th smallest", "next smallest", "iterator over a BST", "inorder
       successor/predecessor", "median of a BST", any rank question.
Approach: an inorder walk visits values in increasing order, so stop at the
          k-th visit. The iterator is that same walk paused: keep the stack of
          left-spine nodes; next() pops one, then pushes the left spine of its
          right child. Successor without a full walk: descend from the root;
          whenever target < node, node is a candidate and go left, else go
          right.
          Many k-th queries on a changing tree: store subtree sizes and
          descend by rank.
Complexity: k-th: O(h + k). Iterator: O(1) amortised next(), O(h) memory.
            Successor: O(h). Rank descent: O(h) per query.
Gotchas: k is 1-based. The successor of the maximum is None. Recursive
         inorder with a counter must stop early or it walks the whole tree;
         the iterative stack makes early exit natural.

Run the tests at the bottom with:  python3 binary_search_trees/kth_and_iterator.py
"""

import random

from bst import build, from_values, inorder, nodes, random_bst


# ---------------------------------------------------------------- implementation


def kth_smallest(root, k):
    st, cur = [], root
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.right
    raise IndexError("k out of range")


class BSTIterator:
    """Ascending iterator; reverse=True gives descending (mirror the walk)."""

    def __init__(self, root, reverse=False):
        self.st, self.rev = [], reverse
        self._push(root)

    def _push(self, n):
        while n:
            self.st.append(n)
            n = n.right if self.rev else n.left

    def has_next(self):
        return bool(self.st)

    def next(self):
        n = self.st.pop()
        self._push(n.left if self.rev else n.right)
        return n.val

    def peek(self):
        return self.st[-1].val


def inorder_successor(root, target):
    """Smallest value > target in the tree (target need not be present), or None."""
    best = None
    while root:
        if target < root.val:
            best, root = root.val, root.left
        else:
            root = root.right
    return best


def inorder_predecessor(root, target):
    """Largest value < target, or None."""
    best = None
    while root:
        if target > root.val:
            best, root = root.val, root.right
        else:
            root = root.left
    return best


def subtree_sizes(root):
    """{node: size of its subtree} — the augmentation for O(h) rank queries."""
    size = {None: 0}
    for n in reversed(nodes(root)):  # reversed preorder: children before parents
        size[n] = size[n.left] + size[n.right] + 1
    return size


def kth_by_size(root, k, size):
    while root:
        left = size[root.left]
        if k <= left:
            root = root.left
        elif k == left + 1:
            return root.val
        else:
            k -= left + 1
            root = root.right
    raise IndexError("k out of range")


# ------------------------------------------------------------------------ tests


def test_known():
    #       5
    #      / \
    #     3   6
    #    / \
    #   2   4
    #  /
    # 1
    t = build([5, 3, 6, 2, 4, None, None, 1])
    assert [kth_smallest(t, k) for k in range(1, 7)] == [1, 2, 3, 4, 5, 6]
    it = BSTIterator(t)
    assert [it.next() for _ in range(3)] == [1, 2, 3] and it.peek() == 4
    assert inorder_successor(t, 4) == 5 and inorder_successor(t, 6) is None
    assert inorder_predecessor(t, 1) is None and inorder_predecessor(t, 5) == 4


def test_out_of_range():
    for bad in (0, 4):
        try:
            kth_smallest(build([2, 1, 3]), bad)
        except IndexError:
            pass
        else:
            raise AssertionError


def test_matches_sorted_list():
    rng = random.Random(31)
    for _ in range(200):
        t = random_bst(rng, rng.randint(1, 30))
        vals = inorder(t)
        size = subtree_sizes(t)
        for k in range(1, len(vals) + 1):
            assert kth_smallest(t, k) == kth_by_size(t, k, size) == vals[k - 1]
        it, back = BSTIterator(t), BSTIterator(t, reverse=True)
        fwd, rev = [], []
        while it.has_next():
            fwd.append(it.next())
        while back.has_next():
            rev.append(back.next())
        assert fwd == vals and rev == vals[::-1]
        for q in range(vals[0] - 2, vals[-1] + 3):
            assert inorder_successor(t, q) == min((v for v in vals if v > q), default=None)
            assert inorder_predecessor(t, q) == max((v for v in vals if v < q), default=None)


def test_iterator_memory_is_height_not_n():
    t = from_values([8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15])  # perfect, h = 3
    it, peak = BSTIterator(t), 0
    while it.has_next():
        peak = max(peak, len(it.st))
        it.next()
    assert peak <= 4


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
