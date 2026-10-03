"""Singly linked list node, list <-> Python list conversion, test generators.

Signs: every other file in this folder imports from here — this is the shared
       plumbing, not a technique.
Approach: `from_list` / `to_list` convert to and from plain Python lists so
          every test can compute the expected answer with list slicing and
          compare. `nodes` returns the node objects themselves, which is how
          tests prove an in-place operation reused the original nodes instead
          of allocating new ones.
Complexity: O(n) for every helper.
Gotchas: `to_list` refuses to walk more than `limit` nodes, so a bug that
         accidentally creates a cycle fails loudly instead of hanging the test
         run. Everything is iterative, so 100k-node lists are fine.

Run the tests at the bottom with:  python3 linked_lists/ll.py
"""

import random


# ---------------------------------------------------------------- implementation


class ListNode:
    __slots__ = ("val", "next")

    def __init__(self, val=0, next=None):
        self.val, self.next = val, next

    def __repr__(self):
        return f"ListNode({self.val!r})"


def from_list(values):
    """Head of a new list holding values in order (None for empty)."""
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def to_list(head, limit=10**6):
    """Values from head to the end. Raises on a cycle / runaway list."""
    out = []
    while head:
        out.append(head.val)
        head = head.next
        if len(out) > limit:
            raise RuntimeError("list longer than limit — cycle?")
    return out


def nodes(head, limit=10**6):
    """The node objects from head to the end, in order."""
    out = []
    while head:
        out.append(head)
        head = head.next
        if len(out) > limit:
            raise RuntimeError("list longer than limit — cycle?")
    return out


def length(head):
    n = 0
    while head:
        n, head = n + 1, head.next
    return n


def random_values(rng, n, lo=-9, hi=9):
    return [rng.randint(lo, hi) for _ in range(n)]


def random_list(rng, n, lo=-9, hi=9):
    """(head, values) for a random list of n values in [lo, hi]."""
    vals = random_values(rng, n, lo, hi)
    return from_list(vals), vals


def random_sorted_list(rng, n, lo=-9, hi=9):
    """(head, values) for a random non-decreasing list — duplicates likely."""
    vals = sorted(random_values(rng, n, lo, hi))
    return from_list(vals), vals


def same_nodes(before, after_head):
    """True if the list at after_head uses exactly the node objects in before."""
    return {id(x) for x in before} == {id(x) for x in nodes(after_head)}


def subset_nodes(before, after_head):
    """True if every node at after_head was already in before (no allocation)."""
    old = {id(x) for x in before}
    return all(id(x) in old for x in nodes(after_head))


# ------------------------------------------------------------------------ tests


def test_round_trip():
    for vals in ([], [1], [1, 2, 3], [5, 5, 5]):
        assert to_list(from_list(vals)) == vals
    assert from_list([]) is None


def test_round_trip_random():
    rng = random.Random(1)
    for _ in range(200):
        head, vals = random_list(rng, rng.randint(0, 30))
        assert to_list(head) == vals and length(head) == len(vals)
        assert [x.val for x in nodes(head)] == vals


def test_sorted_generator():
    rng = random.Random(2)
    for _ in range(100):
        head, vals = random_sorted_list(rng, rng.randint(0, 30))
        assert to_list(head) == sorted(vals)


def test_cycle_is_caught():
    head = from_list([1, 2, 3])
    head.next.next.next = head
    try:
        to_list(head, limit=100)
    except RuntimeError:
        return
    raise AssertionError("cycle not detected")


def test_identity_helpers():
    head = from_list([1, 2, 3])
    ns = nodes(head)
    assert same_nodes(ns, head) and subset_nodes(ns, head.next)
    assert not same_nodes(ns, from_list([1, 2, 3]))
    assert not subset_nodes(ns, from_list([1]))


def test_long_list_is_fine():
    head = from_list(list(range(100_000)))
    assert length(head) == 100_000 and to_list(head)[-1] == 99_999


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
