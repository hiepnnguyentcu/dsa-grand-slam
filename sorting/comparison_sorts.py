"""Comparison sorts from scratch — insertion, merge (top-down, bottom-up), quick.

Signs: "implement sort without the library", a follow-up on stability or
       worst case, nearly-sorted input, linked lists (merge sort), or any
       problem that reuses the merge / partition step (inversions, quickselect).
Approach:
  - Insertion: grow a sorted prefix; shift bigger items right, drop x in.
  - Merge: split in half, sort each, merge two sorted runs with two pointers.
    Bottom-up merges runs of width 1, 2, 4, ... with no recursion.
  - Quick: partition around a pivot, recurse on both sides. Lomuto keeps
    `< pivot` on the left; Hoare walks two pointers inward (fewer swaps);
    3-way splits `< | == | >` so duplicates never recurse.
  - Heap sort lives in stacks_heaps/heap_basics.py (heapify, pop n times).
Complexity:
  - Insertion: O(n^2) worst, O(n + inversions) — O(n) when nearly sorted.
  - Merge: O(n log n) always, O(n) extra space. Stable.
  - Quick: O(n log n) expected with a random pivot, O(n^2) worst, O(log n)
    stack if you recurse on the smaller side. Not stable.
  - Heap: O(n log n) always, O(1) extra. Not stable.
Gotchas:
  - Merge stability comes from `<=` in the merge: on a tie take the LEFT run.
  - Fixed pivot (first/last) goes quadratic on sorted input. Randomise.
  - Lomuto goes quadratic on all-equal input (every item lands on one side).
    Hoare splits equals evenly; 3-way finishes them in one pass.
  - Hoare returns a split index j, not the pivot's final spot: recurse on
    [lo, j] and [j + 1, hi].
  - Python's sorted() is Timsort: stable, O(n) on already-sorted runs.

Run the tests at the bottom with:  python3 sorting/comparison_sorts.py
"""

import random


# ---------------------------------------------------------------- implementation


def insertion_sort(a, key=lambda x: x):
    """In place. Stable: only shift strictly bigger items, so equals keep order."""
    for i in range(1, len(a)):
        x, kx = a[i], key(a[i])
        j = i - 1
        while j >= 0 and key(a[j]) > kx:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = x
    return a


def merge(left, right, key=lambda x: x):
    """Merge two sorted lists. `<=` takes from the left on ties -> stable."""
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def merge_sort(a, key=lambda x: x):
    """Top-down. Returns a new list."""
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    return merge(merge_sort(a[:mid], key), merge_sort(a[mid:], key), key)


def merge_sort_bottom_up(a, key=lambda x: x):
    """Iterative: merge adjacent runs of width 1, 2, 4, ... No recursion."""
    a = list(a)
    width = 1
    while width < len(a):
        for lo in range(0, len(a), 2 * width):
            mid, hi = min(lo + width, len(a)), min(lo + 2 * width, len(a))
            a[lo:hi] = merge(a[lo:mid], a[mid:hi], key)
        width *= 2
    return a


def lomuto_partition(a, lo, hi):
    """Partition a[lo..hi] around a random pivot. Returns pivot's final index.

    Invariant: a[lo..i-1] < pivot, a[i..j-1] >= pivot.
    """
    r = random.randint(lo, hi)
    a[r], a[hi] = a[hi], a[r]
    pivot, i = a[hi], lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i


def quicksort_lomuto(a):
    """In place. Recurse on the smaller side, loop on the larger: O(log n) stack."""
    lo, hi = 0, len(a) - 1
    stack = [(lo, hi)]
    while stack:
        lo, hi = stack.pop()
        while lo < hi:
            p = lomuto_partition(a, lo, hi)
            if p - lo < hi - p:
                stack.append((p + 1, hi))
                hi = p - 1
            else:
                stack.append((lo, p - 1))
                lo = p + 1
    return a


