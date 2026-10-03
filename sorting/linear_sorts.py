"""Non-comparison sorts — counting, radix (LSD), bucket.

Signs: small integer range ("0 <= x <= 100", ages, grades, letters), fixed-
       width keys (digits, 32-bit ints, equal-length strings), uniform floats
       in [0, 1), or an interviewer asking to beat O(n log n).
Approach:
  - Counting: tally each value, then either rewrite values in order (simple),
    or turn counts into prefix sums = end positions and place items from the
    RIGHT (stable, works for records with an integer key).
  - Radix LSD: stable counting sort on the lowest digit, then the next, ...
    Stability carries earlier digits' order through later passes.
  - Bucket: spread n items into n buckets by value, sort each small bucket,
    concatenate. Top-k frequent by count buckets: stacks_heaps/top_k.py.
Complexity:
  - Counting: O(n + k) time and space, k = value range.
  - Radix: O(d * (n + b)), d digits in base b. 32-bit ints, base 256: 4 passes.
  - Bucket: O(n) expected for uniform input, O(n^2) if everything lands in
    one bucket (insertion sort inside).
Gotchas:
  - Counting sort with k >> n is worse than sorting. Offset by min(a) so
    negatives and ranges like [1e9, 1e9 + 100] still work.
  - The stable version must walk the input right-to-left (or use start
    positions and walk left-to-right). Mixing the two breaks stability.
  - Radix MUST use a stable inner sort, and LSD goes low digit -> high.
  - Negatives in radix: sort |x| of negatives and non-negatives separately,
    reverse the negatives. (Or add an offset.)

Run the tests at the bottom with:  python3 sorting/linear_sorts.py
"""

import random


# ---------------------------------------------------------------- implementation


def counting_sort(a):
    """Integers only. Offset by the min so negatives work."""
    if not a:
        return []
    lo = min(a)
    count = [0] * (max(a) - lo + 1)
    for x in a:
        count[x - lo] += 1
    out = []
    for v, c in enumerate(count):
        out.extend([v + lo] * c)
    return out


def counting_sort_stable(items, key, k):
    """Stable sort of records by an integer key in [0, k).

    pos[v] = number of items with key <= v = one past the last slot for v.
    Walk the input backwards and fill each key's slots from the right.
    """
    pos = [0] * k
    for it in items:
        pos[key(it)] += 1
    for v in range(1, k):
        pos[v] += pos[v - 1]
    out = [None] * len(items)
    for it in reversed(items):
        pos[key(it)] -= 1
        out[pos[key(it)]] = it
    return out


def radix_sort_nonneg(a, base=10):
    """LSD radix sort for non-negative ints: one stable counting pass per digit."""
    if not a:
        return []
    out, exp, top = list(a), 1, max(a)
    while top // exp > 0:
        out = counting_sort_stable(out, lambda x: (x // exp) % base, base)
        exp *= base
    return out


def radix_sort(a, base=10):
    """Handles negatives: sort magnitudes of each sign, reverse the negatives."""
    neg = radix_sort_nonneg([-x for x in a if x < 0], base)
    pos = radix_sort_nonneg([x for x in a if x >= 0], base)
    return [-x for x in reversed(neg)] + pos


def bucket_sort(a):
    """Floats in [0, 1). n buckets; bucket i takes [i/n, (i+1)/n)."""
    n = len(a)
    buckets = [[] for _ in range(n)]
    for x in a:
        buckets[int(x * n)].append(x)
    out = []
    for b in buckets:
        out.extend(sorted(b))  # tiny buckets; insertion sort in the textbook
    return out


def sort_letters(s):
    """Counting sort over 26 letters — 'sort a string' in O(n)."""
    count = [0] * 26
    for ch in s:
        count[ord(ch) - 97] += 1
    return "".join(chr(97 + i) * c for i, c in enumerate(count))


# ------------------------------------------------------------------------ tests


def _int_cases():
    random.seed(11)
    yield []
    yield [0]
    yield [-3]
    yield [5, 5, 5]
    yield [10**9, 10**9 + 3, 10**9 + 1]   # big values, small range
    for _ in range(200):
        n = random.randint(0, 40)
        yield [random.randint(-50, 50) for _ in range(n)]


def test_counting_sort_matches_sorted():
    for a in _int_cases():
        assert counting_sort(a) == sorted(a)


def test_counting_sort_stable_is_stable():
    random.seed(12)
    for _ in range(200):
        items = [(random.randint(0, 6), i) for i in range(random.randint(0, 30))]
        got = counting_sort_stable(items, key=lambda t: t[0], k=7)
        assert got == sorted(items, key=lambda t: t[0])  # sorted() is stable


def test_radix_nonneg_matches_sorted():
    random.seed(13)
    for base in (2, 10, 256):
        for _ in range(100):
            a = [random.randint(0, 10**6) for _ in range(random.randint(0, 40))]
            assert radix_sort_nonneg(a, base) == sorted(a)
    assert radix_sort_nonneg([0, 0]) == [0, 0]


def test_radix_with_negatives():
    for a in _int_cases():
        assert radix_sort(a) == sorted(a)


def test_bucket_sort_floats():
    random.seed(14)
    assert bucket_sort([]) == []
    assert bucket_sort([0.5]) == [0.5]
    for _ in range(100):
        a = [random.random() for _ in range(random.randint(0, 50))]
        assert bucket_sort(a) == sorted(a)
    skewed = [0.001 * random.random() for _ in range(50)]  # all in bucket 0
    assert bucket_sort(skewed) == sorted(skewed)


def test_sort_letters():
    random.seed(15)
    assert sort_letters("") == ""
    for _ in range(50):
        s = "".join(random.choice("abcxyz") for _ in range(random.randint(0, 20)))
        assert sort_letters(s) == "".join(sorted(s))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
