"""Prefix sum + hashmap — count or find subarrays whose sum hits a target.

Signs: "number of subarrays with sum k", "longest subarray with sum k",
       equal 0s and 1s, "sum divisible by k", negatives allowed (so a sliding
       window does not work).
Approach: sum(a[i..j]) = p[j + 1] - p[i]. Walking j left to right, a subarray
          ending at j has sum k iff some earlier prefix equals p - k. Keep a
          map of earlier prefixes:
            count    -> {prefix: how many times seen}
            longest  -> {prefix: first index seen}
            mod k    -> key by p % k; equal remainders = divisible difference.
Complexity: O(n) time, O(n) space.
Gotchas:
  - Seed the map: {0: 1} for counting, {0: -1} for longest. Without it,
    subarrays starting at index 0 are missed.
  - Look up p - k BEFORE inserting p, or k == 0 counts empty subarrays.
  - Longest: store only the FIRST index of each prefix. Never overwrite.
  - Python's % is never negative; in Java/C++ use ((p % k) + k) % k.
  - Reframe to reuse: 0/1 balance -> map 0 to -1, target 0. "k odd numbers"
    -> map odd to 1, even to 0, target k.
  - Non-negative values and "at most / at least" -> sliding window is simpler.
  - Shortest subarray with sum >= k, negatives allowed: prefix sums plus a
    monotonic deque (stacks_heaps/monotonic_deque.py).
  - Same trick on root-to-node paths: binary_trees/path_prefix_sum.py.

Run the tests at the bottom with:  python3 prefix_sums/prefix_hashmap.py
"""

import random
from collections import defaultdict


# ---------------------------------------------------------------- implementation


def subarray_sum_count(a, k):
    """Number of non-empty subarrays with sum exactly k."""
    seen = defaultdict(int)
    seen[0] = 1
    p = count = 0
    for x in a:
        p += x
        count += seen[p - k]
        seen[p] += 1
    return count


def longest_subarray_sum(a, k):
    """Length of the longest subarray with sum exactly k, or 0."""
    first = {0: -1}
    p = best = 0
    for j, x in enumerate(a):
        p += x
        if p - k in first:
            best = max(best, j - first[p - k])
        first.setdefault(p, j)              # keep the earliest index only
    return best


def find_max_length(bits):
    """Contiguous Array: longest subarray with equal 0s and 1s."""
    return longest_subarray_sum([1 if b else -1 for b in bits], 0)


def subarrays_div_by_k(a, k):
    """Number of non-empty subarrays whose sum is divisible by k."""
    seen = defaultdict(int)
    seen[0] = 1
    p = count = 0
    for x in a:
        p = (p + x) % k
        count += seen[p]
        seen[p] += 1
    return count


def check_subarray_sum(a, k):
    """Continuous Subarray Sum: is there a subarray of length >= 2 with sum % k == 0?

    Store the first index of each remainder; a repeat at least two positions
    later is the answer.
    """
    first = {0: -1}
    p = 0
    for j, x in enumerate(a):
        p = (p + x) % k
        if p in first:
            if j - first[p] >= 2:
                return True
        else:
            first[p] = j
    return False


def nice_subarrays(a, k):
    """Subarrays containing exactly k odd numbers."""
    return subarray_sum_count([x % 2 for x in a], k)


def xor_subarray_count(a, k):
    """Subarrays whose XOR is exactly k (same idea, ^ instead of -)."""
    seen = defaultdict(int)
    seen[0] = 1
    px = count = 0
    for x in a:
        px ^= x
        count += seen[px ^ k]
        seen[px] += 1
    return count


def min_subarray_to_remove(a, p):
    """Shortest subarray to remove so the rest sums to a multiple of p; -1 if
    only removing everything works.

    Need a subarray with sum % p == total % p. Keep the LAST index of each
    remainder (we want the shortest, so the latest start).
    """
    need = sum(a) % p
    if need == 0:
        return 0
    last = {0: -1}
    cur, best = 0, len(a)
    for j, x in enumerate(a):
        cur = (cur + x) % p
        want = (cur - need) % p
        if want in last:
            best = min(best, j - last[want])
        last[cur] = j
    return best if best < len(a) else -1


# ----------------------------------------------------------------- brute force


def _subarrays(a):
    for i in range(len(a)):
        for j in range(i, len(a)):
            yield i, j, a[i:j + 1]


# ------------------------------------------------------------------------ tests


