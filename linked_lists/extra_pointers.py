"""Extra pointers — deep copy with random pointers; flatten child pointers.

Signs: nodes carry a second pointer besides next (random, child, prev);
       "return a deep copy", "flatten the multilevel list", "no node of the
       copy may point into the original".
Approach: copy random list, hashmap: first pass maps old -> new for every
          node, second pass wires new.next = map[old.next] and new.random =
          map[old.random]. Interleave, O(1) extra space: insert each copy
          right after its original (A -> A' -> B -> B'), then
          A'.random = A.random.next, then unzip the two lists.
          Flatten multilevel doubly linked list: walk with cur; when cur has
          a child, find the child chain's tail, splice the chain between cur
          and cur.next, clear child. Keep walking — the spliced chain is now
          ahead of cur, so deeper levels get flattened in turn.
Complexity: copy O(n) time, O(n) map or O(1) interleave; flatten O(n) time,
            O(1) space (each node is passed by the tail scan at most once
            per level, total O(n)).
Gotchas:
  - random may be None — map[None] must be None (or guard it).
  - Interleave: set ALL random pointers before unzipping; unzipping first
    breaks the A.random.next trick. Restore the original's next pointers.
  - Flatten: set child = None and fix every prev pointer, including the
    old next's prev to the chain tail. Tests usually check both directions.
  - Same map-of-copies idea as graphs/clone_graph.py.

Run the tests at the bottom with:  python3 linked_lists/extra_pointers.py
"""

import random


# ---------------------------------------------------------------- implementation


class RandomNode:
    __slots__ = ("val", "next", "random")

    def __init__(self, val, next=None, random=None):
        self.val, self.next, self.random = val, next, random


class MultiNode:
    __slots__ = ("val", "prev", "next", "child")

    def __init__(self, val, prev=None, next=None, child=None):
        self.val, self.prev, self.next, self.child = val, prev, next, child


def copy_random_list(head):
    """LC 138, hashmap."""
    copy = {None: None}
    cur = head
    while cur:
        copy[cur] = RandomNode(cur.val)
        cur = cur.next
    cur = head
    while cur:
        copy[cur].next = copy[cur.next]
        copy[cur].random = copy[cur.random]
        cur = cur.next
    return copy[head]


def copy_random_list_interleave(head):
    """LC 138, O(1) extra space: weave copies in, set randoms, unweave."""
    cur = head
    while cur:                          # A -> A' -> B -> B'
        cur.next = RandomNode(cur.val, cur.next)
        cur = cur.next.next
    cur = head
    while cur:
        if cur.random:
            cur.next.random = cur.random.next
        cur = cur.next.next
    dummy = tail = RandomNode(0)
    cur = head
    while cur:                          # unweave, restoring the original
        c = cur.next
        cur.next = c.next
        tail.next = tail = c
        cur = cur.next
    return dummy.next


def flatten(head):
    """LC 430. Child chains are spliced in right after their parent."""
    cur = head
    while cur:
        if cur.child:
            child, after = cur.child, cur.next
            tail = child
            while tail.next:
                tail = tail.next
            cur.next, child.prev, cur.child = child, cur, None
            tail.next = after
            if after:
                after.prev = tail
        cur = cur.next
    return head


# ------------------------------------------------------------------------ tests


def build_random(vals, rand_idx):
    """RandomNode list; rand_idx[i] is the index node i's random points to, or None."""
    ns = [RandomNode(v) for v in vals]
    for x, y in zip(ns, ns[1:]):
        x.next = y
    for n, r in zip(ns, rand_idx):
        n.random = ns[r] if r is not None else None
    return (ns[0] if ns else None), ns


def encode_random(head):
    """(values, random indices) — structure without object identity."""
    ns = []
    while head:
        ns.append(head)
        head = head.next
    idx = {id(n): i for i, n in enumerate(ns)}
    return [n.val for n in ns], [idx[id(n.random)] if n.random else None for n in ns], ns


def test_copy_random_examples():
    head, _ = build_random([7, 13, 11, 10, 1], [None, 0, 4, 2, 0])
    for copy in (copy_random_list, copy_random_list_interleave):
        assert encode_random(copy(head))[:2] == ([7, 13, 11, 10, 1], [None, 0, 4, 2, 0])
        assert copy(None) is None


def test_copy_random_is_deep_and_original_untouched():
    rng = random.Random(1)
    for _ in range(300):
        n = rng.randint(0, 15)
        vals = [rng.randint(0, 3) for _ in range(n)]          # repeats: identity matters
        rand = [rng.choice([None] + list(range(n))) for _ in range(n)]
        for copy in (copy_random_list, copy_random_list_interleave):
            head, orig = build_random(vals, rand)
            out_vals, out_rand, out_nodes = encode_random(copy(head))
            assert (out_vals, out_rand) == (vals, rand)
            old = {id(x) for x in orig}
            assert not any(id(x) in old for x in out_nodes)
            assert not any(x.random is not None and id(x.random) in old for x in out_nodes)
            v2, r2, n2 = encode_random(head)                   # original restored
            assert (v2, r2) == (vals, rand) and [id(x) for x in n2] == [id(x) for x in orig]


def build_multi(spec):
    """spec = [(val, child_spec or None), ...] nested; returns head."""
    head = prev = None
    for val, child in spec:
        node = MultiNode(val, prev)
        if prev:
            prev.next = node
        else:
            head = node
        node.child = build_multi(child) if child else None
        prev = node
    return head


def preorder(spec):
    """Reference flatten: depth-first, parent before child before next."""
    out = []
    for val, child in spec:
        out.append(val)
        if child:
            out += preorder(child)
    return out


def check_doubly(head):
    vals, prev = [], None
    while head:
        assert head.prev is prev and head.child is None
        vals.append(head.val)
        prev, head = head, head.next
    return vals


def random_spec(rng, budget, depth=0):
    spec = []
    for _ in range(rng.randint(1, 4)):
        if budget[0] <= 0:
            break
        budget[0] -= 1
        child = random_spec(rng, budget, depth + 1) if depth < 4 and rng.random() < 0.3 else None
        spec.append((budget[0], child or None))
    return spec


def test_flatten_example():
    spec = [(1, None), (2, None), (3, [(7, None), (8, [(11, None), (12, None)]), (9, None)]),
            (4, None), (5, None), (6, None)]
    assert check_doubly(flatten(build_multi(spec))) == [1, 2, 3, 7, 8, 11, 12, 9, 4, 5, 6]
    assert flatten(None) is None


def test_flatten_matches_preorder_and_fixes_prev():
    rng = random.Random(2)
    for _ in range(300):
        spec = random_spec(rng, [rng.randint(1, 25)])
        head = build_multi(spec)
        assert check_doubly(flatten(head)) == preorder(spec)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
