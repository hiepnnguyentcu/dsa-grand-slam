"""Permutations — every ordering, with dups, under a constraint.

Signs: "all orderings", "arrangements", "every way to order", n <= ~9.
Approach: loop from 0 -> start is a SLOT (position being filled) -> start+1.
          Any index can go in any slot, so a `visited` array says what's used.
          Dups: sort, skip `i > 0 and nums[i] == nums[i-1] and not visited[i-1]`
          — the earlier copy must be placed first, so equal values only ever
          appear in one relative order.
          Alternative for dups: count map (freq_m) and loop over distinct keys.
Complexity: O(n! * n).
Gotchas:
  - Forget `visited[i] = False` on the way back -> siblings see a used index.
  - Dedup `not visited[i-1]` (prune siblings) vs `visited[i-1]` (prune
    deeper) both dedupe; `not visited[i-1]` cuts far more of the tree.
  - Constrained (526, 996): check against temp[-1] / the slot BEFORE
    recursing, so a bad prefix dies early.

Run the tests at the bottom with:  python3 backtracking/permutations.py
"""

import math
import random
from collections import defaultdict
from itertools import permutations


# ---------------------------------------------------------------- implementation


def permute(nums):
    """LC 46."""
    n = len(nums)
    res = []
    visited = [False for _ in range(n)]

    def dfs(start, res, temp):
        if start == n:
            res.append(temp.copy())
            return
        for i in range(n):
            if visited[i]:
                continue
            visited[i] = True
            temp.append(nums[i])
            dfs(start + 1, res, temp)
            temp.pop()
            visited[i] = False
    dfs(0, res, [])
    return res


