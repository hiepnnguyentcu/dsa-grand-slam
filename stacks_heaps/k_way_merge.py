"""K-way merge — a heap holding one frontier item per sorted source.

Signs: "merge k sorted lists", "kth smallest in a sorted matrix", "smallest
       range covering one element from each list", "k pairs with smallest
       sums", any problem over several sorted sequences at once.
Approach: seed the heap with the head of each source as (value, source, index).
          Pop the smallest, emit it, push that source's next item. The heap
          never holds more than k items, and it always contains the next
          smallest overall. For a sorted matrix, rows are the sources. For
          pairs, (i, j) spawns (i, j+1) — seeding with every (i, 0).
Complexity: O(N log k) to merge N items from k sources; O(k) heap space.
            kth-of-merge is O(k + m log k) for the m-th item.
Gotchas:
  - Include the source index in the tuple so equal values never fall through
    to comparing list nodes (TypeError on linked lists).
  - Smallest range: track the current *max* of the frontier separately; the
    heap only knows the min. Stop as soon as any source runs out.
  - k smallest pairs: seed only min(k, len(a)) rows, or it is O(len(a)) for
    small k.

Run the tests at the bottom with:  python3 stacks_heaps/k_way_merge.py
"""

import heapq


# ---------------------------------------------------------------- implementation


def merge_k_sorted(lists):
    """One sorted list from k sorted lists."""
    h = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(h)
    out = []
    while h:
        val, i, j = heapq.heappop(h)
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(h, (lists[i][j + 1], i, j + 1))
    return out


def kth_smallest_matrix(matrix, k):
    """kth smallest (1-based) in an n x n matrix with sorted rows and columns.

    Rows are the sorted sources; only the first min(n, k) rows can matter.
    """
    n = len(matrix)
    h = [(matrix[r][0], r, 0) for r in range(min(n, k))]
    heapq.heapify(h)
    for _ in range(k - 1):
        _, r, c = heapq.heappop(h)
        if c + 1 < len(matrix[r]):
            heapq.heappush(h, (matrix[r][c + 1], r, c + 1))
    return h[0][0]


def kth_smallest_matrix_binary_search(matrix, k):
    """Same answer by binary search on the value: count entries <= mid."""
    n = len(matrix)
    lo, hi = matrix[0][0], matrix[-1][-1]
    while lo < hi:
        mid = (lo + hi) // 2
        cnt, c = 0, n - 1  # staircase walk from the top-right corner
        for r in range(n):
            while c >= 0 and matrix[r][c] > mid:
                c -= 1
            cnt += c + 1
        if cnt >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo


def smallest_range(lists):
    """[lo, hi] of minimal width containing at least one item of every list.

    Ties on width go to the smaller lo.
    """
    h = [(lst[0], i, 0) for i, lst in enumerate(lists)]
    heapq.heapify(h)
    cur_max = max(lst[0] for lst in lists)
    best = (h[0][0], cur_max)
    while True:
        lo, i, j = heapq.heappop(h)
        if cur_max - lo < best[1] - best[0]:
            best = (lo, cur_max)
        if j + 1 == len(lists[i]):
            return list(best)  # this list is exhausted: no window can include it
        nxt = lists[i][j + 1]
        cur_max = max(cur_max, nxt)
        heapq.heappush(h, (nxt, i, j + 1))


def k_smallest_pairs(a, b, k):
    """k pairs (x from a, y from b) with the smallest sums; a, b sorted."""
    if not a or not b:
        return []
    h = [(a[i] + b[0], i, 0) for i in range(min(k, len(a)))]
    heapq.heapify(h)
    out = []
    while h and len(out) < k:
        _, i, j = heapq.heappop(h)
        out.append((a[i], b[j]))
        if j + 1 < len(b):
            heapq.heappush(h, (a[i] + b[j + 1], i, j + 1))
    return out


# ------------------------------------------------------------------------ tests


def test_merge_k_sorted():
    import random

    assert merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]]) == [1, 1, 2, 3, 4, 4, 5, 6]
    assert merge_k_sorted([]) == []
    assert merge_k_sorted([[], []]) == []
    rng = random.Random(1)
    for _ in range(500):
        lists = [sorted(rng.randint(0, 20) for _ in range(rng.randint(0, 6))) for _ in range(rng.randint(0, 5))]
        assert merge_k_sorted(lists) == sorted(x for lst in lists for x in lst)


def random_sorted_matrix(rng, n):
    """Rows and columns non-decreasing: prefix maxima of a random grid."""
    m = [[rng.randint(0, 5) for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            m[r][c] += max(m[r - 1][c] if r else 0, m[r][c - 1] if c else 0)
    return m


def test_kth_smallest_matrix():
    import random

    m = [[1, 5, 9], [10, 11, 13], [12, 13, 15]]
    assert kth_smallest_matrix(m, 8) == 13
    assert kth_smallest_matrix_binary_search(m, 8) == 13
    rng = random.Random(2)
    for _ in range(300):
        n = rng.randint(1, 5)
        m = random_sorted_matrix(rng, n)
        flat = sorted(x for row in m for x in row)
        for k in range(1, n * n + 1):
            assert kth_smallest_matrix(m, k) == flat[k - 1]
            assert kth_smallest_matrix_binary_search(m, k) == flat[k - 1]


def brute_smallest_range(lists):
    values = sorted({x for lst in lists for x in lst})
    best = None
    for lo in values:
        for hi in values:
            if hi >= lo and all(any(lo <= x <= hi for x in lst) for lst in lists):
                if best is None or (hi - lo, lo) < (best[1] - best[0], best[0]):
                    best = [lo, hi]
    return best


def test_smallest_range():
    import random

    lists = [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]
    assert smallest_range(lists) == [20, 24]
    assert smallest_range([[1, 2, 3], [1, 2, 3], [1, 2, 3]]) == [1, 1]
    rng = random.Random(3)
    for _ in range(400):
        lists = [sorted(rng.randint(0, 15) for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(1, 4))]
        assert smallest_range(lists) == brute_smallest_range(lists), lists


def test_k_smallest_pairs():
    import random

    assert k_smallest_pairs([1, 7, 11], [2, 4, 6], 3) == [(1, 2), (1, 4), (1, 6)]
    rng = random.Random(4)
    for _ in range(400):
        a = sorted(rng.randint(0, 10) for _ in range(rng.randint(0, 5)))
        b = sorted(rng.randint(0, 10) for _ in range(rng.randint(0, 5)))
        k = rng.randint(1, 12)
        got = k_smallest_pairs(a, b, k)
        all_sums = sorted(x + y for x in a for y in b)
        assert sorted(x + y for x, y in got) == all_sums[:k]
        assert len(got) == min(k, len(a) * len(b))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
