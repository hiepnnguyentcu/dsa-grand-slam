"""Fast & slow pointers (Floyd) — cycles, middle node, k-th from the end.

Signs: linked list with O(1) space, "is there a cycle", "where does the
       cycle start", middle node, "remove the n-th node from the end",
       a function x -> f(x) that must eventually repeat (happy number),
       array values in 1..n used as next-pointers (find the duplicate).
Approach: slow moves 1 step, fast moves 2. In a cycle fast gains 1 per step,
          so they must meet. For the entry: reset one pointer to the head and
          move both 1 step; they meet at the entry. For the middle: when fast
          hits the end, slow is halfway. For k-th from end: give fast a k-step
          head start, then move both.
Complexity: O(n) time, O(1) space. A visited set does the same in O(n) space.
Gotchas:
  - Loop guard is `while fast and fast.next` — check both before fast.next.next.
  - Even length: this middle() returns the SECOND middle (LC 876). Start fast
    at head.next to get the first middle (needed to split for merge sort).
  - Why the entry trick works: if the head-to-entry distance is a and they
    meet m steps into the cycle of length c, then 2(a + m) = a + m + kc, so
    a = kc - m: walking a from the meeting point lands on the entry.
  - Remove n-th from end: use a dummy node so removing the head needs no
    special case.

Run the tests at the bottom with:  python3 sliding_window/fast_slow.py
"""


# ---------------------------------------------------------------- implementation


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build(values, pos=-1):
    """Linked list from values; tail links to index pos (-1 = no cycle)."""
    nodes = [ListNode(v) for v in values]
    for x, y in zip(nodes, nodes[1:]):
        x.next = y
    if nodes and pos >= 0:
        nodes[-1].next = nodes[pos]
    return (nodes[0] if nodes else None), nodes


def to_list(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def has_cycle(head):
    """LC 141."""
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False


def cycle_entry(head):
    """LC 142. The node where the cycle begins, or None."""
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            slow = head                 # a steps from head == a steps from here
            while slow is not fast:
                slow, fast = slow.next, fast.next
            return slow
    return None


def middle(head):
    """LC 876. Middle node; the second of two middles on even length."""
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow


def remove_nth_from_end(head, n):
    """LC 19. Remove the n-th node from the end (1 <= n <= length)."""
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n):
        fast = fast.next                # fast is n ahead
    while fast.next:
        slow, fast = slow.next, fast.next
    slow.next = slow.next.next          # slow sits just before the target
    return dummy.next


def is_happy(n):
    """LC 202. Repeated digit-square-sum reaches 1? Floyd on x -> f(x)."""

    def f(x):
        return sum(int(d) ** 2 for d in str(x))

    slow, fast = n, f(n)
    while fast != 1 and slow != fast:
        slow, fast = f(slow), f(f(fast))
    return fast == 1


def find_duplicate(a):
    """LC 287. a has n+1 values in 1..n: i -> a[i] is a list with a cycle
    whose entry is the duplicate. O(1) space, a is not modified."""
    slow = fast = a[0]
    while True:
        slow, fast = a[slow], a[a[fast]]
        if slow == fast:
            break
    slow = a[0]
    while slow != fast:
        slow, fast = a[slow], a[fast]
    return slow


# ------------------------------------------------------------------------ tests


def test_examples():
    head, nodes = build([3, 2, 0, -4], pos=1)
    assert has_cycle(head) and cycle_entry(head) is nodes[1]
    head, _ = build([1, 2, 3, 4, 5])
    assert middle(head).val == 3
    assert to_list(remove_nth_from_end(head, 2)) == [1, 2, 3, 5]
    assert is_happy(19) and not is_happy(2)
    assert find_duplicate([1, 3, 4, 2, 2]) == 2


def test_cycle_matches_visited_set():
    import random

    rng = random.Random(1)
    for _ in range(500):
        n = rng.randint(0, 12)
        pos = rng.randint(-1, n - 1) if n else -1
        head, nodes = build(list(range(n)), pos)
        seen, cur, entry = set(), head, None  # reference: first repeated node
        while cur:
            if id(cur) in seen:
                entry = cur
                break
            seen.add(id(cur))
            cur = cur.next
        assert has_cycle(head) == (entry is not None)
        assert cycle_entry(head) is entry
        assert entry is (nodes[pos] if pos >= 0 else None)


def test_middle_and_remove_match_list_ops():
    import random

    rng = random.Random(2)
    for _ in range(300):
        vals = [rng.randint(0, 9) for _ in range(rng.randint(1, 12))]
        head, _ = build(vals)
        assert middle(head).val == vals[len(vals) // 2]
        k = rng.randint(1, len(vals))
        assert to_list(remove_nth_from_end(head, k)) == vals[:len(vals) - k] + vals[len(vals) - k + 1:]


def test_happy_matches_visited_set():
    def happy_set(n):
        seen = set()
        while n != 1 and n not in seen:
            seen.add(n)
            n = sum(int(d) ** 2 for d in str(n))
        return n == 1

    for n in range(1, 500):
        assert is_happy(n) == happy_set(n)


def test_find_duplicate_matches_counter():
    import random
    from collections import Counter

    rng = random.Random(3)
    for _ in range(300):
        n = rng.randint(1, 12)
        dup = rng.randint(1, n)
        c = rng.randint(2, n + 1)                 # copies of the duplicate
        others = [v for v in range(1, n + 1) if v != dup]
        a = [dup] * c + rng.sample(others, n + 1 - c)
        rng.shuffle(a)
        assert len(a) == n + 1
        assert find_duplicate(a) == Counter(a).most_common(1)[0][0]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
