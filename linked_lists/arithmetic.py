"""Arithmetic on digit lists — add, plus one, double, with a carry.

Signs: "numbers stored as linked lists of digits", "add two numbers",
       "plus one", "double the number", inputs too long for an int in other
       languages.
Approach: reverse order (least significant first, LC 2): walk both lists
          together with a carry; keep going while either list or the carry
          is left — that one condition handles unequal lengths and a final
          carry. Forward order (LC 445): push digits onto two stacks (or
          reverse both lists), add from the top, and prepend each new node.
          Plus one / double in forward order without reversing: the carry
          into a digit only depends on what is to its right, so remember the
          last digit that can absorb a carry (not 9 for +1, < 5 for doubling)
          and fix up from there.
Complexity: O(n + m) time; stacks are O(n + m) space, the in-place tricks O(1).
Gotchas:
  - `while a or b or carry` — forgetting the carry drops the leading 1 of
    999 + 1.
  - Prepending builds forward order for free: node = ListNode(d, node).
  - Plus one on all 9s needs a new head; a dummy 0 in front makes that the
    same case as the others — strip it if it stayed 0.
  - Doubling: digit d produces a carry iff d >= 5, so each node's new value is
    2d % 10 + (next digit >= 5). One pass, no reverse.

Run the tests at the bottom with:  python3 linked_lists/arithmetic.py
"""

import random

from ll import ListNode, from_list, nodes, subset_nodes, to_list


# ---------------------------------------------------------------- implementation


def add_two_numbers(a, b):
    """LC 2. Digits stored least-significant first."""
    dummy = tail = ListNode(0)
    carry = 0
    while a or b or carry:
        s = carry + (a.val if a else 0) + (b.val if b else 0)
        carry, d = divmod(s, 10)
        tail.next = tail = ListNode(d)
        a = a.next if a else None
        b = b.next if b else None
    return dummy.next


def add_two_numbers_ii(a, b):
    """LC 445. Digits stored most-significant first; inputs left untouched."""
    sa, sb = [], []
    while a:
        sa.append(a.val)
        a = a.next
    while b:
        sb.append(b.val)
        b = b.next
    head, carry = None, 0
    while sa or sb or carry:
        s = carry + (sa.pop() if sa else 0) + (sb.pop() if sb else 0)
        carry, d = divmod(s, 10)
        head = ListNode(d, head)        # prepend: builds forward order
    return head


def plus_one(head):
    """LC 369. Forward order. The last non-9 digit absorbs the carry."""
    dummy = ListNode(0, head)
    not_nine = dummy
    cur = head
    while cur:
        if cur.val != 9:
            not_nine = cur
        cur = cur.next
    not_nine.val += 1
    cur = not_nine.next
    while cur:                          # everything after it was a 9
        cur.val = 0
        cur = cur.next
    return dummy if dummy.val else dummy.next


def double_it(head):
    """LC 2816. Forward order. New digit = 2d % 10 + (next digit >= 5)."""
    if head.val >= 5:
        head = ListNode(0, head)        # the carry out of the top digit
    cur = head
    while cur:
        cur.val = cur.val * 2 % 10 + (1 if cur.next and cur.next.val >= 5 else 0)
        cur = cur.next
    return head


# ------------------------------------------------------------------------ tests


def digits_lsb(n):
    return [int(c) for c in str(n)[::-1]]


def digits_msb(n):
    return [int(c) for c in str(n)]


def test_examples():
    assert to_list(add_two_numbers(from_list([2, 4, 3]), from_list([5, 6, 4]))) == [7, 0, 8]
    assert to_list(add_two_numbers(from_list([9, 9]), from_list([1]))) == [0, 0, 1]
    assert to_list(add_two_numbers_ii(from_list([7, 2, 4, 3]), from_list([5, 6, 4]))) == [7, 8, 0, 7]
    assert to_list(plus_one(from_list([1, 2, 9]))) == [1, 3, 0]
    assert to_list(plus_one(from_list([9, 9]))) == [1, 0, 0]
    assert to_list(double_it(from_list([1, 8, 9]))) == [3, 7, 8]
    assert to_list(double_it(from_list([9, 9, 9]))) == [1, 9, 9, 8]


def random_number(rng):
    return rng.choice([0, rng.randint(0, 99), 10 ** rng.randint(1, 30) - 1,
                       rng.randint(0, 10 ** rng.randint(1, 30))])


def test_add_matches_python_ints():
    rng = random.Random(1)
    for _ in range(1000):
        x, y = random_number(rng), random_number(rng)
        a, b = from_list(digits_lsb(x)), from_list(digits_lsb(y))
        assert to_list(add_two_numbers(a, b)) == digits_lsb(x + y)
        a, b = from_list(digits_msb(x)), from_list(digits_msb(y))
        assert to_list(add_two_numbers_ii(a, b)) == digits_msb(x + y)
        assert to_list(a) == digits_msb(x) and to_list(b) == digits_msb(y)  # untouched


def test_plus_one_and_double_match_python_ints():
    rng = random.Random(2)
    for _ in range(1000):
        x = random_number(rng)
        head = from_list(digits_msb(x))
        before = nodes(head)
        out = plus_one(head)
        assert to_list(out) == digits_msb(x + 1)
        # in place: at most one new node (the leading 1 of 99..9 + 1)
        assert subset_nodes(before, out if len(str(x + 1)) == len(str(x)) else out.next)

        head = from_list(digits_msb(x))
        before = nodes(head)
        out = double_it(head)
        assert to_list(out) == digits_msb(2 * x)
        assert subset_nodes(before, out if len(str(2 * x)) == len(str(x)) else out.next)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
