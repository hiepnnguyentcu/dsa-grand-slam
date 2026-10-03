"""Variable window, shortest valid — grow until valid, shrink while still valid.

Signs: "minimum length subarray with sum >= target", "smallest substring
       containing all of t", "shortest window covering ...". Validity must be
       monotone the OTHER way: if a window is valid, every window containing
       it is valid too.
Approach: for each right, add a[right]; then WHILE the window is valid,
          record its length and shrink from the left. The answer is recorded
          inside the loop — the opposite of longest-valid.
              for right, x in enumerate(a):
                  add(x)
                  while valid(): best = min(best, right - left + 1)
                                 remove(a[left]); left += 1
          Coverage check: keep `missing` = chars of t still unmatched; valid
          iff missing == 0, so each step is O(1).
Complexity: O(n + m) time; O(alphabet) space.
Gotchas:
  - Sentinel for "no window": inf, mapped to 0 or "" at the end.
  - Min window substring: only count a char toward `missing` while the
    window still needs it (need[c] > 0 before decrementing). Surplus copies
    go negative and are given back first when shrinking.
  - Negative numbers break "sum >= target" monotonicity. Use prefix sums +
    monotonic deque: stacks_heaps/monotonic_deque.py
    (shortest_subarray_at_least).
  - Positive values + many queries for different targets: prefix sums are
    sorted, so binary search works too (see binary_search/).

Run the tests at the bottom with:  python3 sliding_window/shortest_window.py
"""

from collections import Counter


# ---------------------------------------------------------------- implementation


def min_subarray_len(target, a):
    """LC 209. Shortest subarray with sum >= target (positive a); 0 if none."""
    left = s = 0
    best = float("inf")
    for right, x in enumerate(a):
        s += x
        while s >= target:
            best = min(best, right - left + 1)
            s -= a[left]
            left += 1
    return 0 if best == float("inf") else best


def min_window(s, t):
    """LC 76. Smallest substring of s containing every char of t (with
    multiplicity); "" if none. Ties -> leftmost."""
    if not t:
        return ""
    need = Counter(t)          # need[c] > 0: window still short of c
    missing = len(t)
    left = 0
    best = (float("inf"), 0, 0)
    for right, c in enumerate(s):
        if need[c] > 0:
            missing -= 1
        need[c] -= 1
        while missing == 0:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right + 1)
            d = s[left]
            need[d] += 1
            if need[d] > 0:    # gave back a char the window needed
                missing += 1
            left += 1
    return s[best[1]:best[2]] if best[0] != float("inf") else ""


def shortest_with_k_distinct(a, k):
    """Shortest window containing at least k distinct values; 0 if none."""
    count = Counter()
    left = 0
    best = float("inf")
    for right, x in enumerate(a):
        count[x] += 1
        while len(count) >= k:
            best = min(best, right - left + 1)
            count[a[left]] -= 1
            if count[a[left]] == 0:
                del count[a[left]]
            left += 1
    return 0 if best == float("inf") else best


# ------------------------------------------------------------------------ tests


def _brute_shortest(a, valid):
    n = len(a)
    return min([j - i for i in range(n) for j in range(i + 1, n + 1) if valid(a[i:j])], default=0)


def _brute_min_window(s, t):
    need = Counter(t)
    best = ""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if not need - Counter(s[i:j]) and (not best or j - i < len(best)):
                best = s[i:j]
    return best


def test_examples():
    assert min_subarray_len(7, [2, 3, 1, 2, 4, 3]) == 2
    assert min_subarray_len(11, [1, 1, 1]) == 0
    assert min_window("ADOBECODEBANC", "ABC") == "BANC"
    assert min_window("a", "aa") == ""
    assert shortest_with_k_distinct([1, 2, 1, 1, 3], 3) == 4


def test_min_subarray_matches_brute_force():
    import random

    rng = random.Random(1)
    for _ in range(500):
        a = [rng.randint(1, 8) for _ in range(rng.randint(0, 12))]
        t = rng.randint(1, 30)
        assert min_subarray_len(t, a) == _brute_shortest(a, lambda w: sum(w) >= t)


def test_min_window_matches_brute_force():
    import random

    rng = random.Random(2)
    for _ in range(500):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 10)))
        t = "".join(rng.choice("abc") for _ in range(rng.randint(1, 3)))
        assert min_window(s, t) == _brute_min_window(s, t)


def test_k_distinct_matches_brute_force():
    import random

    rng = random.Random(3)
    for _ in range(500):
        a = [rng.randint(0, 4) for _ in range(rng.randint(0, 12))]
        k = rng.randint(1, 4)
        assert shortest_with_k_distinct(a, k) == _brute_shortest(a, lambda w: len(set(w)) >= k)


def test_negative_values_break_the_window():
    # [1, -5, 6]: [6] alone reaches 6, but the -5 keeps the running sum at 2,
    # so the window never turns valid and never gets to shrink.
    a, t = [1, -5, 6], 6
    assert _brute_shortest(a, lambda w: sum(w) >= t) == 1
    assert min_subarray_len(t, a) != 1


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
