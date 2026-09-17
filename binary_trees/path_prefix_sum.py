"""Path-prefix hashmap on trees — subarray-sum-equals-k, along root paths.

Signs: count downward paths (any start, any end, parent-to-child direction)
       whose values sum to k; the path need not touch the root or a leaf.
Approach: the array trick — count earlier prefixes equal to prefix - k — but
          "earlier" now means "on the path from the root to this node". Add
          the node's prefix to the counter on the way in and remove it on the
          way out, so the counter always describes exactly the current root
          path and siblings never see each other's prefixes.
Complexity: O(n) time, O(h) space for the counter and the stack.
Gotchas: seed the counter with {0: 1} so paths starting at the root count.
         Look up prefix - k *before* adding the current prefix, or k == 0
         counts every node as a path of zero nodes. Forgetting the decrement
         is the classic bug — it lets paths jump across branches. Negative
         values are fine (no sliding window). The recursive form hits the
         ~1000-frame limit; the iterative one uses enter/exit stack events.

Run the tests at the bottom with:  python3 binary_trees/path_prefix_sum.py
"""

import random
from collections import defaultdict

from tree import build, nodes, random_tree, set_parents, skewed


# ---------------------------------------------------------------- implementation


def path_sum_count(root, k):
    cnt = defaultdict(int)
    cnt[0] = 1

    def dfs(n, s):
        if not n:
            return 0
        s += n.val
        res = cnt[s - k]
        cnt[s] += 1
        res += dfs(n.left, s) + dfs(n.right, s)
        cnt[s] -= 1  # leaving this node: its prefix is no longer on the path
        return res

    return dfs(root, 0)


def path_sum_count_iterative(root, k):
    """Same count; the stack holds (node, prefix-before-node, entering?) events."""
    cnt, res = defaultdict(int), 0
    cnt[0] = 1
    st = [(root, 0, True)] if root else []
    while st:
        n, before, entering = st.pop()
        s = before + n.val
        if not entering:
            cnt[s] -= 1
            continue
        res += cnt[s - k]
        cnt[s] += 1
        st.append((n, before, False))  # runs after both subtrees are done
        for ch in (n.right, n.left):
            if ch:
                st.append((ch, s, True))
    return res


# ------------------------------------------------------------------------ tests


def _brute(root, k):
    """For every node, walk up through its ancestors summing as we go."""
    total = 0
    for n in nodes(set_parents(root)):
        s, x = 0, n
        while x:
            s += x.val
            total += s == k
            x = x.parent
    return total


def test_known():
    t = build([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1])
    assert path_sum_count(t, 8) == 3
    t = build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1])
    assert path_sum_count(t, 22) == 3


def test_paths_must_not_cross_branches():
    #   0
    #  / \
    # 1   2     k = 3: 1 and 2 are siblings, so 1 + 2 is not a downward path
    assert path_sum_count(build([0, 1, 2]), 3) == 0
    assert path_sum_count_iterative(build([0, 1, 2]), 3) == 0


def test_zero_target():
    # 0 alone, -1+1, and 0-(-1)-1 -> three paths; the empty path must not count
    t = build([0, -1, None, 1])
    assert path_sum_count(t, 0) == _brute(t, 0) == 3


def test_matches_brute_force():
    rng = random.Random(120)
    for _ in range(400):
        t = random_tree(rng, rng.randint(0, 30), lo=-3, hi=3)
        k = rng.randint(-4, 4)
        assert path_sum_count(t, k) == path_sum_count_iterative(t, k) == _brute(t, k)


def test_empty_single_skewed():
    assert path_sum_count(None, 0) == path_sum_count_iterative(None, 0) == 0
    assert path_sum_count(build([5]), 5) == 1
    for side in ("left", "right"):
        t = skewed(5, side)  # 1..5: sums of 5 are [5] and [2, 3]
        assert path_sum_count(t, 5) == path_sum_count_iterative(t, 5) == 2


def test_iterative_survives_deep_tree():
    t = skewed(10_000, "left")
    for n in nodes(t):
        n.val = 1
    assert path_sum_count_iterative(t, 3) == 10_000 - 2  # every window of three
    try:
        path_sum_count(t, 3)
    except RecursionError:
        pass
    else:
        raise AssertionError("expected path_sum_count to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