def permute_unique(nums):
    """LC 47."""
    n = len(nums)
    nums = sorted(nums)
    res = []
    visited = [False for _ in range(n)]

    def dfs(start, res, temp):
        if start == n:
            res.append(temp.copy())
            return
        for i in range(n):
            if visited[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not visited[i - 1]:
                continue
            visited[i] = True
            temp.append(nums[i])
            dfs(start + 1, res, temp)
            temp.pop()
            visited[i] = False
    dfs(0, res, [])
    return res


def num_tile_possibilities(tiles):
    """LC 1079. Count non-empty distinct sequences. Count map dedupes for free."""
    freq_m = defaultdict(int)
    for char in tiles:
        freq_m[char] += 1

    def dfs():
        count = 0
        for char in freq_m:
            if freq_m[char] > 0:
                freq_m[char] -= 1
                count += 1 + dfs()          # this sequence + all its extensions
                freq_m[char] += 1
        return count
    return dfs()


def generate_palindromes(s):
    """LC 267. Permute half the counts, mirror around the odd center."""
    freq_m = defaultdict(int)
    for char in s:
        freq_m[char] += 1

    odd = []
    for char, freq in freq_m.items():
        if freq % 2 != 0:
            odd.append(char)

    if len(odd) > 1:
        return []

    for char in freq_m:
        freq_m[char] //= 2

    half_len = sum(freq_m.values())
    center = odd[0] if len(odd) == 1 else ""
    res = []

    def dfs(start, res, temp, freq_m):
        if start == half_len:
            left = "".join(temp)
            right = left[::-1]
            res.append(left + center + right)
            return
        for char in freq_m:
            if freq_m[char] > 0:
                freq_m[char] -= 1
                temp.append(char)
                dfs(start + 1, res, temp, freq_m)
                temp.pop()
                freq_m[char] += 1
    dfs(0, res, [], freq_m)
    return res


def count_arrangement(n):
    """LC 526. Slot `start` (1-indexed) takes num if num % start == 0 or start % num == 0."""
    visited = [False for _ in range(n + 1)]

    def dfs(start):
        if start > n:
            return 1
        count = 0
        for num in range(1, n + 1):
            if visited[num] or (num % start and start % num):
                continue
            visited[num] = True
            count += dfs(start + 1)
            visited[num] = False
        return count
    return dfs(1)


def num_squareful_perms(nums):
    """LC 996. Distinct perms where every adjacent pair sums to a perfect square."""
    n = len(nums)
    nums = sorted(nums)
    visited = [False for _ in range(n)]

    def is_square(x):
        return math.isqrt(x) ** 2 == x

    def dfs(start, temp):
        if start == n:
            return 1
        count = 0
        for i in range(n):
            if visited[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not visited[i - 1]:
                continue
            if temp and not is_square(temp[-1] + nums[i]):
                continue
            visited[i] = True
            temp.append(nums[i])
            count += dfs(start + 1, temp)
            temp.pop()
            visited[i] = False
        return count
    return dfs(0, [])


# ------------------------------------------------------------------------ tests


def test_permute_vs_itertools():
    random.seed(1)
    for n in range(0, 7):
        nums = random.sample(range(50), n)
        got = permute(nums)
        assert len(got) == math.factorial(n)
        assert sorted(map(tuple, got)) == sorted(permutations(nums))


def test_permute_unique_vs_deduped_itertools():
    assert sorted(map(tuple, permute_unique([1, 1, 2]))) == [(1, 1, 2), (1, 2, 1), (2, 1, 1)]
    random.seed(2)
    for _ in range(60):
        nums = [random.randint(0, 2) for _ in range(random.randint(0, 7))]
        got = permute_unique(nums)
        want = set(permutations(nums))
        assert len(got) == len(want) and set(map(tuple, got)) == want


def test_dedup_visited_and_not_visited_both_work():
    def run(prune_siblings):
        nums, n, res = [1, 1, 1, 2], 4, []
        visited = [False] * n

        def dfs(start, temp):
            if start == n:
                res.append(tuple(temp)); return
            for i in range(n):
                if visited[i]:
                    continue
                if i > 0 and nums[i] == nums[i - 1] and visited[i - 1] != prune_siblings:
                    continue
                visited[i] = True; temp.append(nums[i])
                dfs(start + 1, temp)
                temp.pop(); visited[i] = False
        dfs(0, [])
        return res
    a, b = run(True), run(False)
    assert len(a) == len(set(a)) == 4 and set(a) == set(b) and len(b) == 4


def test_num_tile_possibilities_vs_brute_force():
    assert num_tile_possibilities("AAB") == 8
    assert num_tile_possibilities("AAABBC") == 188
    random.seed(3)
    for _ in range(30):
        tiles = "".join(random.choice("ABC") for _ in range(random.randint(1, 6)))
        want = {p for r in range(1, len(tiles) + 1) for p in permutations(tiles, r)}
        assert num_tile_possibilities(tiles) == len(want)


def test_generate_palindromes_vs_brute_force():
    assert sorted(generate_palindromes("aabb")) == ["abba", "baab"]
    assert generate_palindromes("abc") == []
    random.seed(4)
    for _ in range(40):
        s = "".join(random.choice("abc") for _ in range(random.randint(1, 7)))
        want = {"".join(p) for p in permutations(s) if "".join(p) == "".join(p)[::-1]}
        got = generate_palindromes(s)
        assert len(got) == len(want) and set(got) == want


def test_count_arrangement_vs_brute_force():
    for n in range(1, 8):
        want = sum(all(p % i == 0 or i % p == 0 for i, p in enumerate(perm, 1))
                   for perm in permutations(range(1, n + 1)))
        assert count_arrangement(n) == want


def test_num_squareful_perms_vs_brute_force():
    assert num_squareful_perms([1, 17, 8]) == 2
    assert num_squareful_perms([2, 2, 2]) == 1
    random.seed(5)
    for _ in range(40):
        nums = [random.choice([0, 1, 2, 3, 7, 8, 9, 16]) for _ in range(random.randint(1, 6))]
        want = {p for p in permutations(nums)
                if all(math.isqrt(a + b) ** 2 == a + b for a, b in zip(p, p[1:]))}
        assert num_squareful_perms(nums) == len(want)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
