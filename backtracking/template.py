"""Backtracking template — choose, explore, unchoose.

Signs: "return all", "list every", "generate", "find any arrangement that
       satisfies", n small (<= 10-20), answer size itself exponential.
Approach: depth-first walk over a decision tree. At each node: if the partial
          solution is complete, record a *copy*; otherwise for each legal
          choice, apply it (choose), recurse (explore), then undo it
          (unchoose). One mutable `path` is shared by the whole search, so the
          undo must exactly reverse the apply.
          Two tree shapes cover almost everything:
            - include/exclude: one binary decision per element (2^n leaves).
            - for-loop from `start`: each level picks the next element at or
              after `start`, so every subset/combination appears once.
Complexity: O(leaves x cost per leaf). Subsets 2^n * n, permutations n! * n.
            Pruning cuts the tree, never the worst-case bound.
Gotchas:
  - `out.append(path)` stores a reference that later becomes []; append
    `path[:]` or `tuple(path)`.
  - Every mutation in "choose" needs a matching undo in "unchoose" — including
    sets, counters, grid marks. A missed undo leaks state into siblings.
  - If you only need a count or an optimum and subproblems repeat, this is DP
    (see dynamic_programming/), not backtracking.
  - Python recursion limit is 1000; depth here is the path length, which is
    fine for the small n backtracking is used on.

Run the tests at the bottom with:  python3 backtracking/template.py
"""

import random
from itertools import product


# ---------------------------------------------------------------- implementation


def backtrack(n_slots, choices, ok):
    """All sequences of length n_slots built from `choices`, keeping only those
    where ok(path, c) holds for each appended c. The generic skeleton.

    ok(path, c) sees the partial path *before* c is added, so it can prune a
    whole subtree the moment a prefix goes bad.
    """
    out, path = [], []

    def go():
        if len(path) == n_slots:
            out.append(path[:])            # copy, not the live list
            return
        for c in choices:
            if not ok(path, c):
                continue                   # prune this branch
            path.append(c)                 # choose
            go()                           # explore
            path.pop()                     # unchoose
    go()
    return out


def include_exclude(nums):
    """Subsets via the binary decision tree: skip nums[i], or take it."""
    out, path = [], []

    def go(i):
        if i == len(nums):
            out.append(path[:])
            return
        go(i + 1)                          # exclude
        path.append(nums[i])
        go(i + 1)                          # include
        path.pop()
    go(0)
    return out


def all_paths_dag(g, src, dst):
    """Every path src -> dst in a DAG {u: [v]}. No `visited` needed: no cycles.

    In a graph with cycles, add an on-path set and undo it on the way back —
    the same choose/unchoose discipline, applied to the set.
    """
    out, path = [], [src]

    def go(u):
        if u == dst:
            out.append(path[:])
            return
        for v in g.get(u, ()):
            path.append(v)
            go(v)
            path.pop()
    go(src)
    return out


def simple_paths(g, src, dst):
    """Every simple path src -> dst in a graph that may have cycles."""
    out, path, on_path = [], [src], {src}

    def go(u):
        if u == dst:
            out.append(path[:])
            return
        for v in g.get(u, ()):
            if v in on_path:
                continue
            on_path.add(v); path.append(v)       # choose (both structures)
            go(v)
            on_path.discard(v); path.pop()       # unchoose (both structures)
    go(src)
    return out


# ------------------------------------------------------------------------ tests


def test_backtrack_matches_product_filter():
    # Binary strings of length 6 with no two adjacent 1s.
    ok = lambda path, c: not (c == 1 and path and path[-1] == 1)
    got = backtrack(6, [0, 1], ok)
    want = [list(t) for t in product([0, 1], repeat=6)
            if all(not (a == b == 1) for a, b in zip(t, t[1:]))]
    assert got == want
    assert len(got) == 21  # Fibonacci(8)


def test_backtrack_no_pruning_is_product():
    assert backtrack(3, "ab", lambda p, c: True) == [list(t) for t in product("ab", repeat=3)]


def test_copy_trap():
    out, path = [], []

    def go(i):
        if i == 2:
            out.append(path)  # BUG: the live list
            return
        path.append(i)
        go(i + 1)
        path.pop()
    go(0)
    assert out == [[]]  # it was emptied by the unchoose steps


def test_include_exclude_gives_power_set():
    nums = [3, 1, 4, 5]
    got = sorted(sorted(s) for s in include_exclude(nums))
    want = sorted(sorted(x for x, keep in zip(nums, bits) if keep)
                  for bits in product([0, 1], repeat=len(nums)))
    assert got == want and len(got) == 16


def test_all_paths_dag():
    g = {0: [1, 2], 1: [3], 2: [3], 3: []}
    assert sorted(all_paths_dag(g, 0, 3)) == [[0, 1, 3], [0, 2, 3]]
    assert all_paths_dag(g, 3, 0) == []


def test_simple_paths_random_vs_brute_force():
    from itertools import permutations

    random.seed(11)
    for _ in range(30):
        n = random.randint(2, 6)
        g = {u: [v for v in range(n) if v != u and random.random() < 0.4] for u in range(n)}
        got = sorted(simple_paths(g, 0, n - 1))
        # brute force: every ordering of every subset of middle nodes
        mids = list(range(1, n - 1))
        want = []
        for mask in range(1 << len(mids)):
            chosen = [mids[i] for i in range(len(mids)) if mask >> i & 1]
            for perm in permutations(chosen):
                p = [0, *perm, n - 1]
                if all(b in g[a] for a, b in zip(p, p[1:])):
                    want.append(p)
        assert got == sorted(want)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
