"""Same-direction read/write pointers — in-place filter, dedupe, partition.

Signs: "in place", "O(1) extra memory", "return the new length k", remove /
       keep elements by a rule, move zeroes, dedupe a sorted array, sort an
       array of only 0s, 1s and 2s.
Approach: `read` scans every element; `write` marks where the next kept
          element goes. Invariant: a[:write] is the answer so far. When
          a[read] passes the rule, copy it to a[write] and advance write.
          Dutch flag uses three regions: < pivot | == pivot | unknown | > pivot.
Complexity: O(n) time, O(1) space.
Gotchas:
  - Dedupe keeping at most k copies: compare a[read] with a[write - k], the
    last kept copy k back, not with a[read - 1] (that one may be overwritten).
  - Move zeroes must keep order -> swap with write, not with the end.
  - Dutch flag: after swapping with `hi`, do NOT advance `mid` — the value
    that came back from the right is still unexamined.
  - Order not required (LC 27)? Swapping the unwanted value with the last
    element does fewer writes.

Run the tests at the bottom with:  python3 sliding_window/read_write.py
"""


# ---------------------------------------------------------------- implementation


def remove_element(a, val):
    """LC 27. Keep everything != val in a[:k]; return k. Order kept."""
    write = 0
    for x in a:
        if x != val:
            a[write] = x
            write += 1
    return write


def remove_duplicates(a, k=1):
    """LC 26 (k=1) / LC 80 (k=2). Sorted a; keep at most k copies of each."""
    write = 0
    for x in a:
        if write < k or a[write - k] != x:  # differs from the copy k back
            a[write] = x
            write += 1
    return write


def move_zeroes(a):
    """LC 283. Zeroes to the end, others keep their order. In place."""
    write = 0
    for read in range(len(a)):
        if a[read] != 0:
            a[write], a[read] = a[read], a[write]
            write += 1


def sort_colors(a):
    """LC 75. Dutch national flag: 0s, 1s, 2s in one pass, in place.

    Invariant: a[:lo] == 0, a[lo:mid] == 1, a[mid:hi+1] unknown, a[hi+1:] == 2.
    """
    lo, mid, hi = 0, 0, len(a) - 1
    while mid <= hi:
        if a[mid] == 0:
            a[lo], a[mid] = a[mid], a[lo]
            lo += 1
            mid += 1       # what came from lo is a known 1 (or mid == lo)
        elif a[mid] == 1:
            mid += 1
        else:
            a[mid], a[hi] = a[hi], a[mid]
            hi -= 1        # mid stays: the swapped-in value is unexamined


def partition_three_way(a, pivot):
    """Rearrange a into < pivot | == pivot | > pivot. Returns (lt, gt) bounds.

    Same loop as sort_colors with a general pivot: this is the partition step
    of 3-way quicksort / quickselect.
    """
    lt, i, gt = 0, 0, len(a) - 1
    while i <= gt:
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            lt += 1
            i += 1
        elif a[i] > pivot:
            a[i], a[gt] = a[gt], a[i]
            gt -= 1
        else:
            i += 1
    return lt, gt + 1


# ------------------------------------------------------------------------ tests


def test_examples():
    a = [0, 1, 2, 2, 3, 0, 4, 2]
    k = remove_element(a, 2)
    assert a[:k] == [0, 1, 3, 0, 4]
    a = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
    assert a[:remove_duplicates(a)] == [0, 1, 2, 3, 4]
    a = [1, 1, 1, 2, 2, 3]
    assert a[:remove_duplicates(a, 2)] == [1, 1, 2, 2, 3]
    a = [0, 1, 0, 3, 12]
    move_zeroes(a)
    assert a == [1, 3, 12, 0, 0]
    a = [2, 0, 2, 1, 1, 0]
    sort_colors(a)
    assert a == [0, 0, 1, 1, 2, 2]


def test_filters_match_list_comprehension():
    import random
    from itertools import groupby

    rng = random.Random(1)
    for _ in range(500):
        orig = [rng.randint(0, 4) for _ in range(rng.randint(0, 15))]
        a = orig[:]
        assert a[:remove_element(a, 2)] == [x for x in orig if x != 2]
        a = orig[:]
        move_zeroes(a)
        nz = [x for x in orig if x != 0]
        assert a == nz + [0] * (len(orig) - len(nz))
        s = sorted(orig)
        for k in (1, 2, 3):
            a = s[:]
            want = [x for _, g in groupby(s) for x in list(g)[:k]]
            assert a[:remove_duplicates(a, k)] == want


def test_dutch_flag_matches_sort():
    import random

    rng = random.Random(2)
    for _ in range(500):
        orig = [rng.randint(0, 2) for _ in range(rng.randint(0, 15))]
        a = orig[:]
        sort_colors(a)
        assert a == sorted(orig)


def test_three_way_partition_regions():
    import random

    rng = random.Random(3)
    for _ in range(500):
        orig = [rng.randint(-5, 5) for _ in range(rng.randint(0, 15))]
        p = rng.randint(-6, 6)
        a = orig[:]
        lt, gt = partition_three_way(a, p)
        assert sorted(a) == sorted(orig)
        assert all(x < p for x in a[:lt])
        assert all(x == p for x in a[lt:gt])
        assert all(x > p for x in a[gt:])


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
