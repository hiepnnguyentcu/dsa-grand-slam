"""Binary trie — maximum XOR of two numbers, max XOR under a limit (offline).

Signs: "maximum XOR of a pair", "max XOR of x with some element", answers
       about XOR over a changing set, constraints like nums[i] < 2^31.
Approach: store each number as a path of its bits, most significant first.
          To maximise x XOR y, walk from the top bit and at each level take
          the child with the *opposite* bit of x if it exists — a 1 at a
          higher bit beats any combination of lower bits. Greedy is exact.
            - Max XOR pair: insert each number, then query it against the
              numbers already inserted.
            - Max XOR with element <= m (queries): sort numbers and queries by
              m; before each query insert every number <= m. Offline sort
              turns "only some elements count" into "elements so far".
Complexity: O(B) per insert / query, B = bit width (31 or 32). Pair O(n * B).
            Limit queries O((n + q) log + (n + q) * B). Space O(n * B) nodes.
Gotchas:
  - Fix the width B from the largest value (max(nums).bit_length()) or the
    problem bound; every number must use the same B or paths misalign.
  - Query an empty trie and you return garbage: answer -1 (or skip) when
    nothing has been inserted.
  - Keep the original query index when sorting queries offline.
  - Negative numbers: Python ints have no fixed width. Offset or mask to B
    bits first.
  - Need deletions (sliding window)? Store a count per node, decrement on
    remove, and treat count 0 as a missing child.

Run the tests at the bottom with:  python3 tries/bitwise_trie.py
"""

import random


# ---------------------------------------------------------------- implementation


class BitTrie:
    """Binary trie over B-bit non-negative ints, with removal counts."""

    def __init__(self, bits=31):
        self.bits = bits
        self.child = [[0, 0]]   # node 0 = root; 0 also means "no child"
        self.cnt = [0]

    def insert(self, x, delta=1):
        """Add x (delta=1) or remove one copy of x (delta=-1)."""
        v = 0
        self.cnt[0] += delta
        for b in range(self.bits - 1, -1, -1):
            bit = (x >> b) & 1
            if not self.child[v][bit]:
                self.child[v][bit] = len(self.child)
                self.child.append([0, 0])
                self.cnt.append(0)
            v = self.child[v][bit]
            self.cnt[v] += delta

    def max_xor(self, x):
        """max(x ^ y) over stored y, or -1 if the trie is empty."""
        if self.cnt[0] == 0:
            return -1
        v, out = 0, 0
        for b in range(self.bits - 1, -1, -1):
            want = 1 - ((x >> b) & 1)          # opposite bit sets this bit
            u = self.child[v][want]
            if u and self.cnt[u]:
                out |= 1 << b
                v = u
            else:
                v = self.child[v][1 - want]
        return out


def find_maximum_xor(nums):
    """max(a ^ b) over pairs (a may equal b, so 0 for a single number)."""
    t = BitTrie(max(max(nums).bit_length(), 1))
    best = 0
    for x in nums:
        t.insert(x)
        best = max(best, t.max_xor(x))
    return best


def maximize_xor(nums, queries):
    """queries[i] = (x, m): max(x ^ y) over nums y <= m, else -1."""
    top = max(nums + [x for x, _ in queries])
    t = BitTrie(max(top.bit_length(), 1))
    nums = sorted(nums)
    order = sorted(range(len(queries)), key=lambda i: queries[i][1])
    out, k = [-1] * len(queries), 0
    for i in order:
        x, m = queries[i]
        while k < len(nums) and nums[k] <= m:
            t.insert(nums[k])
            k += 1
        out[i] = t.max_xor(x)                  # -1 when nothing is <= m
    return out


# ------------------------------------------------------------------------ tests


def test_max_xor_classic():
    assert find_maximum_xor([3, 10, 5, 25, 2, 8]) == 28   # 5 ^ 25
    assert find_maximum_xor([14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70]) == 127
    assert find_maximum_xor([0]) == 0
    assert find_maximum_xor([7]) == 0


def test_max_xor_matches_brute_force():
    random.seed(13)
    for _ in range(200):
        nums = [random.randrange(1 << random.randint(1, 12)) for _ in range(random.randint(1, 20))]
        want = max(a ^ b for a in nums for b in nums)
        assert find_maximum_xor(nums) == want


def test_maximize_xor_classic():
    assert maximize_xor([0, 1, 2, 3, 4], [(3, 1), (1, 3), (5, 6)]) == [3, 3, 7]
    assert maximize_xor([5, 2, 4, 6, 6, 3], [(12, 4), (8, 1), (6, 3)]) == [15, -1, 5]


def test_maximize_xor_matches_brute_force():
    random.seed(14)
    for _ in range(200):
        nums = [random.randrange(64) for _ in range(random.randint(1, 15))]
        qs = [(random.randrange(64), random.randrange(64)) for _ in range(10)]
        want = [max((x ^ y for y in nums if y <= m), default=-1) for x, m in qs]
        assert maximize_xor(nums, qs) == want


def test_removal_counts_track_a_multiset():
    random.seed(15)
    t, bag = BitTrie(6), []
    for _ in range(2000):
        if bag and random.random() < 0.4:
            y = bag.pop(random.randrange(len(bag)))
            t.insert(y, -1)
        else:
            y = random.randrange(64)
            t.insert(y)
            bag.append(y)
        x = random.randrange(64)
        assert t.max_xor(x) == max((x ^ y for y in bag), default=-1)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
