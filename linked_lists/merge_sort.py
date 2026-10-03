"""Merging & sorting — splice sorted lists together; merge sort a list.

Signs: "merge two sorted lists", "merge k sorted lists", "sort a linked list
       in O(n log n) and O(1) space", "insertion sort the list".
Approach: merge two: dummy + tail, take the smaller head each step, attach the
          leftover in one assignment. Merge k by divide & conquer: merge
          neighbours pairwise, halving the number of lists each round (the
          heap version is in stacks_heaps/k_way_merge.py). Sort list:
          top-down merge sort — split at the first middle, sort halves,
          merge. Bottom-up merges runs of 1, 2, 4, ... for true O(1) space.
          Insertion sort: walk a sorted dummy list from its start to find
          each node's slot.
Complexity: merge two O(n + m); merge k O(N log k); sort list O(n log n)
            with O(log n) recursion (bottom-up: O(1)); insertion O(n^2).
Gotchas:
  - Use `<=` when taking from the left list, or the merge (and the sort) is
    not stable.
  - Split at the FIRST middle (fast = head.next). With the second middle a
    2-node list splits into 2 + 0 and recursion never ends.
  - Merge k: lists can be empty or k can be 0 — return None.
  - Linked lists are where merge sort beats quicksort: no random access
    needed, and merging relinks instead of copying.

Run the tests at the bottom with:  python3 linked_lists/merge_sort.py
"""

import random

from ll import ListNode, from_list, nodes, random_list, random_sorted_list, same_nodes, to_list


# ---------------------------------------------------------------- implementation


def merge_two(a, b):
    """LC 21. Splice two sorted lists into one; stable (ties from a first)."""
    dummy = tail = ListNode(0)
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next


def merge_k(lists):
    """LC 23. Divide & conquer: pairwise rounds, log k of them."""
    lists = list(lists)
    if not lists:
        return None
    while len(lists) > 1:
        merged = [merge_two(lists[i], lists[i + 1]) for i in range(0, len(lists) - 1, 2)]
        if len(lists) % 2:
            merged.append(lists[-1])
        lists = merged
    return lists[0]


def sort_list(head):
    """LC 148. Top-down merge sort."""
    if not head or not head.next:
        return head
    slow, fast = head, head.next        # first middle
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    right, slow.next = slow.next, None
    return merge_two(sort_list(head), sort_list(right))


def sort_list_bottom_up(head):
    """LC 148 follow-up. Merge runs of width 1, 2, 4, ...: O(1) extra space."""
    n, cur = 0, head
    while cur:
        n, cur = n + 1, cur.next
    dummy = ListNode(0, head)
    width = 1
    while width < n:
        tail, cur = dummy, dummy.next
        while cur:
            left = cur
            right = _cut(left, width)
            cur = _cut(right, width)
            tail.next = merge_two(left, right)
            while tail.next:
                tail = tail.next
        width *= 2
    return dummy.next


def _cut(head, k):
    """Detach the first k nodes; return the head of what follows."""
    for _ in range(k - 1):
        if not head:
            return None
        head = head.next
    if not head:
        return None
    rest, head.next = head.next, None
    return rest


def insertion_sort_list(head):
    """LC 147. Stable insertion sort by relinking."""
    dummy = ListNode(0)
    while head:
        nxt = head.next
        prev = dummy
        while prev.next and prev.next.val <= head.val:  # <= keeps it stable
            prev = prev.next
        head.next, prev.next = prev.next, head
        head = nxt
    return dummy.next


# ------------------------------------------------------------------------ tests


def test_examples():
    assert to_list(merge_two(from_list([1, 2, 4]), from_list([1, 3, 4]))) == [1, 1, 2, 3, 4, 4]
    assert merge_k([]) is None and merge_k([None, None]) is None
    lists = [from_list([1, 4, 5]), from_list([1, 3, 4]), from_list([2, 6])]
    assert to_list(merge_k(lists)) == [1, 1, 2, 3, 4, 4, 5, 6]
    assert to_list(sort_list(from_list([4, 2, 1, 3]))) == [1, 2, 3, 4]
    assert to_list(insertion_sort_list(from_list([-1, 5, 3, 4, 0]))) == [-1, 0, 3, 4, 5]


def test_merge_two_matches_sorted_and_is_stable():
    rng = random.Random(1)
    for _ in range(500):
        a, va = random_sorted_list(rng, rng.randint(0, 12), 0, 5)
        b, vb = random_sorted_list(rng, rng.randint(0, 12), 0, 5)
        na, nb = nodes(a), nodes(b)
        out = nodes(merge_two(a, b))
        assert [x.val for x in out] == sorted(va + vb)
        # stability: ties come from a before b, each side in original order
        order = {id(x): (x.val, 0, i) for i, x in enumerate(na)}
        order.update({id(x): (x.val, 1, i) for i, x in enumerate(nb)})
        keys = [order[id(x)] for x in out]
        assert keys == sorted(keys) and len(out) == len(na) + len(nb)


def test_merge_k_matches_sorted():
    rng = random.Random(2)
    for _ in range(300):
        pairs = [random_sorted_list(rng, rng.randint(0, 8)) for _ in range(rng.randint(0, 9))]
        before = [x for h, _ in pairs for x in nodes(h)]
        out = merge_k(h for h, _ in pairs)
        assert to_list(out) == sorted(v for _, vals in pairs for v in vals)
        assert same_nodes(before, out)


def test_sorts_match_sorted_and_are_stable():
    rng = random.Random(3)
    for _ in range(300):
        for sort in (sort_list, sort_list_bottom_up, insertion_sort_list):
            head, vals = random_list(rng, rng.randint(0, 30), 0, 5)
            before = nodes(head)
            rank = {id(x): i for i, x in enumerate(before)}
            out = nodes(sort(head))
            assert [x.val for x in out] == sorted(vals), sort.__name__
            assert len(out) == len(before) and same_nodes(before, out[0] if out else None)
            keys = [(x.val, rank[id(x)]) for x in out]
            assert keys == sorted(keys), sort.__name__


def test_sort_large():
    rng = random.Random(4)
    head, vals = random_list(rng, 50_000, -10**6, 10**6)
    assert to_list(sort_list(head)) == sorted(vals)
    head = from_list(vals)
    assert to_list(sort_list_bottom_up(head)) == sorted(vals)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
