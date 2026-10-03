"""K-th smallest by value — binary search the value, count how many are <= it.

Signs: "k-th smallest in a sorted matrix", "k-th number in a multiplication
       table", "k-th smallest pair distance", "k-th smallest fraction", too
       many candidates to list (m * n up to 1e9) but each can be counted fast.
Approach: let count(v) = number of candidates <= v. It is non-decreasing in v,
          so the k-th smallest is the first v with count(v) >= k (first_true
          on values). That v is always a real candidate: count jumps only at
          candidate values.
Complexity: O(log(value range) x cost(count)). Sorted matrix:
            O((R + C) log range); multiplication table: O(m log(m * n));
            pair distances: O(n log n + n log range).
Gotchas:
  - Search on VALUES, not indices; there's no array to index into.
  - Use count(v) >= k, not == k. Duplicates make count skip past k.
  - Real-valued candidates (fractions) need a different finish: track the
    largest candidate <= mid while counting.
  - A heap gives O(k log k); prefer it only when k is small.

Run the tests at the bottom with:  python3 binary_search/kth_by_value.py
"""


# ---------------------------------------------------------------- implementation


def first_true(lo, hi, pred):
    while lo < hi:
        mid = (lo + hi) // 2
        if pred(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def kth_smallest_matrix(m, k):
    """k-th smallest (1-based) in a matrix whose rows and columns are sorted."""
    R, C = len(m), len(m[0])

    def count_leq(x):                  # staircase from bottom-left
        r, c, count = R - 1, 0, 0
        while r >= 0 and c < C:
            if m[r][c] <= x:
                count += r + 1
                c += 1
            else:
                r -= 1
        return count

    return first_true(m[0][0], m[-1][-1], lambda v: count_leq(v) >= k)


def kth_in_multiplication_table(m, n, k):
    """k-th smallest in the m x n table where cell (i, j) = i * j (1-based).

    Row i holds i, 2i, ..., ni, so it has min(v // i, n) entries <= v.
    """
    def enough(v):
        return sum(min(v // i, n) for i in range(1, m + 1)) >= k

    return first_true(1, m * n, enough)


def kth_smallest_pair_distance(nums, k):
    """k-th smallest |a[i] - a[j]| over pairs i < j.

    After sorting, count pairs with distance <= d by a sliding window: for
    each right end, the left end only ever moves right.
    """
    a = sorted(nums)

    def enough(d):
        count = left = 0
        for right in range(len(a)):
            while a[right] - a[left] > d:
                left += 1
            count += right - left
        return count >= k

    return first_true(0, a[-1] - a[0], enough)


def kth_smallest_fraction(arr, k):
    """k-th smallest arr[i] / arr[j], i < j, arr sorted, distinct primes and 1.

    Real-valued search on the fraction. While counting fractions <= mid,
    remember the largest one; when the count hits exactly k, that is it.
    Distinct fractions guarantee an exact hit eventually.
    """
    n = len(arr)
    lo, hi = 0.0, 1.0
    while True:
        mid = (lo + hi) / 2
        count, best, j = 0, (0, 1), 1
        for i in range(n - 1):
            while j < n and arr[i] > mid * arr[j]:
                j += 1
            if j == n:
                break
            count += n - j
            if arr[i] * best[1] > best[0] * arr[j]:
                best = (arr[i], arr[j])
        if count == k:
            return list(best)
        if count < k:
            lo = mid
        else:
            hi = mid


# ------------------------------------------------------------------------ tests


def test_matrix_matches_sorting():
    import random

    rng = random.Random(80)
    for _ in range(200):
        R, C = rng.randint(1, 6), rng.randint(1, 6)
        m = [[0] * C for _ in range(R)]
        for r in range(R):
            for c in range(C):
                floor = max(m[r - 1][c] if r else -5, m[r][c - 1] if c else -5)
                m[r][c] = floor + rng.randint(0, 3)
        flat = sorted(v for row in m for v in row)
        for k in range(1, R * C + 1):
            assert kth_smallest_matrix(m, k) == flat[k - 1]


def test_multiplication_table_matches_sorting():
    for m in range(1, 8):
        for n in range(1, 8):
            flat = sorted(i * j for i in range(1, m + 1) for j in range(1, n + 1))
            for k in range(1, m * n + 1):
                assert kth_in_multiplication_table(m, n, k) == flat[k - 1]
    assert kth_in_multiplication_table(3, 3, 5) == 3


def test_pair_distance_matches_sorting():
    import random

    rng = random.Random(81)
    for _ in range(300):
        nums = [rng.randint(0, 30) for _ in range(rng.randint(2, 10))]
        dists = sorted(abs(nums[i] - nums[j]) for i in range(len(nums)) for j in range(i + 1, len(nums)))
        k = rng.randint(1, len(dists))
        assert kth_smallest_pair_distance(nums, k) == dists[k - 1]


def test_fraction_matches_sorting():
    from fractions import Fraction

    primes = [1, 2, 3, 5, 7, 11, 13, 17, 19, 23]
    for size in range(2, len(primes) + 1):
        arr = primes[:size]
        fr = sorted((Fraction(arr[i], arr[j]), arr[i], arr[j])
                    for i in range(size) for j in range(i + 1, size))
        for k in range(1, len(fr) + 1):
            assert kth_smallest_fraction(arr, k) == [fr[k - 1][1], fr[k - 1][2]]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
