"""Depth-first search — recursive and iterative.

Signs: reachability, connected components, flood fill, path existence,
       cycle detection, exploring all configurations.
Approach: visit a node, mark it seen, then descend into unseen neighbours.
          The recursive call stack *is* the traversal stack; the iterative
          version makes that stack explicit.
Complexity: O(V + E) time, O(V) space.
Gotchas: CPython's recursion limit is ~1000 frames — a path graph of 10^5
         nodes will blow the stack, so reach for the iterative form on large
         grids/graphs (or raise sys.setrecursionlimit, which only moves the
         cliff).

Graphs are plain adjacency dicts: {node: [neighbour, ...]}. Neighbours are
read with g.get(u, ()) so sink nodes need no entry of their own.

Run the tests at the bottom with:  python3 graphs/dfs.py
"""


# ---------------------------------------------------------------- implementation


def dfs_recursive(g, start):
    """Preorder DFS. Returns nodes in the order they were first visited.

    A node is appended when it is *entered*, before its children are explored.
    """
    seen, order = set(), []

    def visit(u):
        seen.add(u)
        order.append(u)
        for v in g.get(u, ()):
            if v not in seen:
                visit(v)

    visit(start)
    return order


def dfs_iterative(g, start):
    """Preorder DFS with an explicit stack. Same order as dfs_recursive.

    Two details make the orders match exactly:
      1. Neighbours are pushed in reverse, so the first neighbour ends up on
         top of the stack and is explored first.
      2. A node is marked seen when it is *popped*, not when it is pushed.
         Marking on push is also correct DFS, but it yields a different order
         because a node's position is then fixed by whoever pushed it first.
    A node can sit on the stack more than once; the `if u in seen` guard
    discards the stale copies.
    """
    seen, order, stack = set(), [], [start]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        order.append(u)
        for v in reversed(g.get(u, ())):
            if v not in seen:
                stack.append(v)
    return order


# ------------------------------------------------------------------------ tests

#     3       5           (7 --- 8 is a separate component)
#     |       |
#     0 --- 2 --- 4 --- 6
#     |           |
#     1 ----------+
GRAPH = {
    0: [1, 2, 3],
    1: [0, 4],
    2: [0, 4, 5],
    3: [0],
    4: [1, 2, 6],
    5: [2],
    6: [4],
    7: [8],
    8: [7],
}


def test_preorder_from_source():
    # 0 -> 1 -> 4 -> 2 -> 5, back up to 4 -> 6, back up to 0 -> 3
    assert dfs_recursive(GRAPH, 0) == [0, 1, 4, 2, 5, 6, 3]


def test_iterative_matches_recursive():
    for start in GRAPH:
        assert dfs_iterative(GRAPH, start) == dfs_recursive(GRAPH, start)


def test_visits_only_its_own_component():
    assert sorted(dfs_recursive(GRAPH, 0)) == [0, 1, 2, 3, 4, 5, 6]
    assert sorted(dfs_iterative(GRAPH, 7)) == [7, 8]


def test_isolated_node():
    assert dfs_recursive({0: []}, 0) == [0]
    assert dfs_iterative({}, "lonely") == ["lonely"]  # no adjacency entry at all


def test_directed_edges_are_one_way():
    g = {0: [1], 1: [2], 2: []}
    assert dfs_iterative(g, 0) == [0, 1, 2]
    assert dfs_iterative(g, 2) == [2]


def test_cycle_terminates():
    g = {0: [1], 1: [2], 2: [0]}  # every node reachable from every other
    assert dfs_recursive(g, 0) == [0, 1, 2]


def test_iterative_survives_depth_that_overflows_recursion():
    # A path graph deeper than CPython's ~1000-frame recursion limit. This is
    # the reason the iterative version exists.
    n = 10_000
    path = {i: [i + 1] for i in range(n - 1)}
    assert len(dfs_iterative(path, 0)) == n

    try:
        dfs_recursive(path, 0)
    except RecursionError:
        pass
    else:
        raise AssertionError("expected dfs_recursive to overflow on a deep path")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
