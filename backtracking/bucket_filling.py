"""Bucket filling — split items into k groups (equal sums, or min max load).

Signs: "partition into k equal-sum subsets", "matchsticks square",
       "distribute to k children / workers, minimise the max", n <= ~16.
Approach: two views.
          bucket -> items (698, 473): fill ONE bucket to target with a
            loop-from-start over unused items (visited); when it hits target,
            restart at dfs(0, k_left - 1, 0) for the next bucket. k_left == 1
            -> done (last bucket must hold the rest).
          item -> bucket (2305, 1723): start is the item (slot); loop over
            the k buckets, add, recurse start + 1, subtract.
Pruning that makes it pass:
  - sort descending: big items fail fast.
  - skip `curr_sum + nums[i] > target`.
  - bucket -> items: if curr_sum == 0 after a failed try, break — an empty
    bucket that can't take this item never will.
  - item -> bucket: two empty buckets are the same; break after the first.
    Skip a bucket once its load >= best so far.
Complexity: O(k * 2^n) worst case; pruning is what makes it fast.
Gotchas:
  - total % k != 0 -> False up front; any item > target -> False.
  - 2551 (marbles in bags) looks like this but is greedy: sort pair sums.

Run the tests at the bottom with:  python3 backtracking/bucket_filling.py
"""

import random
from itertools import combinations, product


# ---------------------------------------------------------------- implementation


def can_partition_k_subsets(nums, k):
    """LC 698."""
    total = sum(nums)
    if total % k:
        return False

    target = total // k
    nums = sorted(nums, reverse=True)
    visited = [False for _ in range(len(nums))]

    def dfs(start, k_left, curr_sum):
        if k_left == 1:
            return True

        if curr_sum == target:
            return dfs(0, k_left - 1, 0)

        for i in range(start, len(nums)):
            if visited[i] or curr_sum + nums[i] > target:
                continue
            visited[i] = True
            if dfs(i + 1, k_left, curr_sum + nums[i]):
                return True
            visited[i] = False

            if curr_sum == 0:
                break
        return False
    return dfs(0, k, 0)


def makesquare(matchsticks):
    """LC 473. Same as 698 with k = 4."""
    if sum(matchsticks) % 4 != 0:
        return False

    target = sum(matchsticks) // 4
    nums = sorted(matchsticks, reverse=True)
    visited = [False for _ in range(len(matchsticks))]

    def dfs(start, k_left, curr_sum):
        if k_left == 1:
            return True

        if curr_sum == target:
            return dfs(0, k_left - 1, 0)

        for i in range(start, len(nums)):
            if visited[i] or curr_sum + nums[i] > target:
                continue

            visited[i] = True
            if dfs(i + 1, k_left, curr_sum + nums[i]):
                return True
            visited[i] = False

            if curr_sum == 0:
                break
        return False

    return dfs(0, 4, 0)


def distribute_cookies(cookies, k):
    """LC 2305. Min over distributions of the max child total."""
    n = len(cookies)
    cookies = sorted(cookies, reverse=True)
    buckets = [0 for _ in range(k)]
    res = [float("inf")]

    def dfs(start):
        if start == n:
            res[0] = min(res[0], max(buckets))
            return
        for j in range(k):
            if buckets[j] + cookies[start] >= res[0]:
                continue
            buckets[j] += cookies[start]
            dfs(start + 1)
            buckets[j] -= cookies[start]
            if buckets[j] == 0:            # other empty buckets are the same
                break
    dfs(0)
    return res[0]


def minimum_time_required(jobs, k):
    """LC 1723. Same as 2305: min possible max worker load."""
    n = len(jobs)
    jobs = sorted(jobs, reverse=True)
    workers = [0 for _ in range(k)]
    res = [sum(jobs)]

    def dfs(start):
        if start == n:
            res[0] = min(res[0], max(workers))
            return
        for j in range(k):
            if workers[j] + jobs[start] >= res[0]:
                continue
            workers[j] += jobs[start]
            dfs(start + 1)
            workers[j] -= jobs[start]
            if workers[j] == 0:
                break
    dfs(0)
    return res[0]


def put_marbles(weights, k):
    """LC 2551. Greedy, not backtracking: each cut adds weights[i] + weights[i+1]."""
    pair_sums = sorted(weights[i] + weights[i + 1] for i in range(len(weights) - 1))
    return sum(pair_sums[len(pair_sums) - k + 1:]) - sum(pair_sums[:k - 1])


# ------------------------------------------------------------------------ tests


def brute_k_equal(nums, k):
    if sum(nums) % k:
        return False
    target = sum(nums) // k
    for assign in product(range(k), repeat=len(nums)):
        sums = [0] * k
        for x, b in zip(nums, assign):
            sums[b] += x
        if all(s == target for s in sums):
            return True
    return False


def brute_min_max(nums, k):
    best = float("inf")
    for assign in product(range(k), repeat=len(nums)):
        sums = [0] * k
        for x, b in zip(nums, assign):
            sums[b] += x
        best = min(best, max(sums))
    return best


def test_can_partition_k_subsets_vs_brute_force():
    assert can_partition_k_subsets([4, 3, 2, 3, 5, 2, 1], 4)
    assert not can_partition_k_subsets([1, 2, 3, 4], 3)
    random.seed(1)
    for _ in range(150):
        nums = [random.randint(1, 6) for _ in range(random.randint(1, 7))]
        k = random.randint(1, 4)
        assert can_partition_k_subsets(nums, k) == brute_k_equal(nums, k)


def test_makesquare_vs_brute_force():
    assert makesquare([1, 1, 2, 2, 2]) and not makesquare([3, 3, 3, 3, 4])
    random.seed(2)
    for _ in range(80):
        sticks = [random.randint(1, 5) for _ in range(random.randint(1, 8))]
        assert makesquare(sticks) == brute_k_equal(sticks, 4)


def test_distribute_cookies_and_jobs_vs_brute_force():
    assert distribute_cookies([8, 15, 10, 20, 8], 2) == 31
    assert minimum_time_required([1, 2, 4, 7, 8], 2) == 11
    random.seed(3)
    for _ in range(80):
        nums = [random.randint(1, 20) for _ in range(random.randint(2, 7))]
        k = random.randint(2, min(4, len(nums)))
        want = brute_min_max(nums, k)
        assert distribute_cookies(nums, k) == want
        assert minimum_time_required(nums, k) == want


def test_put_marbles_vs_brute_force():
    assert put_marbles([1, 3, 5, 1], 2) == 4
    random.seed(4)
    for _ in range(80):
        w = [random.randint(1, 9) for _ in range(random.randint(1, 8))]
        k = random.randint(1, len(w))
        scores = []
        for cuts in combinations(range(1, len(w)), k - 1):
            bounds = [0, *cuts, len(w)]
            scores.append(sum(w[a] + w[b - 1] for a, b in zip(bounds, bounds[1:])))
        assert put_marbles(w, k) == max(scores) - min(scores)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
