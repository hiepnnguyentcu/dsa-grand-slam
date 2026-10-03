"""Reordering — rearrange nodes by position: interleave, rotate, split.

Signs: "reorder to L0 -> Ln -> L1 -> Ln-1 ...", "odd positions then even
       positions", "rotate right by k", "split into k parts as equal as
       possible", any reshuffle defined by index, not by value.
Approach: these are compositions of three primitives — find the middle,
          reverse, and walk two chains in lockstep.
          Reorder: middle (first middle), cut, reverse the second half,
          zip the halves. Odd-even: two tails advancing two steps each, then
          odd_tail.next = even_head. Rotate: one pass for length and tail,
          k %= n, close into a ring, cut at n - k. Split: q, r = divmod(n, k);
          the first r parts get q + 1 nodes, cut after each part.
Complexity: O(n) time, O(1) extra space (split returns a k-slot list).
Gotchas:
  - Reorder must split at the FIRST middle (fast starts at head.next) and cut
    slow.next = None, or the first half runs into the reversed second half.
  - Odd-even is by position, not value. Loop guard: `while even and
    even.next`.
  - Rotate: k can be far bigger than n — always k %= n, and return early on
    an empty list (n = 0 would divide by zero).
  - Split: k > n gives trailing None parts; they still count.

Run the tests at the bottom with:  python3 linked_lists/reordering.py
"""

import random

from ll import from_list, nodes, random_list, same_nodes, to_list


# ---------------------------------------------------------------- implementation


def reorder_list(head):
    """LC 143. L0 -> Ln -> L1 -> Ln-1 -> ... in place. Returns head."""
    if not head or not head.next:
        return head
    slow, fast = head, head.next        # slow ends on the first middle
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    second, slow.next = slow.next, None
    prev = None
    while second:                       # reverse second half
        second.next, prev, second = prev, second, second.next
    a, b = head, prev
    while b:                            # zip: second half is never longer
        a_next, b_next = a.next, b.next
        a.next, b.next = b, a_next
        a, b = a_next, b_next
    return head


def odd_even_list(head):
    """LC 328. Nodes at odd positions, then even positions, order kept."""
    if not head:
        return head
    odd, even = head, head.next
    even_head = even
    while even and even.next:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = even_head
    return head


def rotate_right(head, k):
    """LC 61. Move the last k nodes to the front."""
    if not head:
        return head
    n, tail = 1, head
    while tail.next:
        n, tail = n + 1, tail.next
    k %= n
    if k == 0:
        return head
    tail.next = head                    # ring
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next
    new_head, new_tail.next = new_tail.next, None
    return new_head


def split_list_to_parts(head, k):
    """LC 725. k consecutive parts, sizes differ by at most 1, bigger first."""
    n, cur = 0, head
    while cur:
        n, cur = n + 1, cur.next
    q, r = divmod(n, k)
    parts, cur = [], head
    for i in range(k):
        parts.append(cur)
        for _ in range(q + (i < r) - 1):
            cur = cur.next
        if cur:
            cur.next, cur = None, cur.next
    return parts


# ------------------------------------------------------------------------ tests


def test_examples():
    assert to_list(reorder_list(from_list([1, 2, 3, 4, 5]))) == [1, 5, 2, 4, 3]
    assert to_list(odd_even_list(from_list([2, 1, 3, 5, 6, 4, 7]))) == [2, 3, 6, 7, 1, 5, 4]
    assert to_list(rotate_right(from_list([1, 2, 3, 4, 5]), 2)) == [4, 5, 1, 2, 3]
    parts = split_list_to_parts(from_list(list(range(1, 11))), 3)
    assert [to_list(p) for p in parts] == [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10]]
    assert [to_list(p) for p in split_list_to_parts(from_list([1, 2]), 4)] == [[1], [2], [], []]


def test_reorder_matches_index_reference():
    rng = random.Random(1)
    for _ in range(500):
        n = rng.randint(0, 20)
        head, vals = from_list(list(range(n))), list(range(n))
        before = nodes(head)
        expect, i, j = [], 0, n - 1
        while i <= j:
            expect.append(vals[i])
            if i != j:
                expect.append(vals[j])
            i, j = i + 1, j - 1
        out = reorder_list(head)
        assert to_list(out) == expect and same_nodes(before, out)


def test_odd_even_matches_slicing():
    rng = random.Random(2)
    for _ in range(500):
        head, vals = random_list(rng, rng.randint(0, 20))
        before = nodes(head)
        out = odd_even_list(head)
        assert to_list(out) == vals[0::2] + vals[1::2] and same_nodes(before, out)


def test_rotate_matches_slicing():
    rng = random.Random(3)
    for _ in range(500):
        head, vals = random_list(rng, rng.randint(0, 15))
        before = nodes(head)
        k = rng.randint(0, 50)
        out = rotate_right(head, k)
        s = k % len(vals) if vals else 0
        assert to_list(out) == (vals[-s:] + vals[:-s] if s else vals)
        assert same_nodes(before, out)


def test_split_matches_slicing():
    rng = random.Random(4)
    for _ in range(500):
        head, vals = random_list(rng, rng.randint(0, 25))
        before = nodes(head)
        k = rng.randint(1, 8)
        parts = split_list_to_parts(head, k)
        q, r = divmod(len(vals), k)
        expect, i = [], 0
        for p in range(k):
            size = q + (p < r)
            expect.append(vals[i:i + size])
            i += size
        assert [to_list(p) for p in parts] == expect
        assert [id(x) for p in parts for x in nodes(p)] == [id(x) for x in before]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
