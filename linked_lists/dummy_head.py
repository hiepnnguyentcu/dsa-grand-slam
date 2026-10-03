"""Dummy head — a fake node before the head so deleting the head is not special.

Signs: "remove all nodes with value x", "delete duplicates from a sorted list",
       "partition around x", anything where the head itself might be removed
       or replaced, building a new list node by node.
Approach: dummy = ListNode(0, head). Keep a pointer `prev` that is always the
          last node you are keeping; decide about prev.next, then either skip
          it (prev.next = prev.next.next) or keep it (prev = prev.next).
          Return dummy.next — never the old head, which may be gone.
          Partition builds two lists, each with its own dummy, then joins.
          Delete-given-only-the-node has no prev at all: copy the next value
          into this node and delete the next node instead.
Complexity: O(n) time, O(1) extra space; nodes are relinked, never allocated.
Gotchas:
  - After skipping, do NOT advance prev — the new prev.next needs checking too
    (e.g. removing 6 from 6 -> 6 -> 1).
  - Partition: cut the tail (big_tail.next = None) or the last big node still
    points into the small list and you get a cycle.
  - Duplicates II removes every copy: remember the duplicate value and skip
    while equal, then relink prev once.
  - Delete-node cannot delete the tail (nothing to copy from) and it changes
    which node object holds which value — fine for LC 237, wrong if others
    hold references to the next node.

Run the tests at the bottom with:  python3 linked_lists/dummy_head.py
"""

import random

from ll import ListNode, from_list, nodes, random_list, random_sorted_list, subset_nodes, to_list


# ---------------------------------------------------------------- implementation


def remove_elements(head, val):
    """LC 203. Remove every node whose value is val."""
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next:
        if prev.next.val == val:
            prev.next = prev.next.next  # skip; prev stays, recheck new next
        else:
            prev = prev.next
    return dummy.next


def delete_duplicates(head):
    """LC 83. Sorted list: keep one copy of each value. Head never goes, so no dummy."""
    cur = head
    while cur and cur.next:
        if cur.next.val == cur.val:
            cur.next = cur.next.next
        else:
            cur = cur.next
    return head


def delete_duplicates_ii(head):
    """LC 82. Sorted list: drop every value that appears more than once."""
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next:
        cur = prev.next
        if cur.next and cur.next.val == cur.val:
            v = cur.val
            while cur and cur.val == v:
                cur = cur.next
            prev.next = cur             # the whole run is gone
        else:
            prev = cur
    return dummy.next


def partition(head, x):
    """LC 86. Nodes < x first, then the rest; both halves keep their order."""
    small = small_tail = ListNode(0)
    big = big_tail = ListNode(0)
    while head:
        if head.val < x:
            small_tail.next = head
            small_tail = head
        else:
            big_tail.next = head
            big_tail = head
        head = head.next
    big_tail.next = None                # cut, or the last big node may loop back
    small_tail.next = big.next
    return small.next


def delete_node(node):
    """LC 237. Delete node (not the tail) with no access to the head."""
    node.val = node.next.val
    node.next = node.next.next


# ------------------------------------------------------------------------ tests


def test_examples():
    assert to_list(remove_elements(from_list([1, 2, 6, 3, 4, 5, 6]), 6)) == [1, 2, 3, 4, 5]
    assert to_list(remove_elements(from_list([7, 7, 7]), 7)) == []
    assert to_list(delete_duplicates(from_list([1, 1, 2, 3, 3]))) == [1, 2, 3]
    assert to_list(delete_duplicates_ii(from_list([1, 1, 1, 2, 3]))) == [2, 3]
    assert to_list(partition(from_list([1, 4, 3, 2, 5, 2]), 3)) == [1, 2, 2, 4, 3, 5]
    head = from_list([4, 5, 1, 9])
    delete_node(head.next)
    assert to_list(head) == [4, 1, 9]


def test_remove_elements_matches_filter():
    rng = random.Random(1)
    for _ in range(500):
        head, vals = random_list(rng, rng.randint(0, 15), 0, 3)
        before = nodes(head)
        v = rng.randint(0, 3)
        out = remove_elements(head, v)
        assert to_list(out) == [x for x in vals if x != v]
        assert subset_nodes(before, out)


def test_delete_duplicates_match_counter():
    from collections import Counter

    rng = random.Random(2)
    for _ in range(500):
        head, vals = random_sorted_list(rng, rng.randint(0, 15), 0, 5)
        before = nodes(head)
        out = delete_duplicates(head)
        assert to_list(out) == sorted(set(vals)) and subset_nodes(before, out)

        head = from_list(vals)
        before = nodes(head)
        c = Counter(vals)
        out = delete_duplicates_ii(head)
        assert to_list(out) == [v for v in vals if c[v] == 1] and subset_nodes(before, out)


def test_partition_is_stable_and_in_place():
    rng = random.Random(3)
    for _ in range(500):
        head, vals = random_list(rng, rng.randint(0, 15), 0, 6)
        before = nodes(head)
        x = rng.randint(-1, 7)
        out = partition(head, x)
        got = nodes(out)
        assert [n.val for n in got] == [v for v in vals if v < x] + [v for v in vals if v >= x]
        # same node objects, and each half keeps original relative order
        pos = {id(n): i for i, n in enumerate(before)}
        small = [pos[id(n)] for n in got if n.val < x]
        big = [pos[id(n)] for n in got if n.val >= x]
        assert small == sorted(small) and big == sorted(big) and len(got) == len(before)


def test_delete_node_matches_list_delete():
    rng = random.Random(4)
    for _ in range(300):
        head, vals = random_list(rng, rng.randint(2, 12))
        i = rng.randrange(len(vals) - 1)          # never the tail
        delete_node(nodes(head)[i])
        assert to_list(head) == vals[:i] + vals[i + 1:]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