def hoare_partition(a, lo, hi):
    """Two pointers walk inward and swap misplaced pairs. Returns split j:
    every item in a[lo..j] <= every item in a[j+1..hi]."""
    r = random.randint(lo, hi)
    a[lo], a[r] = a[r], a[lo]  # pivot at lo guarantees j < hi (no empty side)
    pivot = a[lo]
    i, j = lo - 1, hi + 1
    while True:
        i += 1
        while a[i] < pivot:
            i += 1
        j -= 1
        while a[j] > pivot:
            j -= 1
        if i >= j:
            return j
        a[i], a[j] = a[j], a[i]


def quicksort_hoare(a, lo=0, hi=None):
    if hi is None:
        hi = len(a) - 1
    if lo < hi:
        j = hoare_partition(a, lo, hi)
        quicksort_hoare(a, lo, j)      # note: j, not j - 1
        quicksort_hoare(a, j + 1, hi)
    return a


def quicksort_3way(a, lo=0, hi=None):
    """Dijkstra 3-way: a[lo..lt-1] < p, a[lt..gt] == p, a[gt+1..hi] > p.
    Equal keys are done after one pass, so all-equal input is O(n)."""
    if hi is None:
        hi = len(a) - 1
    if lo >= hi:
        return a
    pivot = a[random.randint(lo, hi)]
    lt, i, gt = lo, lo, hi
    while i <= gt:
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            lt += 1
            i += 1
        elif a[i] > pivot:
            a[gt], a[i] = a[i], a[gt]
            gt -= 1             # don't advance i: the swapped-in item is unseen
        else:
            i += 1
    quicksort_3way(a, lo, lt - 1)
    quicksort_3way(a, gt + 1, hi)
    return a


# ------------------------------------------------------------------------ tests


def _cases():
    random.seed(1)
    yield []
    yield [5]
    yield [2, 1]
    yield [3, 3, 3, 3]
    yield list(range(50))                 # sorted: kills fixed-pivot quicksort
    yield list(range(50, 0, -1))
    for _ in range(200):
        n = random.randint(0, 40)
        yield [random.randint(-10, 10) for _ in range(n)]   # dups + negatives


def test_all_sorts_match_sorted():
    sorts = [
        lambda a: insertion_sort(list(a)),
        merge_sort,
        merge_sort_bottom_up,
        lambda a: quicksort_lomuto(list(a)),
        lambda a: quicksort_hoare(list(a)),
        lambda a: quicksort_3way(list(a)),
    ]
    for a in _cases():
        for s in sorts:
            assert s(a) == sorted(a), (a, s)


def test_merge_sort_does_not_mutate_input():
    a = [3, 1, 2]
    merge_sort(a)
    merge_sort_bottom_up(a)
    assert a == [3, 1, 2]


def test_stability_insertion_and_merge():
    random.seed(2)
    for _ in range(100):
        items = [(random.randint(0, 5), i) for i in range(random.randint(0, 30))]
        expect = sorted(items, key=lambda t: t[0])  # sorted() is stable
        k = lambda t: t[0]
        assert insertion_sort(list(items), key=k) == expect
        assert merge_sort(items, key=k) == expect
        assert merge_sort_bottom_up(items, key=k) == expect


def test_lomuto_partition_invariant():
    random.seed(4)
    for _ in range(100):
        a = [random.randint(-5, 5) for _ in range(random.randint(1, 20))]
        p = lomuto_partition(a, 0, len(a) - 1)
        assert all(x < a[p] for x in a[:p])
        assert all(x >= a[p] for x in a[p:])


def test_hoare_partition_invariant():
    random.seed(5)
    for _ in range(100):
        a = [random.randint(-5, 5) for _ in range(random.randint(2, 20))]
        j = hoare_partition(a, 0, len(a) - 1)
        assert 0 <= j < len(a) - 1
        assert max(a[: j + 1]) <= min(a[j + 1 :])


def test_3way_handles_many_duplicates_fast():
    a = [7] * 100_000           # Lomuto would be O(n^2) here
    assert quicksort_3way(a) == [7] * 100_000


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
