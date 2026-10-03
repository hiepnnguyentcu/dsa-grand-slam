"""Floor, ceil, closest value — binary search down one root-to-leaf path.

Signs: "largest value <= x", "smallest value >= x", "closest value in a BST",
       "k values closest to target", nearest booking/timestamp in a tree.
Approach: walk from the root. Floor: if node.val <= x it is a candidate, go
          right for a bigger one; else go left. Ceil mirrors it. Closest:
          track the best |val - x| on the same path — the answer is always on
          the search path for x.
          k closest: two iterators from x's position, predecessor stack and
          successor stack, then merge k times like two-pointer.
Complexity: floor/ceil/closest O(h). k closest O(h + k).
Gotchas: floor/ceil return None when nothing qualifies; closest needs a
         non-empty tree. Pick a tie rule for closest (here: smaller value)
         and state it. An exact match ends the walk early.

Run the tests at the bottom with:  python3 binary_search_trees/floor_ceil.py
"""

import random

from bst import build, inorder, random_bst


# ---------------------------------------------------------------- implementation


def floor(root, x):
    best = None
    while root:
        if root.val == x:
            return x
        if root.val < x:
            best, root = root.val, root.right
        else:
            root = root.left
    return best


def ceil(root, x):
    best = None
    while root:
        if root.val == x:
            return x
        if root.val > x:
            best, root = root.val, root.left
        else:
            root = root.right
    return best


def closest_value(root, x):
    """Value nearest x; ties go to the smaller value."""
    best = root.val
    while root:
        if (abs(root.val - x), root.val) < (abs(best - x), best):
            best = root.val
        if root.val == x:
            break
        root = root.left if x < root.val else root.right
    return best


def k_closest(root, x, k):
    """k values nearest x in increasing order of distance (ties: smaller first)."""
    pred, succ = [], []  # pred: path nodes with val <= x; succ: val > x
    n = root
    while n:
        if n.val <= x:
            pred.append(n)
            n = n.right
        else:
            succ.append(n)
            n = n.left

    def next_pred():
        node = pred.pop()
        c = node.left
        while c:  # push the right spine of the left subtree
            pred.append(c)
            c = c.right
        return node.val

    def next_succ():
        node = succ.pop()
        c = node.right
        while c:
            succ.append(c)
            c = c.left
        return node.val

    out = []
    while len(out) < k and (pred or succ):
        if not succ or (pred and x - pred[-1].val <= succ[-1].val - x):
            out.append(next_pred())
        else:
            out.append(next_succ())
    return out


# ------------------------------------------------------------------------ tests


def test_known():
    #      8
    #     / \
    #    4   12
    #   / \    \
    #  2   6    14
    t = build([8, 4, 12, 2, 6, None, 14])
    assert floor(t, 7) == 6 and ceil(t, 7) == 8
    assert floor(t, 1) is None and ceil(t, 15) is None
    assert floor(t, 12) == ceil(t, 12) == 12
    assert closest_value(t, 10) == 8   # tie 8 vs 12 -> smaller
    assert closest_value(t, 13) == 12
    assert k_closest(t, 5, 3) == [4, 6, 2]


def test_matches_brute_force():
    rng = random.Random(61)
    for _ in range(300):
        t = random_bst(rng, rng.randint(1, 25), lo=-30, hi=30)
        vals = inorder(t)
        for x in range(-33, 34):
            assert floor(t, x) == max((v for v in vals if v <= x), default=None)
            assert ceil(t, x) == min((v for v in vals if v >= x), default=None)
            by_dist = sorted(vals, key=lambda v: (abs(v - x), v))
            assert closest_value(t, x) == by_dist[0]
            k = rng.randint(1, len(vals))
            assert k_closest(t, x, k) == by_dist[:k]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
