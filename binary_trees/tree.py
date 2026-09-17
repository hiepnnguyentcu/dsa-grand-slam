"""Binary tree node, LeetCode level-order encoding, and test-tree generators.

Signs: every other file in this folder imports from here — this is the shared
       plumbing, not a technique.
Approach: `build` and `to_list` speak LeetCode's level-order encoding:
          [1, None, 2, 3] is 1 with no left child, right child 2, and 3 as
          2's left child. Only *present* nodes claim two slots in the list, so
          a missing node's children are simply never written.
          `random_tree` grows a tree by attaching each new node to a random
          empty child slot, which gives a good mix of bushy and stringy shapes.
Complexity: O(n) for build / to_list / nodes / to_graph.
Gotchas: trailing Nones are dropped by to_list, so build(to_list(t)) round-
         trips but to_list(build(x)) only equals x if x had no trailing
         Nones. Everything here is iterative, so deep skewed trees are safe
         to build and inspect even where the recursive technique under test
         is not.

Run the tests at the bottom with:  python3 binary_trees/tree.py
"""

import random
from collections import deque


# ---------------------------------------------------------------- implementation


class TreeNode:
    __slots__ = ("val", "left", "right", "parent")

    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right
        self.parent = None  # only filled in by set_parents, for the few techniques that want it

    def __repr__(self):
        return f"TreeNode({self.val!r})"


def build(values):
    """Tree from a level-order list with None for missing nodes."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    q, i = deque([root]), 1
    # once the list runs out every remaining slot is empty, so stop there
    # rather than draining the queue
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


def set_parents(root):
    """Fill in node.parent for every node (root's parent stays None)."""
    for n in nodes(root):
        for ch in (n.left, n.right):
            if ch:
                ch.parent = n
    return root


def to_graph(root):
    """Undirected adjacency dict {node: [neighbour, ...]} — the brute-force view.

    Many tests check a clever tree answer by forgetting the tree is a tree and
    running BFS on this graph instead.
    """
    g = {n: [] for n in nodes(root)}
    for n in g:
        for ch in (n.left, n.right):
            if ch:
                g[n].append(ch)
                g[ch].append(n)
    return g


def bfs_dist(g, src):
    """Hop distance from src to every node of an adjacency dict."""
    dist, q = {src: 0}, deque([src])
    while q:
        u = q.popleft()
        for v in g[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def random_tree(rng, n, lo=-9, hi=9, values=None):
    """A random-shaped tree of n nodes.

    Values are drawn from [lo, hi] unless `values` (a sequence of length n) is
    given — pass range(n) or a shuffled list when a technique needs unique
    values. Each new node goes into a uniformly random empty child slot.
    """
    if n == 0:
        return None
    vals = list(values) if values is not None else [rng.randint(lo, hi) for _ in range(n)]
    root = TreeNode(vals[0])
    slots = [(root, "left"), (root, "right")]
    for v in vals[1:]:
        i = rng.randrange(len(slots))
        slots[i], slots[-1] = slots[-1], slots[i]
        parent, side = slots.pop()
        child = TreeNode(v)
        setattr(parent, side, child)
        slots += [(child, "left"), (child, "right")]
    return root


def skewed(n, side="left", start=1):
    """A path of n nodes where every node has only a `side` child."""
    root = None
    for v in range(start + n - 1, start - 1, -1):
        node = TreeNode(v)
        setattr(node, side, root)
        root = node
    return root


def complete_tree(n):
    """The complete tree with values 1..n in level order (heap layout)."""
    return build(list(range(1, n + 1)))


# ------------------------------------------------------------------------ tests


def test_build_shape():
    #     1
    #      \
    #       2
    #      /
    #     3
    root = build([1, None, 2, 3])
    assert root.val == 1 and root.left is None
    assert root.right.val == 2 and root.right.right is None
    assert root.right.left.val == 3


def test_missing_nodes_claim_no_slots():
    #       1
    #      / \
    #     2   3
    #    /     \
    #   4       5
    #          /
    #         6
    # 2's right slot is written as None; 4 has children slots but they are
    # trailing and dropped, so 6 goes to 5, not to 4.
    root = build([1, 2, 3, 4, None, None, 5, None, None, 6])
    assert root.right.right.left.val == 6
    assert root.left.left.left is None


def test_round_trip_known():
    for vals in ([], [1], [1, 2], [1, None, 2], [3, 9, 20, None, None, 15, 7],
                 [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]):
        assert to_list(build(vals)) == vals


def test_trailing_nones_are_dropped():
    assert to_list(build([1, 2, None, None, None])) == [1, 2]
    assert build([None]) is None


def test_round_trip_random():
    rng = random.Random(1)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 40))
        vals = to_list(t)
        assert to_list(build(vals)) == vals
        assert len(nodes(build(vals))) == len(nodes(t))


def test_random_tree_has_n_nodes_and_given_values():
    rng = random.Random(2)
    for n in range(30):
        t = random_tree(rng, n, values=range(n))
        assert sorted(x.val for x in nodes(t)) == list(range(n))


def test_random_tree_shapes_vary():
    # a generator that only ever produced paths or only full trees would make
    # every "compare against brute force" test much weaker
    rng = random.Random(3)
    shapes = {tuple(v is None for v in to_list(random_tree(rng, 6))) for _ in range(200)}
    assert len(shapes) > 50


def test_skewed():
    assert to_list(skewed(3, "left")) == [1, 2, None, 3]
    assert to_list(skewed(3, "right")) == [1, None, 2, None, 3]
    assert skewed(0) is None


def test_deep_skewed_is_fine_iteratively():
    t = skewed(50_000, "right")
    assert len(nodes(t)) == 50_000
    assert len(to_list(t)) == 2 * 50_000 - 1
    assert to_list(build(to_list(t))) == to_list(t)


def test_complete_tree():
    assert to_list(complete_tree(6)) == [1, 2, 3, 4, 5, 6]
    assert complete_tree(0) is None


def test_parents_and_graph():
    root = set_parents(build([1, 2, 3, 4]))
    four = root.left.left
    assert four.parent is root.left and root.left.parent is root and root.parent is None
    g = to_graph(root)
    assert len(g) == 4 and sum(map(len, g.values())) == 2 * 3  # n - 1 edges, both ways
    assert bfs_dist(g, four)[root.right] == 3


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