def test_subarray_sum_count_examples():
    assert subarray_sum_count([1, 1, 1], 2) == 2
    assert subarray_sum_count([1, 2, 3], 3) == 2
    assert subarray_sum_count([1, -1, 0], 0) == 3   # [1,-1], [0], [1,-1,0]
    assert subarray_sum_count([], 0) == 0


def test_subarray_sum_count_matches_brute_force():
    random.seed(21)
    for _ in range(300):
        a = [random.randint(-4, 4) for _ in range(random.randint(0, 12))]
        k = random.randint(-5, 5)
        assert subarray_sum_count(a, k) == sum(sum(s) == k for _, _, s in _subarrays(a))


def test_longest_subarray_sum_matches_brute_force():
    random.seed(22)
    assert longest_subarray_sum([1, -1, 5, -2, 3], 3) == 4
    assert longest_subarray_sum([-2, -1, 2, 1], 1) == 2
    for _ in range(300):
        a = [random.randint(-4, 4) for _ in range(random.randint(0, 12))]
        k = random.randint(-5, 5)
        want = max((j - i + 1 for i, j, s in _subarrays(a) if sum(s) == k), default=0)
        assert longest_subarray_sum(a, k) == want


def test_find_max_length_matches_brute_force():
    random.seed(23)
    assert find_max_length([0, 1, 0]) == 2
    for _ in range(300):
        b = [random.randint(0, 1) for _ in range(random.randint(0, 14))]
        want = max((j - i + 1 for i, j, s in _subarrays(b) if 2 * sum(s) == len(s)), default=0)
        assert find_max_length(b) == want


def test_subarrays_div_by_k_matches_brute_force():
    random.seed(24)
    assert subarrays_div_by_k([4, 5, 0, -2, -3, 1], 5) == 7
    for _ in range(300):
        a = [random.randint(-9, 9) for _ in range(random.randint(0, 12))]
        k = random.randint(1, 6)
        assert subarrays_div_by_k(a, k) == sum(sum(s) % k == 0 for _, _, s in _subarrays(a))


def test_check_subarray_sum_matches_brute_force():
    random.seed(25)
    assert check_subarray_sum([23, 2, 4, 6, 7], 6) is True
    assert check_subarray_sum([23, 2, 6, 4, 7], 13) is False
    assert check_subarray_sum([5, 0, 0], 3) is True       # [0, 0] counts
    assert check_subarray_sum([6], 6) is False            # length 1 does not
    for _ in range(400):
        a = [random.randint(0, 9) for _ in range(random.randint(1, 10))]
        k = random.randint(1, 7)
        want = any(len(s) >= 2 and sum(s) % k == 0 for _, _, s in _subarrays(a))
        assert check_subarray_sum(a, k) is want


def test_nice_subarrays_matches_brute_force():
    random.seed(26)
    assert nice_subarrays([1, 1, 2, 1, 1], 3) == 2
    assert nice_subarrays([2, 4, 6], 1) == 0
    for _ in range(200):
        a = [random.randint(1, 9) for _ in range(random.randint(1, 12))]
        k = random.randint(1, 4)
        want = sum(sum(x % 2 for x in s) == k for _, _, s in _subarrays(a))
        assert nice_subarrays(a, k) == want


def test_xor_subarray_count_matches_brute_force():
    random.seed(27)
    assert xor_subarray_count([4, 2, 2, 6, 4], 6) == 4
    for _ in range(200):
        a = [random.randint(0, 7) for _ in range(random.randint(0, 12))]
        k = random.randint(0, 7)
        want = 0
        for _, _, s in _subarrays(a):
            x = 0
            for v in s:
                x ^= v
            want += x == k
        assert xor_subarray_count(a, k) == want


def test_min_subarray_to_remove_matches_brute_force():
    random.seed(28)
    assert min_subarray_to_remove([3, 1, 4, 2], 6) == 1
    assert min_subarray_to_remove([6, 3, 5, 2], 9) == 2
    assert min_subarray_to_remove([1, 2, 3], 7) == -1
    for _ in range(300):
        a = [random.randint(1, 9) for _ in range(random.randint(1, 10))]
        p = random.randint(1, 10)
        total = sum(a)
        if total % p == 0:
            want = 0
        else:
            lens = [len(s) for _, _, s in _subarrays(a)
                    if len(s) < len(a) and (total - sum(s)) % p == 0]
            want = min(lens, default=-1)
        assert min_subarray_to_remove(a, p) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
