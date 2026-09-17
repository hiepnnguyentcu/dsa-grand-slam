"""Coordinate tagging — carry a column or a heap index through the BFS.

Signs: vertical columns, top/bottom view, "maximum width" where the gaps
       between nodes (the missing ones) count.
Approach: put (node, coordinate) in the queue instead of bare nodes.
          Columns: left child is col - 1, right is col + 1.
          Width: number positions like a heap — children of i are 2i and
          2i + 1 — so a level's width is last index - first index + 1, gaps
          included, no matter how many nodes are actually missing.
Complexity: O(n) for width; O(n) plus O(c log c) to sort c columns for
            vertical order (O(n log n) when ties must be sorted by value).
Gotchas: vertical order must be BFS, not DFS — DFS can emit a deep node of a
         column before a shallow one. Read the tie-break rule: LeetCode 314
         keeps same-cell nodes left to right, 987 sorts them by value.
         Heap indices double per level, so a 60-deep skewed tree has indices
         near 2^60; Python ints don't care, fixed-width languages do.
         Guard the empty tree — the reference width code crashes on it.

Run the tests at the bottom with:  python3 binary_trees/coordinate_tagging.py
"""

import random
from collections import defaultdict, deque

from tree import build, nodes, random_tree, set_parents, skewed


# ---------------------------------------------------------------- implementation


def vertical_order(root):
    """Columns left to right; inside a column, top to bottom then left to right."""
    cols, q = defaultdict(list), deque([(root, 0)] if root else [])
    while q:
        n, c = q.popleft()
        cols[c].append(n.val)
        if n.left:
            q.append((n.left, c - 1))
        if n.right:
            q.append((n.right, c + 1))
    return [cols[c] for c in sorted(cols)]


def vertical_traversal(root):
    """LeetCode 987: like vertical_order, but nodes sharing a cell sort by value."""
    cells, q = [], deque([(root, 0, 0)] if root else [])
    while q:
        n, r, c = q.popleft()
        cells.append((c, r, n.val))
        if n.left:
            q.append((n.left, r + 1, c - 1))
        if n.right:
            q.append((n.right, r + 1, c + 1))
    out, last = [], None
    for c, _, v in sorted(cells):
        if c != last:
            out.append([])
            last = c
        out[-1].append(v)
    return out


def top_view(root):
    """First node BFS reaches in each column."""
    return [col[0] for col in vertical_order(root)]


def bottom_view(root):
    """Last node BFS reaches in each column (the later one wins a tie)."""
    return [col[-1] for col in vertical_order(root)]


def max_width(root):
    """Widest level, counting the missing positions between its end nodes."""
    if not root:
        return 0
    best, q = 0, deque([(root, 0)])
    while q:
        best = max(best, q[-1][1] - q[0][1] + 1)
        for _ in range(len(q)):
            n, i = q.popleft()
            if n.left:
                q.append((n.left, 2 * i))
            if n.right:
                q.append((n.right, 2 * i + 1))
    return best


# ------------------------------------------------------------------------ tests


def _coords(root):
    """Brute force: {node: (row, col)} by walking parent pointers."""
    out = {}
    for n in nodes(set_parents(root)):
        r = c = 0
        x = n
        while x.parent:
            c += -1 if x.parent.left is x else 1
            r += 1
            x = x.parent
        out[n] = (r, c)
    return out


def _width_brute(root):
    """Materialise every row as a full list with None holes, then measure."""
    best, row = 0, [root] if root else []
    while any(row):
        idx = [i for i, n in enumerate(row) if n]
        best = max(best, idx[-1] - idx[0] + 1)
        row = [ch for n in row for ch in ((n.left, n.right) if n else (None, None))]
    return best


def test_vertical_order_known():
    assert vertical_order(build([3, 9, 20, None, None, 15, 7])) == [[9], [3, 15], [20], [7]]
    # 2 sits deep in column 1 under the left subtree; DFS would list it before 8
    t = build([3, 9, 8, 4, 0, 1, 7, None, None, None, 2, 5])
    assert vertical_order(t) == [[4], [9, 5], [3, 0, 1], [8, 2], [7]]


def test_vertical_traversal_sorts_ties():
    # 5 and 6 share row 2, column 0; 314 keeps them left to right, 987 sorts
    t = build([1, 2, 3, 4, 6, 5, 7])
    assert vertical_order(t) == [[4], [2], [1, 6, 5], [3], [7]]
    assert vertical_traversal(t) == [[4], [2], [1, 5, 6], [3], [7]]


def test_vertical_matches_brute_force():
    rng = random.Random(60)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 30))
        pos = _coords(t) if t else {}
        pre = {n: i for i, n in enumerate(nodes(t))}  # left-to-right within a row
        cols = sorted({c for _, c in pos.values()})
        by_bfs = sorted(pos, key=lambda n: (pos[n][1], pos[n][0], pre[n]))
        by_val = sorted(pos, key=lambda n: (pos[n][1], pos[n][0], n.val))
        assert [v for col in vertical_order(t) for v in col] == [n.val for n in by_bfs]
        assert [v for col in vertical_traversal(t) for v in col] == [n.val for n in by_val]
        assert len(vertical_order(t)) == len(vertical_traversal(t)) == len(cols)


def test_views():
    #       1
    #      / \
    #     2   3
    #      \
    #       4
    #        \
    #         5
    t = build([1, 2, 3, None, 4, None, None, None, 5])
    assert top_view(t) == [2, 1, 3]
    assert bottom_view(t) == [2, 4, 5]


def test_width_known():
    assert max_width(build([1, 3, 2, 5, 3, None, 9])) == 4
    assert max_width(build([1, 3, 2, 5, None, None, 9, 6, None, 7])) == 7
    assert max_width(build([1, 3, 2, 5])) == 2


def test_width_matches_brute_force():
    rng = random.Random(61)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 14))
        assert max_width(t) == _width_brute(t)


def test_empty_single_skewed():
    assert vertical_order(None) == vertical_traversal(None) == top_view(None) == []
    assert max_width(None) == 0
    assert max_width(build([1])) == 1
    for side, cols in (("left", [[3], [2], [1]]), ("right", [[1], [2], [3]])):
        assert vertical_order(skewed(3, side)) == cols
        assert max_width(skewed(3, side)) == 1


def test_deep_skewed_width_uses_big_indices():
    # the rightmost node at depth 199 has index 2^199 - 1; still width 1
    assert max_width(skewed(200, "right")) == 1
    assert len(vertical_order(skewed(20_000, "left"))) == 20_000


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
