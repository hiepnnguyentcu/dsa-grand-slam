"""Tree DP with state tuples — each node reports its best value per state.

Signs: pick nodes under parent/child rules — house robber on a tree (maximum
       weight independent set), minimum vertex cover, minimum cameras
       (dominating set), anything where a node's choice constrains its
       neighbours.
Approach: each node returns one value per state, e.g. (taken, not_taken). A
          parent combines its children's tuples according to the rule: if the
          parent is taken, children must be skipped; if skipped, each child
          picks its better state. Cameras use three states — not covered,
          covered without a camera, has a camera — and place a camera only
          when a child would otherwise be left uncovered.
Complexity: O(n * s^2) for s states per node; O(n) here.
Gotchas: the root has no parent to cover it, so its final state needs a
         fix-up (cameras: add one if the root came back uncovered). Evaluate
         the DP *before* reading a global it updates — `cams + (dfs(root) ==
         0)` reads cams first, a bug in the reference. None children need a
         neutral state (cameras: "covered", or leaves would force cameras on
         themselves). Recursion hits the ~1000-frame limit; the iterative
         forms fold children first in reversed preorder.

Run the tests at the bottom with:  python3 binary_trees/tree_dp.py
"""

import random
from itertools import combinations

from tree import build, nodes, random_tree, skewed, to_graph


# ---------------------------------------------------------------- implementation


def rob_tree(root):
    """Max total value of nodes with no two adjacent."""

    def dfs(n):
        if not n:
            return 0, 0  # (rob this node, skip this node)
        lr, ls = dfs(n.left)
        rr, rs = dfs(n.right)
        return n.val + ls + rs, max(lr, ls) + max(rr, rs)

    return max(dfs(root))


def rob_tree_iterative(root):
    best = {None: (0, 0)}
    for n in reversed(nodes(root)):
        (lr, ls), (rr, rs) = best[n.left], best[n.right]
        best[n] = (n.val + ls + rs, max(lr, ls) + max(rr, rs))
    return max(best[root])


def min_vertex_cover(root):
    """Fewest nodes such that every edge has at least one chosen end."""

    def dfs(n):
        if not n:
            return 0, 0  # (n chosen, n not chosen)
        lt, ls = dfs(n.left)
        rt, rs = dfs(n.right)
        # a skipped node forces every real child to be chosen
        skip = (lt if n.left else 0) + (rt if n.right else 0)
        return 1 + min(lt, ls) + min(rt, rs), skip

    return min(dfs(root))


UNCOVERED, COVERED, CAMERA = 0, 1, 2


def min_cameras(root):
    """Fewest cameras so every node has a camera on itself or a neighbour.

    Greedy-by-DP from the leaves: never put a camera on a leaf when its parent
    can cover the leaf *and* more.
    """
    cams = 0

    def dfs(n):
        nonlocal cams
        if not n:
            return COVERED
        l, r = dfs(n.left), dfs(n.right)
        if l == UNCOVERED or r == UNCOVERED:
            cams += 1
            return CAMERA
        return COVERED if l == CAMERA or r == CAMERA else UNCOVERED

    root_state = dfs(root)  # must run before cams is read
    return cams + (root_state == UNCOVERED)


def min_cameras_iterative(root):
    cams, state = 0, {None: COVERED}
    for n in reversed(nodes(root)):
        l, r = state[n.left], state[n.right]
        if UNCOVERED in (l, r):
            cams += 1
            state[n] = CAMERA
        else:
            state[n] = COVERED if CAMERA in (l, r) else UNCOVERED
    return cams + (state[root] == UNCOVERED)


# ------------------------------------------------------------------------ tests


def _subsets(root):
    ns = nodes(root)
    for size in range(len(ns) + 1):
        for chosen in combinations(ns, size):
            yield set(chosen)


def _edges(root):
    return [(n, ch) for n in nodes(root) for ch in (n.left, n.right) if ch]


def test_rob_known():
    assert rob_tree(build([3, 2, 3, None, 3, None, 1])) == 7
    assert rob_tree(build([3, 4, 5, 1, 3, None, 1])) == 9
    assert rob_tree(None) == rob_tree_iterative(None) == 0


def test_cameras_known():
    assert min_cameras(build([0, 0, None, 0, 0])) == 1
    assert min_cameras(build([0, 0, None, 0, None, 0, None, None, 0])) == 2
    assert min_cameras(build([0])) == 1
    assert min_cameras(None) == 0


def test_reference_evaluation_order_bug():
    # The reference returned `cams + (dfs(root) == 0)`. Python evaluates the
    # left operand first, so it read cams while it was still 0.
    def reference(root):
        cams = 0

        def dfs(n):
            nonlocal cams
            if not n:
                return 1
            l, r = dfs(n.left), dfs(n.right)
            if l == 0 or r == 0:
                cams += 1
                return 2
            return 1 if l == 2 or r == 2 else 0

        return cams + (dfs(root) == 0)

    t = build([0, 0, None, 0, 0])
    assert reference(t) == 0  # wrong: one camera is needed
    assert min_cameras(t) == min_cameras_iterative(t) == 1


def test_vertex_cover_known():
    assert min_vertex_cover(build([1, 2, 3, 4, 5])) == 2  # nodes 1 and 2
    assert min_vertex_cover(build([1])) == 0
    assert min_vertex_cover(None) == 0


def test_matches_brute_force():
    rng = random.Random(130)
    for _ in range(250):
        t = random_tree(rng, rng.randint(1, 11), lo=0, hi=20)
        g, edges, subsets = to_graph(t), _edges(t), list(_subsets(t))
        rob = max(sum(n.val for n in s) for s in subsets
                  if not any(a in s and b in s for a, b in edges))
        cover = min(len(s) for s in subsets if all(a in s or b in s for a, b in edges))
        cams = min(len(s) for s in subsets if all(n in s or s & set(g[n]) for n in g))
        assert rob_tree(t) == rob_tree_iterative(t) == rob
        assert min_vertex_cover(t) == cover
        assert min_cameras(t) == min_cameras_iterative(t) == cams


def test_rob_with_negative_values():
    # skipping everything (total 0) must stay available
    assert rob_tree(build([-1, -2, -3])) == rob_tree_iterative(build([-1, -2, -3])) == 0


def test_skewed_both_ways():
    for side in ("left", "right"):
        t = skewed(5, side)  # 1-2-3-4-5
        assert rob_tree(t) == 9  # 1 + 3 + 5
        assert min_vertex_cover(t) == 2  # 2 and 4
        assert min_cameras(t) == min_cameras_iterative(t) == 2


def test_iterative_survives_deep_tree():
    n = 9_999  # a path of 3m nodes needs m cameras
    t = skewed(n, "right")
    assert min_cameras_iterative(t) == n // 3
    assert rob_tree_iterative(t) == sum(range(1, n + 1, 2))
    try:
        min_cameras(t)
    except RecursionError:
        pass
    else:
        raise AssertionError("expected min_cameras to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
