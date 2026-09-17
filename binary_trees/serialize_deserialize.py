"""Serialize / deserialize — a tree to a string and back.

Signs: encode a tree for storage or the wire, deep copy, compare or hash
       whole structures via strings, find duplicate subtrees.
Approach: preorder with '#' for every missing child. The null markers make the
          encoding unambiguous on their own, so no inorder is needed.
          Deserialize consumes the tokens in the same order: a token is a node
          whose left subtree comes next, then its right; '#' ends a branch.
          (tree.py's to_list/build is the other common codec: level order.)
Complexity: O(n) time and space.
Gotchas: split on a delimiter — values can be negative or multi-digit, so
         never parse character by character. Forgetting the null markers
         loses the shape. The recursive pair overflows at ~1000 levels; the
         iterative pair produces the same string and handles any depth.

Run the tests at the bottom with:  python3 binary_trees/serialize_deserialize.py
"""

import random

from tree import TreeNode, build, nodes, random_tree, skewed, to_list


# ---------------------------------------------------------------- implementation


def serialize(root):
    out = []

    def dfs(n):
        if not n:
            out.append("#")
            return
        out.append(str(n.val))
        dfs(n.left)
        dfs(n.right)

    dfs(root)
    return ",".join(out)


def deserialize(data):
    it = iter(data.split(","))

    def build():
        v = next(it)
        if v == "#":
            return None
        n = TreeNode(int(v))
        n.left = build()
        n.right = build()
        return n

    return build()


def serialize_iterative(root):
    out, st = [], [root]
    while st:
        n = st.pop()
        if n is None:
            out.append("#")
        else:
            out.append(str(n.val))
            st += [n.right, n.left]
    return ",".join(out)


def deserialize_iterative(data):
    """Stack of [node, filled] pairs: filled is 0 until its left slot is set.

    Each token goes into the top node's next empty slot. A node whose right
    slot has just been filled is complete, so it leaves the stack; a new real
    node goes on top because the tokens that follow belong to its subtree.
    """
    tokens = data.split(",")
    if tokens[0] == "#":
        return None
    root = TreeNode(int(tokens[0]))
    st = [[root, 0]]
    for tok in tokens[1:]:
        node = None if tok == "#" else TreeNode(int(tok))
        top = st[-1]
        if top[1] == 0:
            top[0].left, top[1] = node, 1
        else:
            top[0].right = node
            st.pop()
        if node:
            st.append([node, 0])
    return root


# ------------------------------------------------------------------------ tests


def test_known():
    t = build([1, 2, 3, None, None, 4, 5])
    assert serialize(t) == "1,2,#,#,3,4,#,#,5,#,#"
    assert to_list(deserialize("1,2,#,#,3,4,#,#,5,#,#")) == [1, 2, 3, None, None, 4, 5]


def test_empty_and_single():
    for ser, de in ((serialize, deserialize), (serialize_iterative, deserialize_iterative)):
        assert ser(None) == "#" and de("#") is None
        assert ser(build([0])) == "0,#,#"
        assert to_list(de("0,#,#")) == [0]


def test_shape_is_preserved_by_null_markers():
    a, b = build([1, 2]), build([1, None, 2])
    assert serialize(a) != serialize(b)
    assert to_list(deserialize(serialize(b))) == [1, None, 2]


def test_negative_and_multi_digit_values():
    t = build([-10, 123, -7, None, 45])
    assert to_list(deserialize(serialize(t))) == [-10, 123, -7, None, 45]
    assert to_list(deserialize_iterative(serialize_iterative(t))) == [-10, 123, -7, None, 45]


def test_round_trip_random():
    rng = random.Random(110)
    for _ in range(400):
        t = random_tree(rng, rng.randint(0, 40), lo=-1000, hi=1000)
        s = serialize(t)
        assert serialize_iterative(t) == s
        assert s.count("#") == len(nodes(t)) + 1  # n nodes have n + 1 empty slots
        for de in (deserialize, deserialize_iterative):
            copy = de(s)
            assert to_list(copy) == to_list(t)
            assert serialize(copy) == s
            assert not set(map(id, nodes(copy))) & set(map(id, nodes(t)))  # a real deep copy


def test_skewed_both_ways():
    assert serialize(skewed(2, "left")) == "1,2,#,#,#"
    assert serialize(skewed(2, "right")) == "1,#,2,#,#"
    for side in ("left", "right"):
        t = skewed(6, side)
        assert to_list(deserialize_iterative(serialize_iterative(t))) == to_list(t)


def test_iterative_survives_deep_trees():
    for side in ("left", "right"):
        t = skewed(20_000, side)
        s = serialize_iterative(t)
        assert to_list(deserialize_iterative(s)) == to_list(t)
    try:
        serialize(t)
    except RecursionError:
        pass
    else:
        raise AssertionError("expected serialize to overflow on a deep path")
    try:
        deserialize(s)
    except RecursionError:
        pass
    else:
        raise AssertionError("expected deserialize to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
