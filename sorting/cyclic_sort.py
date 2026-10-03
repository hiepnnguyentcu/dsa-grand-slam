"""Cyclic sort — values in 1..n go to index value - 1, in place.

Signs: "array of n integers in the range [1, n]" (or [0, n]), "find the
       missing / duplicate / disappeared numbers", O(n) time AND O(1) extra
       space, "first missing positive", minimum swaps to place items.
Approach: walk i; while a[i] is in range and not already at its home
          (a[a[i] - 1] != a[i]), swap it home. Each swap fixes one value for
          good, so there are at most n swaps in total. Afterwards, any index
          i with a[i] != i + 1 is a hole: i + 1 is missing and a[i] is a
          duplicate (or out of range).
          Floyd's read-only duplicate finder: sliding_window/fast_slow.py.
Complexity: O(n) time (<= n swaps plus one scan), O(1) extra.
Gotchas:
  - Compare with the TARGET slot (a[a[i] - 1] != a[i]), not with i + 1, or
    duplicates loop forever.
  - Use `while`, not `if`: the value swapped into i also needs a home.
  - Out-of-range values (<= 0, > n) just stay put and mark holes.
  - It mutates the input. If that's banned, use sign-marking (also mutates)
    or Floyd (read-only) for the duplicate.

Run the tests at the bottom with:  python3 sorting/cyclic_sort.py
"""

import random
from itertools import permutations


# ---------------------------------------------------------------- implementation


def cyclic_sort(a):
    """Place each in-range value v at index v - 1. In place; returns a."""
    n = len(a)
    for i in range(n):
        while 1 <= a[i] <= n and a[a[i] - 1] != a[i]:
            j = a[i] - 1
            a[i], a[j] = a[j], a[i]
    return a


def first_missing_positive(nums):
    """Smallest positive int not in nums. O(n) time, O(1) extra."""
    a = cyclic_sort(list(nums))     # copy only so tests can reuse inputs
    for i, x in enumerate(a):
        if x != i + 1:
            return i + 1
    return len(a) + 1


def find_disappeared(nums):
    """Values in 1..n absent from nums (len n, values in 1..n)."""
    a = cyclic_sort(list(nums))
    return [i + 1 for i, x in enumerate(a) if x != i + 1]


def find_all_duplicates(nums):
    """Values appearing twice (values in 1..n): they sit in someone else's hole."""
    a = cyclic_sort(list(nums))
    return sorted(x for i, x in enumerate(a) if x != i + 1)


def find_duplicate_cyclic(nums):
    """n + 1 values in 1..n, one repeated. Mutating contrast to Floyd.

    Swap a[0] home until its home already holds the same value.
    """
    a = list(nums)
    while a[a[0]] != a[0]:
        j = a[0]
        a[0], a[j] = a[j], a[0]
    return a[0]


def min_swaps_couples(row):
    """Couples holding hands: pairs (0,1), (2,3), ... must sit side by side.

    Greedy: for each seat pair, if the partner isn't next to you, swap them
    in. Each swap seats one couple for good, which is optimal (each cycle of
    c mismatched couples needs exactly c - 1 swaps).
    """
    row = list(row)
    pos = {p: i for i, p in enumerate(row)}
    swaps = 0
    for i in range(0, len(row), 2):
        partner = row[i] ^ 1
        if row[i + 1] != partner:
            j = pos[partner]
            row[i + 1], row[j] = row[j], row[i + 1]
            pos[row[j]], pos[partner] = j, i + 1
            swaps += 1
    return swaps


def min_swaps_to_sort(a):
    """Min swaps to sort distinct values = n - number of cycles in the permutation."""
    order = sorted(range(len(a)), key=lambda i: a[i])   # order[k] = index of k-th smallest
    seen, swaps = [False] * len(a), 0
    for i in range(len(a)):
        length = 0
        while not seen[i]:
            seen[i] = True
            i = order[i]
            length += 1
        swaps += max(0, length - 1)
    return swaps


# ------------------------------------------------------------------------ tests


def test_cyclic_sort_permutation_is_sorted():
    random.seed(61)
    assert cyclic_sort([]) == []
    for _ in range(100):
        n = random.randint(1, 20)
        a = random.sample(range(1, n + 1), n)
        assert cyclic_sort(a) == list(range(1, n + 1))


def test_first_missing_positive_matches_set_scan():
    assert first_missing_positive([1, 2, 0]) == 3
    assert first_missing_positive([3, 4, -1, 1]) == 2
    assert first_missing_positive([7, 8, 9, 11, 12]) == 1
    assert first_missing_positive([]) == 1
    assert first_missing_positive([1, 1]) == 2
    random.seed(62)
    for _ in range(300):
        a = [random.randint(-3, 12) for _ in range(random.randint(0, 12))]
        s, m = set(a), 1
        while m in s:
            m += 1
        assert first_missing_positive(a) == m


def test_disappeared_and_duplicates_match_counter():
    assert find_disappeared([4, 3, 2, 7, 8, 2, 3, 1]) == [5, 6]
    assert find_all_duplicates([4, 3, 2, 7, 8, 2, 3, 1]) == [2, 3]
    random.seed(63)
    for _ in range(300):
        n = random.randint(1, 15)
        a = [random.randint(1, n) for _ in range(n)]
        assert find_disappeared(a) == [v for v in range(1, n + 1) if v not in a]
        # with values in 1..n, the holes hold each extra copy once
        extras = sorted(v for v in set(a) for _ in range(a.count(v) - 1))
        assert find_all_duplicates(a) == extras


def test_find_duplicate_cyclic():
    assert find_duplicate_cyclic([1, 3, 4, 2, 2]) == 2
    assert find_duplicate_cyclic([3, 1, 3, 4, 2]) == 3
    assert find_duplicate_cyclic([1, 1]) == 1
    random.seed(64)
    for _ in range(300):
        n = random.randint(1, 15)
        dup = random.randint(1, n)
        a = list(range(1, n + 1)) + [dup]
        for i in random.sample(range(n + 1), random.randint(0, n // 2)):
            a[i] = dup                  # the duplicate may repeat many times
        random.shuffle(a)
        assert find_duplicate_cyclic(a) == dup


def _brute_swaps(start, done):
    """BFS over arrangements: fewest swaps to reach a state where done() holds."""
    from collections import deque
    start = tuple(start)
    dist, q = {start: 0}, deque([start])
    while q:
        s = q.popleft()
        if done(s):
            return dist[s]
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                t = list(s)
                t[i], t[j] = t[j], t[i]
                t = tuple(t)
                if t not in dist:
                    dist[t] = dist[s] + 1
                    q.append(t)


def test_couples_match_bfs():
    assert min_swaps_couples([0, 2, 1, 3]) == 1
    assert min_swaps_couples([3, 2, 0, 1]) == 0
    random.seed(65)
    paired = lambda s: all(s[i] ^ 1 == s[i + 1] for i in range(0, len(s), 2))
    for _ in range(40):
        n = 2 * random.randint(1, 3)
        row = random.sample(range(n), n)
        assert min_swaps_couples(row) == _brute_swaps(row, paired)


def test_min_swaps_to_sort_matches_bfs():
    assert min_swaps_to_sort([]) == 0
    assert min_swaps_to_sort([4, 3, 2, 1]) == 2
    for p in permutations([10, -3, 7, 0, 5]):
        target = tuple(sorted(p))
        assert min_swaps_to_sort(list(p)) == _brute_swaps(p, lambda s: s == target)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
