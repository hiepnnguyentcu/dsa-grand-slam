"""Two-sum in a BST — two pointers on the sorted order, without flattening it.

Signs: "two sum in a BST", "pair with given sum", "two sum across two BSTs",
       any sorted-array two-pointer problem whose array is a BST.
Approach: a forward inorder iterator (smallest first) and a backward one
          (largest first) act as the two pointers of sorted-array two-sum:
          sum too small -> advance forward, too big -> advance backward, stop
          when they meet. Two BSTs: forward over one, backward over the other,
          same loop.
Complexity: O(n) time, O(h) space (two stacks). Flattening to a list is also
            O(n) time but O(n) space; a hash set works on any tree, O(n) space.
Gotchas: stop when the pointers meet, or one node pairs with itself
         (target = 2 * val). With two trees there is no meeting condition —
         run until either iterator is exhausted.

Run the tests at the bottom with:  python3 binary_search_trees/two_sum_bst.py
"""

import random

from bst import build, inorder, random_bst


# ---------------------------------------------------------------- implementation


class _Walk:
    """Inorder iterator; forward=False walks largest to smallest."""

    def __init__(self, root, forward=True):
        self.st, self.fwd = [], forward
        self._push(root)

    def _push(self, n):
        while n:
            self.st.append(n)
            n = n.left if self.fwd else n.right

    def peek(self):
        return self.st[-1].val if self.st else None

    def advance(self):
        n = self.st.pop()
        self._push(n.right if self.fwd else n.left)


def find_target(root, k):
    """True if two different nodes sum to k."""
    lo, hi = _Walk(root, True), _Walk(root, False)
    while lo.st and hi.st and lo.st[-1] is not hi.st[-1]:
        s = lo.peek() + hi.peek()
        if s == k:
            return True
        if s < k:
            lo.advance()
        else:
            hi.advance()
    return False


def two_sum_bsts(a, b, k):
    """True if some x in a and y in b have x + y == k."""
    lo, hi = _Walk(a, True), _Walk(b, False)
    while lo.st and hi.st:
        s = lo.peek() + hi.peek()
        if s == k:
            return True
        if s < k:
            lo.advance()
        else:
            hi.advance()
    return False


# ------------------------------------------------------------------------ tests


def test_known():
    t = build([5, 3, 6, 2, 4, None, 7])
    assert find_target(t, 9) and not find_target(t, 28)
    assert not find_target(build([1]), 2)        # no self-pairing
    assert not find_target(build([2, 1, 3]), 6)  # 3 + 3 would need two 3s
    assert two_sum_bsts(build([2, 1, 4]), build([1, 0, 3]), 5)
    assert not two_sum_bsts(build([0, -10, 10]), build([5, 1, 7, 0, 2]), 18)
    assert not two_sum_bsts(None, build([1]), 1)


def test_matches_brute_force():
    rng = random.Random(41)
    for _ in range(300):
        a = random_bst(rng, rng.randint(0, 15), lo=-20, hi=20)
        b = random_bst(rng, rng.randint(0, 15), lo=-20, hi=20)
        va, vb = inorder(a), inorder(b)
        for k in range(-42, 43, 3):
            want = any(va[i] + va[j] == k for i in range(len(va)) for j in range(i + 1, len(va)))
            assert find_target(a, k) == want
            assert two_sum_bsts(a, b, k) == any(x + y == k for x in va for y in vb)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
