"""Intersection — the first node two lists share, by switching starts.

Signs: "two lists merge into a Y shape, find the merge node", O(1) space,
       lists of unknown and different lengths. Same trick: LCA with parent
       pointers (binary_trees/lca.py).
Approach: walk pa from A and pb from B. When a pointer falls off the end,
          restart it at the OTHER list's head. Both travel a + c + b steps
          (a, b = private parts, c = shared tail), so they reach the junction
          on the same step — or both reach None together if there is none.
          Alternative: measure both lengths, advance the longer by the
          difference, then walk together.
Complexity: O(a + b + c) time, O(1) space. A visited set is O(a + c) space.
Gotchas:
  - Compare nodes with `is`, never values — equal values are not shared nodes.
  - Switch to the other head on None, not on .next is None, or the no-
    intersection case loops forever (they would never both be None).
  - Lists must be acyclic; with cycles combine with fast/slow
    (sliding_window/fast_slow.py).

Run the tests at the bottom with:  python3 linked_lists/intersection.py
"""

import random

from ll import from_list, nodes


# ---------------------------------------------------------------- implementation


def get_intersection_node(a, b):
    """LC 160. Two-pointer switch."""
    pa, pb = a, b
    while pa is not pb:
        pa = pa.next if pa else b
        pb = pb.next if pb else a
    return pa


def get_intersection_node_lengths(a, b):
    """LC 160. Align by length difference, then walk together."""
    la, lb = len(nodes(a)), len(nodes(b))
    if la < lb:
        a, b, la, lb = b, a, lb, la
    for _ in range(la - lb):
        a = a.next
    while a is not b:
        a, b = a.next, b.next
    return a


# ------------------------------------------------------------------------ tests


def make_y(rng, a, b, c):
    """Lists with private parts of length a, b and a shared tail of length c."""
    shared = from_list([rng.randint(0, 2) for _ in range(c)])
    ha = from_list([rng.randint(0, 2) for _ in range(a)])
    hb = from_list([rng.randint(0, 2) for _ in range(b)])

    def attach(h):
        if not h:
            return shared
        nodes(h)[-1].next = shared
        return h

    return attach(ha), attach(hb), shared


def test_example():
    shared = from_list([8, 4, 5])
    a = from_list([4, 1])
    a.next.next = shared
    b = from_list([5, 6, 1])
    b.next.next.next = shared
    assert get_intersection_node(a, b) is shared
    assert get_intersection_node(from_list([1, 2]), from_list([1, 2])) is None  # equal values, no share


def test_matches_visited_set():
    rng = random.Random(1)
    for _ in range(1000):
        a, b, c = rng.randint(0, 8), rng.randint(0, 8), rng.randint(0, 8)
        ha, hb, shared = make_y(rng, a, b, c)
        seen = {id(x) for x in nodes(ha)}
        ref = next((x for x in nodes(hb) if id(x) in seen), None)  # brute force
        assert ref is shared
        assert get_intersection_node(ha, hb) is ref
        assert get_intersection_node_lengths(ha, hb) is ref


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
