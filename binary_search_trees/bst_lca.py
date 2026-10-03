"""BST lowest common ancestor — walk down until p and q split.

Signs: "LCA of two nodes in a BST", distance between two BST values, the
       generic LCA problem but the tree is ordered.
Approach: from the root, if both values are smaller go left, if both are
          larger go right; otherwise this node separates them (or is one of
          them) and is the LCA. Ordering replaces the generic O(n) search in
          binary_trees/lca.py. Distance = depth(p) + depth(q) - 2 *
          depth(lca), each depth an O(h) BST search.
Complexity: O(h) time, O(1) space.
Gotchas: assumes both values are in the tree; if not, it still returns a
         split point. Check membership first when the problem allows missing
         values. Compare by value; nodes are only located by value here.

Run the tests at the bottom with:  python3 binary_search_trees/bst_lca.py
"""

import random

from bst import build, inorder, random_bst


# ---------------------------------------------------------------- implementation


def lca(root, p, q):
    """Node that is the LCA of values p and q."""
    lo, hi = min(p, q), max(p, q)
    while root:
        if hi < root.val:
            root = root.left
        elif lo > root.val:
            root = root.right
        else:
            return root
    return None


def depth(root, v):
    d = 0
    while root.val != v:
        root = root.left if v < root.val else root.right
        d += 1
    return d


def distance(root, p, q):
    a = lca(root, p, q)
    return depth(a, p) + depth(a, q)


# ------------------------------------------------------------------------ tests


def _path(root, v):
    out = []
    while root:
        out.append(root)
        if root.val == v:
            return out
        root = root.left if v < root.val else root.right
    raise ValueError


def _lca_brute(root, p, q):
    a, b = _path(root, p), _path(root, q)
    common = [x for x, y in zip(a, b) if x is y]
    return common[-1]


def test_known():
    #         6
    #       /   \
    #      2     8
    #     / \   / \
    #    0   4 7   9
    #       / \
    #      3   5
    t = build([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
    assert lca(t, 2, 8).val == 6 and lca(t, 2, 4).val == 2 and lca(t, 3, 5).val == 4
    assert distance(t, 3, 7) == 5 and distance(t, 4, 4) == 0


def test_matches_brute_force():
    rng = random.Random(71)
    for _ in range(300):
        t = random_bst(rng, rng.randint(1, 30))
        vals = inorder(t)
        for _ in range(10):
            p, q = rng.choice(vals), rng.choice(vals)
            want = _lca_brute(t, p, q)
            assert lca(t, p, q) is want
            assert distance(t, p, q) == len(_path(t, p)) + len(_path(t, q)) - 2 * len(_path(t, want.val))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
