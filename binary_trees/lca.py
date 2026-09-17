"""Lowest common ancestor — the deepest node that has both p and q below it.

Signs: LCA of two nodes, distance between two nodes (depth(p) + depth(q) -
       2 * depth(lca)), "smallest subtree containing" two nodes.
Approach: recursive — return the node itself if it is p or q (or None);
          otherwise ask both children. If both sides found something, p and q
          split here, so this node is the LCA; otherwise pass up whichever
          side found something.
          With parent pointers it becomes linked-list intersection: walk up
          from p and from q, and when a pointer falls off the root, restart
          it at the *other* start. Both pointers then travel depth(p) +
          depth(q) steps and meet at the LCA.
Complexity: O(n) time, O(h) space; O(h) time and O(1) space with parents.
Gotchas: the recursive version assumes both nodes are in the tree — if only p
         is, it returns p rather than None. A node counts as its own
         ancestor, so lca(p, child of p) is p. Compare nodes with `is`, not
         by value, when values repeat. Recursion depth is the height (~1000-
         frame limit); the parent-map version is iterative.

Run the tests at the bottom with:  python3 binary_trees/lca.py
"""

import random

from tree import bfs_dist, build, nodes, random_tree, set_parents, skewed, to_graph


# ---------------------------------------------------------------- implementation


def lca(root, p, q):
    if not root or root is p or root is q:
        return root
    l, r = lca(root.left, p, q), lca(root.right, p, q)
    return root if l and r else l or r


def lca_parent(p, q):
    """LCA using node.parent pointers only — no root needed."""
    a, b = p, q
    while a is not b:
        a = a.parent if a else q
        b = b.parent if b else p
    return a


def lca_iterative(root, p, q):
    """No recursion and no parent field: record parents with a stack first.

    Stops the walk as soon as both p and q have been seen, then collects p's
    ancestors and climbs from q until it hits one.
    """
    parent, st = {root: None}, [root]
    while p not in parent or q not in parent:
        n = st.pop()
        for ch in (n.left, n.right):
            if ch:
                parent[ch] = n
                st.append(ch)
    ancestors = set()
    while p:
        ancestors.add(p)
        p = parent[p]
    while q not in ancestors:
        q = parent[q]
    return q


def node_distance(root, p, q):
    """Edges between p and q, via the LCA."""

    def depth(target):
        st = [(root, 0)]  # no parent pointers assumed, so search with a stack
        while st:
            n, d = st.pop()
            if n is target:
                return d
            st += [(ch, d + 1) for ch in (n.left, n.right) if ch]
        raise ValueError("node not in tree")

    a = lca_iterative(root, p, q)
    return depth(p) + depth(q) - 2 * depth(a)


# ------------------------------------------------------------------------ tests


def _lca_brute(p, q):
    """Deepest node on both parent chains (needs set_parents)."""
    chain = []
    while p:
        chain.append(p)
        p = p.parent
    qs = set()
    while q:
        qs.add(q)
        q = q.parent
    return next(x for x in chain if x in qs)


def _find(root, val):
    return next(n for n in nodes(root) if n.val == val)


def test_known():
    #         3
    #       /   \
    #      5     1
    #     / \   / \
    #    6   2 0   8
    #       / \
    #      7   4
    t = set_parents(build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]))
    f = lambda v: _find(t, v)
    for p, q, want in ((5, 1, 3), (5, 4, 5), (7, 4, 2), (6, 4, 5), (7, 8, 3), (0, 0, 0)):
        for fn in (lambda a, b: lca(t, a, b), lca_parent, lambda a, b: lca_iterative(t, a, b)):
            assert fn(f(p), f(q)) is f(want)
    assert node_distance(t, f(6), f(4)) == 3
    assert node_distance(t, f(7), f(8)) == 5
    assert node_distance(t, f(1), f(1)) == 0


def test_matches_brute_force():
    rng = random.Random(80)
    for _ in range(200):
        # values 0/1 repeat on purpose: identity, not value, must decide
        t = set_parents(random_tree(rng, rng.randint(1, 30), lo=0, hi=1))
        ns, g = nodes(t), to_graph(t)
        for _ in range(10):
            p, q = rng.choice(ns), rng.choice(ns)
            want = _lca_brute(p, q)
            assert lca(t, p, q) is want
            assert lca_parent(p, q) is want
            assert lca_iterative(t, p, q) is want
            assert node_distance(t, p, q) == bfs_dist(g, p)[q]


def test_single_node_and_missing_node():
    t = build([1])
    assert lca(t, t, t) is t and lca_iterative(t, t, t) is t
    # the recursive form only reports what it finds: with q absent it returns p
    t = build([1, 2, 3])
    stranger = build([9])
    assert lca(t, t.left, stranger) is t.left
    assert lca(None, t, t) is None


def test_skewed_both_ways():
    for side in ("left", "right"):
        t = set_parents(skewed(6, side))
        ns = nodes(t)
        assert lca(t, ns[2], ns[5]) is ns[2]  # an ancestor is its own answer
        assert lca_parent(ns[5], ns[2]) is ns[2]
        assert node_distance(t, ns[0], ns[5]) == 5


def test_iterative_survives_deep_tree():
    t = set_parents(skewed(10_000, "left"))
    ns = nodes(t)
    assert lca_parent(ns[-1], ns[5_000]) is ns[5_000]
    assert lca_iterative(t, ns[-1], ns[7_000]) is ns[7_000]
    try:
        lca(t, ns[-1], ns[-2])
    except RecursionError:
        pass
    else:
        raise AssertionError("expected lca to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
