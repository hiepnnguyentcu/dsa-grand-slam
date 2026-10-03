"""BST node, LeetCode level-order encoding, and random-BST generators.

Signs: every other file in this folder imports from here — this is the shared
       plumbing, not a technique.
Approach: `build` / `to_list` speak LeetCode's level-order encoding, same as
          binary_trees/tree.py (copied so this folder stands alone).
          `random_bst` inserts distinct values in random order, which gives
          the mix of bushy and stringy shapes real BST inputs have.
          `inorder` and `is_bst_brute` are the reference answers most tests
          compare against.
Complexity: O(n) for build / to_list / nodes / inorder; random_bst is
            O(n * h).
Gotchas: trailing Nones are dropped by to_list. Everything here is
         iterative, so deep skewed trees are safe to build and inspect.
         Values are distinct unless a test says otherwise — duplicates make
         "the" BST ambiguous.

Run the tests at the bottom with:  python3 binary_search_trees/bst.py
"""

import random
from collections import deque


# ---------------------------------------------------------------- implementation


class TreeNode:
    __slots__ = ("val", "left", "right")

    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

    def __repr__(self):
        return f"TreeNode({self.val!r})"


def build(values):
    """Tree from a level-order list with None for missing nodes."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    q, i = deque([root]), 1
    while q and i < len(values):
        node = q.popleft()
        for side in ("left", "right"):
            if i < len(values) and values[i] is not None:
                child = TreeNode(values[i])
                setattr(node, side, child)
                q.append(child)
            i += 1
    return root


def to_list(root):
    """Level-order list with None for missing children, trailing Nones dropped."""
    out, q = [], deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        q.append(node.left)
        q.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def nodes(root):
    """Every node, in preorder, without recursion."""
    out, st = [], [root] if root else []
    while st:
        n = st.pop()
        out.append(n)
        if n.right:
            st.append(n.right)
        if n.left:
            st.append(n.left)
    return out


def inorder(root):
    """Values in inorder, iteratively. For a valid BST this is sorted."""
    out, st, cur = [], [], root
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        out.append(cur.val)
        cur = cur.right
    return out


def bst_insert(root, val):
    """Plain iterative insert (no rebalancing). Duplicates go right."""
    node = TreeNode(val)
    if root is None:
        return node
    cur = root
    while True:
        side = "left" if val < cur.val else "right"
        nxt = getattr(cur, side)
        if nxt is None:
            setattr(cur, side, node)
            return root
        cur = nxt


def from_values(values):
    """BST made by inserting values in the given order."""
    root = None
    for v in values:
        root = bst_insert(root, v)
    return root


def random_bst(rng, n, lo=0, hi=None):
    """A BST of n distinct values drawn from [lo, hi], inserted in random order."""
    hi = lo + 3 * n if hi is None else hi
    vals = rng.sample(range(lo, hi + 1), n)
    return from_values(vals)


def is_bst_brute(root):
    """Every node greater than all of its left subtree, smaller than all of its right.

    O(n^2) on purpose: it checks the definition directly, so it can judge the
    clever O(n) validators.
    """
    for n in nodes(root):
        if any(x.val >= n.val for x in nodes(n.left)):
            return False
        if any(x.val <= n.val for x in nodes(n.right)):
            return False
    return True


def height(root):
    """Edges on the longest root-to-leaf path; -1 for an empty tree."""
    h, q = -1, deque([root] if root else [])
    while q:
        h += 1
        for _ in range(len(q)):
            n = q.popleft()
            q.extend(c for c in (n.left, n.right) if c)
    return h


# ------------------------------------------------------------------------ tests


def test_round_trip_known():
    for vals in ([], [1], [2, 1, 3], [5, 3, 6, 2, 4, None, 7], [1, None, 2]):
        assert to_list(build(vals)) == vals


def test_from_values_shape():
    #     5
    #    / \
    #   3   8
    #  /   /
    # 1   7
    assert to_list(from_values([5, 3, 8, 1, 7])) == [5, 3, 8, 1, None, 7]


def test_random_bst_is_bst_with_sorted_inorder():
    rng = random.Random(1)
    for _ in range(200):
        n = rng.randint(0, 30)
        t = random_bst(rng, n)
        vals = inorder(t)
        assert len(vals) == n and vals == sorted(set(vals))
        assert is_bst_brute(t)


def test_is_bst_brute_catches_deep_violation():
    #     5
    #    / \
    #   3   8
    #        \
    #         4   <- right of 5 but smaller: only a whole-subtree check sees it
    t = build([5, 3, 8, None, None, None, 4])
    assert not is_bst_brute(t)
    assert is_bst_brute(build([5, 3, 8, None, None, None, 9]))


def test_random_shapes_vary():
    rng = random.Random(2)
    shapes = {tuple(v is None for v in to_list(random_bst(rng, 7))) for _ in range(300)}
    assert len(shapes) > 50


def test_height_and_deep_tree():
    assert height(None) == -1 and height(build([1])) == 0
    t = from_values(range(20_000))  # sorted input -> right-leaning path
    assert height(t) == 19_999
    assert inorder(t) == list(range(20_000))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
