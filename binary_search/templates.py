"""Binary search templates — first-true predicate, lower/upper bound, closed vs half-open.

Signs: sorted input, "find the first / smallest / earliest x such that ...",
       O(log n) required, a yes/no question whose answer flips exactly once.
Approach: every binary search is "find the boundary of a monotone predicate".
          Arrange the search space as F F F T T T and keep the invariant
          "answer is in [lo, hi]" with hi a valid "none found" sentinel. Look at
          mid: True means the boundary is at mid or left (hi = mid), False means
          strictly right (lo = mid + 1). The loop ends with lo == hi == answer.
Complexity: O(log n) predicate calls. Total cost = log n x cost(pred).
Gotchas:
  - Pick ONE template and derive the rest. Half-open [lo, hi) with
    `while lo < hi`, `hi = mid`, `lo = mid + 1` never loops forever, because
    mid < hi always, so both branches shrink the range.
  - `lo = mid` (no +1) with mid rounded down loops forever on a 2-element
    range. If you need it, round mid up: mid = (lo + hi + 1) // 2.
  - Closed [lo, hi] with `while lo <= hi` is fine for "find exactly x", but
    boundary questions are easier half-open.
  - Python ints don't overflow; in C/Java write lo + (hi - lo) // 2.
  - `//` floors, so negative ranges are safe in Python. C's `/` truncates
    towards zero: (-3 + 0) / 2 == -1 there, not -2.

Run the tests at the bottom with:  python3 binary_search/templates.py
"""


# ---------------------------------------------------------------- implementation


def first_true(lo, hi, pred):
    """Smallest x in [lo, hi) with pred(x) True, or hi if there is none.

    pred must be monotone over the range: False ... False True ... True.
    This is the one template. Everything below is a call to it.
    """
    while lo < hi:
        mid = (lo + hi) // 2
        if pred(mid):
            hi = mid        # mid might be the answer; keep it
        else:
            lo = mid + 1    # mid is definitely not; drop it
    return lo


def last_true(lo, hi, pred):
    """Largest x in [lo, hi) with pred(x) True, or lo - 1 if there is none.

    pred must be True ... True False ... False. The last True sits just before
    the first False, so flip the predicate and step back one.
    """
    return first_true(lo, hi, lambda x: not pred(x)) - 1


def lower_bound(a, x):
    """First index i with a[i] >= x (len(a) if none). Same as bisect_left."""
    return first_true(0, len(a), lambda i: a[i] >= x)


def upper_bound(a, x):
    """First index i with a[i] > x (len(a) if none). Same as bisect_right."""
    return first_true(0, len(a), lambda i: a[i] > x)


def search_closed(a, x):
    """Index of some occurrence of x in sorted a, or -1. Closed [lo, hi].

    The textbook form: three-way compare, return early on a hit. Good for
    "is it there", useless for "where does the run of x start".
    """
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == x:
            return mid
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def search_half_open(a, x):
    """Index of the FIRST occurrence of x, or -1. Half-open, via lower_bound."""
    i = lower_bound(a, x)
    return i if i < len(a) and a[i] == x else -1


def last_true_round_up(lo, hi, pred):
    """Largest x in [lo, hi] with pred True (pred True ... False), lo - 1 if none.

    The other common template: closed range, `lo = mid`, so mid must round
    UP or a 2-element range never shrinks. Shown for recognition; prefer
    last_true above.
    """
    lo -= 1  # lo is now a sentinel "known True" position (virtual)
    while lo < hi:
        mid = (lo + hi + 1) // 2  # round up: mid > lo, so lo = mid makes progress
        if pred(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


# ------------------------------------------------------------------------ tests


def _random_sorted(rng, n, span):
    return sorted(rng.randint(-span, span) for _ in range(n))


def test_first_true_matches_linear_scan():
    import random

    rng = random.Random(1)
    for _ in range(500):
        lo = rng.randint(-20, 20)
        hi = lo + rng.randint(0, 30)
        cut = rng.randint(lo - 3, hi + 3)  # boundary may sit outside the range
        pred = lambda x, c=cut: x >= c
        expected = next((x for x in range(lo, hi) if pred(x)), hi)
        assert first_true(lo, hi, pred) == expected


def test_last_true_both_templates_match_linear_scan():
    import random

    rng = random.Random(2)
    for _ in range(500):
        lo = rng.randint(-20, 20)
        hi = lo + rng.randint(0, 30)
        cut = rng.randint(lo - 3, hi + 3)
        pred = lambda x, c=cut: x <= c
        expected = max((x for x in range(lo, hi) if pred(x)), default=lo - 1)
        assert last_true(lo, hi, pred) == expected
        # the round-up template works on the closed range [lo, hi - 1]
        assert last_true_round_up(lo, hi - 1, pred) == expected


def test_bounds_match_bisect():
    import random
    from bisect import bisect_left, bisect_right

    rng = random.Random(3)
    for _ in range(500):
        a = _random_sorted(rng, rng.randint(0, 15), 6)
        x = rng.randint(-8, 8)
        assert lower_bound(a, x) == bisect_left(a, x)
        assert upper_bound(a, x) == bisect_right(a, x)


def test_closed_and_half_open_agree_on_membership():
    import random

    rng = random.Random(4)
    for _ in range(500):
        a = _random_sorted(rng, rng.randint(0, 15), 6)
        x = rng.randint(-8, 8)
        i = search_closed(a, x)
        j = search_half_open(a, x)
        if x in a:
            assert a[i] == x                 # some occurrence
            assert j == a.index(x)           # the first occurrence
        else:
            assert i == j == -1


def test_predicate_is_called_log_times():
    calls = []

    def pred(x):
        calls.append(x)
        return x >= 700_000

    assert first_true(0, 10**6, pred) == 700_000
    assert len(calls) <= 20  # ceil(log2(10^6)) == 20


def test_empty_and_single():
    assert lower_bound([], 5) == 0
    assert search_closed([], 5) == -1
    assert search_half_open([5], 5) == 0
    assert search_half_open([5], 4) == -1
    assert first_true(3, 3, lambda x: True) == 3  # empty range returns hi


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
