"""Balance a BST, count and generate all BST shapes (Catalan numbers).

Signs: "balance a binary search tree", "unique BSTs" (count), "unique BSTs II"
       (list them all), "why is my BST O(n)", self-balancing trees (AVL,
       red-black) in design questions.
Approach: balance: inorder to a sorted list, then rebuild from the middle —
          O(n), simplest correct answer. Count: pick root i of 1..n; left has
          i-1 keys, right has n-i, and shapes multiply:
          C(n) = sum C(i-1) * C(n-i), C(0) = 1 (Catalan). Generate: same
          split, returning every (left, right) pair; subtrees may be shared.
          AVL / red-black keep h = O(log n) with rotations after each
          insert/delete; in Python, reach for `sortedcontainers` or bisect
          on a list instead of writing one in an interview.
Complexity: balance O(n). Count O(n^2) DP (or closed form C(2n, n) / (n+1)).
            Generate O(C(n) * n) — C(n) grows like 4^n, so n <= ~10.
Gotchas: generated trees share subtrees — copy before mutating one. Count
         depends only on n, not on the values. A rotation must preserve
         inorder; that is the whole check.

Run the tests at the bottom with:  python3 binary_search_trees/balance_and_count.py
"""

import random
from math import comb

from bst import TreeNode, from_values, height, inorder, is_bst_brute, nodes, to_list


# ---------------------------------------------------------------- implementation


def balance_bst(root):
    vals = inorder(root)

    def go(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        return TreeNode(vals[mid], go(lo, mid - 1), go(mid + 1, hi))

    return go(0, len(vals) - 1)


def num_trees(n):
    c = [1] + [0] * n
    for k in range(1, n + 1):
        c[k] = sum(c[i - 1] * c[k - i] for i in range(1, k + 1))
    return c[n]


def generate_trees(n):
    """Every BST on keys 1..n (as roots; subtrees are shared between trees)."""
    memo = {}

    def go(lo, hi):
        if lo > hi:
            return [None]
        if (lo, hi) not in memo:
            memo[lo, hi] = [TreeNode(r, l, rt)
                            for r in range(lo, hi + 1)
                            for l in go(lo, r - 1)
                            for rt in go(r + 1, hi)]
        return memo[lo, hi]

    return go(1, n) if n else []


def rotate_right(y):
    """    y         x
          / \\       / \\
         x   C  -> A   y
        / \\           / \\
       A   B         B   C      inorder A x B y C is unchanged."""
    x = y.left
    y.left, x.right = x.right, y
    return x


def rotate_left(x):
    y = x.right
    x.right, y.left = y.left, x
    return y


# ------------------------------------------------------------------------ tests


def test_known():
    assert [num_trees(n) for n in range(8)] == [1, 1, 2, 5, 14, 42, 132, 429]
    assert sorted(to_list(t) for t in generate_trees(3)) == sorted([
        [1, None, 2, None, 3], [1, None, 3, 2], [2, 1, 3], [3, 1, None, None, 2], [3, 2, None, 1]])
    assert to_list(balance_bst(from_values([1, 2, 3, 4]))) == [2, 1, 3, None, None, None, 4]


def test_count_matches_closed_form_and_generation():
    for n in range(0, 20):
        assert num_trees(n) == comb(2 * n, n) // (n + 1)
    for n in range(1, 9):
        trees = generate_trees(n)
        assert len(trees) == num_trees(n)
        assert len({tuple(to_list(t)) for t in trees}) == len(trees)  # all distinct
        assert all(inorder(t) == list(range(1, n + 1)) for t in trees)


def test_balance_random():
    rng = random.Random(111)
    for _ in range(200):
        n = rng.randint(0, 60)
        vals = rng.sample(range(500), n)
        if rng.random() < 0.3:
            vals.sort()  # worst case: a path
        t = balance_bst(from_values(vals))
        assert inorder(t) == sorted(vals)
        assert height(t) == (n.bit_length() - 1 if n else -1)


def test_rotations_preserve_inorder():
    rng = random.Random(112)
    for _ in range(300):
        t = from_values(rng.sample(range(100), rng.randint(2, 20)))
        want = inorder(t)
        candidates = [n for n in nodes(t) if n.left]
        if candidates:
            y = rng.choice(candidates)
            # rotate the subtree at y, then hang it back under y's parent
            parent = next((p for p in nodes(t) if y in (p.left, p.right)), None)
            x = rotate_right(y)
            if parent is None:
                t = x
            elif parent.left is y:
                parent.left = x
            else:
                parent.right = x
            assert inorder(t) == want and is_bst_brute(t)
            assert rotate_left(x) is y  # and back again
            if parent is None:
                t = y
            elif parent.left is x:
                parent.left = y
            else:
                parent.right = y
            assert inorder(t) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
