"""Reversal — flip next pointers, whole list or a segment at a time.

Signs: "reverse the list", "reverse positions m..n", "reverse every k nodes",
       "swap adjacent pairs", palindrome check in O(1) space, anything that
       needs to walk the list backwards without a stack.
Approach: three pointers. prev = None, cur = head; each step save nxt =
          cur.next, point cur.next = prev, then shift prev = cur, cur = nxt.
          When cur is None, prev is the new head.
          Segment reversal: stand on the node *before* the segment (a dummy
          if the segment starts at the head), reverse the segment, then stitch
          both ends back. k-groups repeat that, first checking that k nodes
          remain. Palindrome: find the middle (fast/slow), reverse the second
          half, compare, reverse it back.
Complexity: O(n) time, O(1) space iterative; recursive reverse is O(n) stack.
Gotchas:
  - Save cur.next before overwriting it — that is the whole bug surface.
  - In reverse_between the segment's first node becomes its last; keep a
    handle on it to reconnect to whatever followed.
  - k-group leaves a final short group as-is; count before reversing.
  - Recursive reverse dies around 1000 nodes in Python — interview-fine,
    production-wrong. Mention it.
  - Palindrome: restore the list if the caller still owns it.

Run the tests at the bottom with:  python3 linked_lists/reversal.py
"""

import random

from ll import ListNode, from_list, nodes, random_list, same_nodes, to_list


# ---------------------------------------------------------------- implementation


def reverse(head):
    """LC 206, iterative."""
    prev, cur = None, head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
    return prev


def reverse_recursive(head):
    """LC 206, recursive: reverse the rest, then hang head after its old next."""
    if head is None or head.next is None:
        return head
    new_head = reverse_recursive(head.next)
    head.next.next = head               # old next is now the tail of the rest
    head.next = None
    return new_head


def reverse_between(head, left, right):
    """LC 92. Reverse positions left..right (1-indexed, inclusive)."""
    dummy = ListNode(0, head)
    before = dummy
    for _ in range(left - 1):
        before = before.next
    seg_first = before.next             # becomes the segment's last node
    prev, cur = None, seg_first
    for _ in range(right - left + 1):
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
    before.next = prev                  # new segment head
    seg_first.next = cur                # whatever followed the segment
    return dummy.next


def reverse_k_group(head, k):
    """LC 25. Reverse each full block of k nodes; a short tail stays put."""
    dummy = ListNode(0, head)
    before = dummy
    while True:
        probe = before
        for _ in range(k):
            probe = probe.next
            if probe is None:
                return dummy.next
        seg_first = before.next
        prev, cur = None, seg_first
        for _ in range(k):
            nxt = cur.next
            cur.next = prev
            prev, cur = cur, nxt
        before.next = prev
        seg_first.next = cur
        before = seg_first


def swap_pairs(head):
    """LC 24. Swap every two adjacent nodes (k-group with k = 2, spelled out)."""
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next and prev.next.next:
        a, b = prev.next, prev.next.next
        a.next = b.next
        b.next = a
        prev.next = b
        prev = a
    return dummy.next


def is_palindrome(head):
    """LC 234. O(1) space: reverse the second half, compare, restore."""
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    tail = reverse(slow)                # odd length: middle sits in this half, harmless
    ok, a, b = True, head, tail
    while b:
        if a.val != b.val:
            ok = False
            break
        a, b = a.next, b.next
    reverse(tail)                       # put it back
    return ok


# ------------------------------------------------------------------------ tests


def test_examples():
    assert to_list(reverse(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    assert reverse(None) is None
    assert to_list(reverse_between(from_list([1, 2, 3, 4, 5]), 2, 4)) == [1, 4, 3, 2, 5]
    assert to_list(reverse_k_group(from_list([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
    assert to_list(reverse_k_group(from_list([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
    assert to_list(swap_pairs(from_list([1, 2, 3, 4]))) == [2, 1, 4, 3]
    assert is_palindrome(from_list([1, 2, 2, 1])) and not is_palindrome(from_list([1, 2]))


def test_reverse_matches_slicing_and_reuses_nodes():
    rng = random.Random(1)
    for _ in range(300):
        head, vals = random_list(rng, rng.randint(0, 20))
        before = nodes(head)
        out = reverse(head)
        assert to_list(out) == vals[::-1] and same_nodes(before, out)
        out = reverse_recursive(out)
        assert to_list(out) == vals and same_nodes(before, out)


def test_reverse_between_matches_slicing():
    rng = random.Random(2)
    for _ in range(500):
        head, vals = random_list(rng, rng.randint(1, 15))
        before = nodes(head)
        l = rng.randint(1, len(vals))
        r = rng.randint(l, len(vals))
        out = reverse_between(head, l, r)
        assert to_list(out) == vals[:l - 1] + vals[l - 1:r][::-1] + vals[r:]
        assert same_nodes(before, out)


def test_k_group_and_swap_pairs_match_slicing():
    def ref(vals, k):
        out = []
        for i in range(0, len(vals), k):
            block = vals[i:i + k]
            out += block[::-1] if len(block) == k else block
        return out

    rng = random.Random(3)
    for _ in range(500):
        head, vals = random_list(rng, rng.randint(0, 20))
        before = nodes(head)
        k = rng.randint(1, 6)
        out = reverse_k_group(head, k)
        assert to_list(out) == ref(vals, k) and same_nodes(before, out)

        head = from_list(vals)
        before = nodes(head)
        out = swap_pairs(head)
        assert to_list(out) == ref(vals, 2) and same_nodes(before, out)


def test_palindrome_matches_slicing_and_restores_list():
    rng = random.Random(4)
    for _ in range(500):
        half = [rng.randint(0, 2) for _ in range(rng.randint(0, 6))]
        vals = half + [rng.randint(0, 2)] * rng.randint(0, 1) + half[::-1]
        if rng.random() < 0.5:
            vals = [rng.randint(0, 2) for _ in range(rng.randint(0, 10))]
        head = from_list(vals)
        before = nodes(head)
        assert is_palindrome(head) == (vals == vals[::-1])
        assert nodes(head) == before    # same nodes, same order, afterwards


def test_iterative_handles_long_lists():
    head = from_list(list(range(100_000)))
    assert to_list(reverse(head))[:3] == [99_999, 99_998, 99_997]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
