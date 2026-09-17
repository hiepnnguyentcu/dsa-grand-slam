"""Count the nodes of a complete binary tree in O(log^2 n).

Signs: the tree is *complete* (every level full except possibly the last,
       which fills from the left) and O(n) counting is too slow.
Approach: walk the left spine and the right spine. Equal lengths mean the
          subtree is perfect: 2^h - 1 nodes, no need to look inside.
          Otherwise one of the two children is perfect, so recursing on both
          costs only one real descent per level.
          Alternative: at depth d the last level holds positions 0..2^d - 1;
          binary search for the last present one, testing each position by
          following its d bits from the root (0 = left, 1 = right).
Complexity: O(log^2 n) time — O(log n) levels, each spending O(log n) on
            spine walks. O(log n) stack.
Gotchas: only valid on complete trees — on other shapes it can shortcut
         past holes and miscount (see the test). Spine heights here count
         *nodes*, so a perfect tree is 2^h - 1; mixing node and edge heights
         is the usual off-by-one. Recursion depth is the height, about
         log2(n), so the frame limit is not a concern here.

Run the tests at the bottom with:  python3 binary_trees/count_complete.py
"""

from tree import build, complete_tree, nodes, skewed


# ---------------------------------------------------------------- implementation


def count_complete(root):
    if not root:
        return 0
    lh, rh, l, r = 0, 0, root, root
    while l:
        lh += 1
        l = l.left
    while r:
        rh += 1
        r = r.right
    if lh == rh:
        return (1 << lh) - 1
    return 1 + count_complete(root.left) + count_complete(root.right)


def count_complete_binary_search(root):
    """Binary search the last level for its rightmost present position."""
    if not root:
        return 0
    h, n = 0, root.left
    while n:
        h += 1
        n = n.left
    # levels 0..h-1 are full; the last level has positions 0..2^h - 1

    def exists(pos):
        node = root
        for bit in range(h - 1, -1, -1):
            node = node.right if pos >> bit & 1 else node.left
        return node is not None

    lo, hi = 0, (1 << h) - 1  # position 0 always exists (leftmost spine)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if exists(mid):
            lo = mid
        else:
            hi = mid - 1
    return (1 << h) - 1 + lo + 1


# ------------------------------------------------------------------------ tests


def test_known():
    assert count_complete(build([1, 2, 3, 4, 5, 6])) == 6
    assert count_complete(None) == count_complete_binary_search(None) == 0
    assert count_complete(build([1])) == count_complete_binary_search(build([1])) == 1


def test_every_size_up_to_600():
    for n in range(600):
        t = complete_tree(n)
        assert count_complete(t) == count_complete_binary_search(t) == len(nodes(t)) == n


def test_visits_only_log_squared_nodes():
    # count how many calls the recursion makes on a large, non-perfect tree
    n = (1 << 17) + 12_345
    t = complete_tree(n)
    calls = 0
    original = count_complete

    def counting(root):
        nonlocal calls
        calls += 1
        return original(root)

    globals()["count_complete"] = counting
    try:
        assert counting(t) == n
    finally:
        globals()["count_complete"] = original
    h = n.bit_length()
    assert calls <= 2 * h + 1  # far below n = 143,417


def test_two_node_complete_tree():
    # the only complete two-node tree has its child on the left; a lone
    # right child is not complete (see the next test)
    assert count_complete(skewed(2, "left")) == count_complete_binary_search(skewed(2, "left")) == 2


def test_wrong_on_non_complete_trees():
    #     1
    #    / \
    #   2   3        spines both have length 2, so it answers 3 — but there
    #    \           are 4 nodes: the shortcut never looked inside
    #     4
    t = build([1, 2, 3, None, 4])
    assert count_complete(t) == 3 != len(nodes(t))
    # a right-skewed chain is not complete either, yet the fallback happens
    # to count it correctly — no promise either way off complete trees
    assert count_complete(skewed(3, "right")) == 3


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
