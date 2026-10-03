"""Bitwise over subarrays — XOR triplets via prefix XOR, distinct ORs, decode XOR.

Signs: "count triplets i < j <= k with a[i..j-1] XOR == a[j..k] XOR", "number
       of distinct OR (or AND) values over all subarrays", "smallest subarray
       with maximum OR", "decode an array from adjacent XORs".
Approach:
  - XOR-equal triplets: xor(a[i..j-1]) == xor(a[j..k]) means
    xor(a[i..k]) == 0, i.e. px[i] == px[k + 1]. Every j in (i, k] works, so
    a matching prefix pair (i, k + 1) adds k - i triplets. Group equal prefix
    values in a hashmap: keep count and sum of indices seen. O(n).
  - Subarray ORs: ORs ending at index i only ever gain bits as the start moves
    left, so there are at most ~30 distinct values. Carry that set forward:
    cur = {x | a[i] for x in cur} | {a[i]}. AND works the same (bits only lost).
  - Decode XORed array (encoded[i] = a[i] ^ a[i+1], a[0] given): prefix XOR.
  - Decode XORed permutation (perm of 1..n, n odd): XOR of 1..n is known;
    XOR of encoded[1], encoded[3], ... is everything but perm[0].
  - Subarray XOR == k counting: prefix_sums/prefix_hashmap.py
    (xor_subarray_count). Range XOR queries: prefix_sums/prefix_ops.py.
Complexity: triplets O(n); distinct ORs O(n * 30); decodes O(n).
Gotchas:
  - Triplets: the answer counts j too, so a zero-XOR range [i..k] of length L
    contributes L - 1, not 1.
  - Distinct ORs: do not rebuild every subarray, O(n^2) on n = 5 * 10^4.
  - Decode permutation relies on n odd: pairs (encoded[1], encoded[3], ...)
    cover perm[1..n-1] exactly.

Run the tests at the bottom with:  python3 bit_manipulation/subarray_bitwise.py
"""

import random
from functools import reduce
from operator import or_, xor


# ---------------------------------------------------------------- implementation


def count_triplets(a):
    """Triplets i < j <= k with xor(a[i..j-1]) == xor(a[j..k]) (LeetCode 1442)."""
    count = {0: 1}  # prefix value -> how many prefix indices had it
    index_sum = {0: 0}  # prefix value -> sum of those indices
    px = 0
    total = 0
    for k, x in enumerate(a):
        px ^= x  # px is the prefix XOR at index k + 1
        c, s = count.get(px, 0), index_sum.get(px, 0)
        total += c * k - s  # sum over earlier i with px[i] == px of (k - i)
        count[px] = c + 1
        index_sum[px] = s + k + 1
    return total


def subarray_bitwise_ors(a):
    """Number of distinct values of OR over all non-empty subarrays (LeetCode 898)."""
    seen = set()
    cur = set()
    for x in a:
        cur = {y | x for y in cur} | {x}
        seen |= cur
    return len(seen)


def decode_xored(encoded, first):
    """encoded[i] = a[i] ^ a[i + 1]; rebuild a (LeetCode 1720)."""
    out = [first]
    for e in encoded:
        out.append(out[-1] ^ e)
    return out


def decode_permutation(encoded):
    """perm of 1..n, n = len(encoded) + 1 odd, encoded[i] = perm[i] ^ perm[i+1] (LeetCode 1734)."""
    n = len(encoded) + 1
    total = reduce(xor, range(1, n + 1), 0)
    rest = reduce(xor, encoded[1::2], 0)  # perm[1] ^ perm[2] ^ ... ^ perm[n-1]
    return decode_xored(encoded, total ^ rest)


# ------------------------------------------------------------------------ tests


def test_count_triplets_against_brute_force():
    rng = random.Random(50)
    for _ in range(300):
        a = [rng.randint(1, 8) for _ in range(rng.randint(1, 25))]
        n = len(a)
        brute = 0
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j, n):
                    if reduce(xor, a[i:j]) == reduce(xor, a[j:k + 1]):
                        brute += 1
        assert count_triplets(a) == brute
    assert count_triplets([2, 3, 1, 6, 7]) == 4
    assert count_triplets([1, 1, 1, 1, 1]) == 10


def test_subarray_ors_against_brute_force():
    rng = random.Random(51)
    for _ in range(300):
        a = [rng.randrange(64) for _ in range(rng.randint(1, 30))]
        brute = {reduce(or_, a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1)}
        assert subarray_bitwise_ors(a) == len(brute)


def test_or_set_stays_small():
    rng = random.Random(52)
    a = [rng.randrange(2**30) for _ in range(3000)]
    cur, biggest = set(), 0
    for x in a:
        cur = {y | x for y in cur} | {x}
        biggest = max(biggest, len(cur))
    assert biggest <= 31  # each step down the chain adds at least one bit


def test_decode_round_trips():
    rng = random.Random(53)
    for _ in range(300):
        a = [rng.randrange(10**5) for _ in range(rng.randint(1, 20))]
        enc = [x ^ y for x, y in zip(a, a[1:])]
        assert decode_xored(enc, a[0]) == a
    for n in range(1, 40, 2):
        perm = list(range(1, n + 1))
        rng.shuffle(perm)
        enc = [x ^ y for x, y in zip(perm, perm[1:])]
        assert decode_permutation(enc) == perm


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
