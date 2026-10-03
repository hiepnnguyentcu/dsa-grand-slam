"""Variable window, longest valid — grow right, shrink left while invalid.

Signs: "longest substring / subarray such that ...", "at most k distinct",
       "at most k flips / replacements", "no repeating characters", fruit
       into baskets. Validity must be MONOTONE: if a window is valid, every
       window inside it is valid too.
Approach: for each right, add a[right]; while the window breaks the rule,
          remove a[left] and left += 1; then [left, right] is the longest
          valid window ending at right — record right - left + 1.
          Template:
              for right, x in enumerate(a):
                  add(x)
                  while invalid(): remove(a[left]); left += 1
                  best = max(best, right - left + 1)
Complexity: O(n) — left and right each move at most n times.
Gotchas:
  - Shrink with `while`, not `if` (except the replacement trick below).
  - Character replacement (LC 424): valid iff len - max_freq <= k. max_freq
    never needs to decrease: a smaller max can't produce a longer answer, so
    a stale max only keeps the window from shrinking. Here `if` suffices.
  - "Without repeats" can jump left straight past the last occurrence:
    left = max(left, last[c] + 1). The max() matters — last[c] may be stale.
  - Validity not monotone (e.g. sum == k with negatives)? A window won't
    work: use prefix sums + hash map (see counting.py, subarray_sum_equals_k).
  - Window rule depends on max - min? Needs a monotonic deque:
    stacks_heaps/monotonic_deque.py (longest_subarray_within_limit).

Run the tests at the bottom with:  python3 sliding_window/longest_window.py
"""

from collections import defaultdict


# ---------------------------------------------------------------- implementation


def longest_no_repeat(s):
    """LC 3. Longest substring with all-distinct characters."""
    last = {}
    left = best = 0
    for right, c in enumerate(s):
        if c in last:
            left = max(left, last[c] + 1)   # jump past the previous copy
        last[c] = right
        best = max(best, right - left + 1)
    return best


def longest_at_most_k_distinct(a, k):
    """LC 340. Longest window with at most k distinct values."""
    count = defaultdict(int)
    left = best = 0
    for right, x in enumerate(a):
        count[x] += 1
        while len(count) > k:
            count[a[left]] -= 1
            if count[a[left]] == 0:
                del count[a[left]]          # keep len(count) == distinct
            left += 1
        best = max(best, right - left + 1)
    return best


def total_fruit(fruits):
    """LC 904. Fruit into baskets == longest window with <= 2 distinct."""
    return longest_at_most_k_distinct(fruits, 2)


def character_replacement(s, k):
    """LC 424. Longest window that becomes one repeated char after <= k edits."""
    count = defaultdict(int)
    left = max_freq = best = 0
    for right, c in enumerate(s):
        count[c] += 1
        max_freq = max(max_freq, count[c])
        if right - left + 1 - max_freq > k:  # `if`: window slides, never shrinks
            count[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


def longest_ones(a, k):
    """LC 1004. Max consecutive 1s if you may flip at most k zeros."""
    left = zeros = best = 0
    for right, x in enumerate(a):
        zeros += x == 0
        while zeros > k:
            zeros -= a[left] == 0
            left += 1
        best = max(best, right - left + 1)
    return best


def longest_sum_at_most(a, limit):
    """Longest subarray with sum <= limit, NON-NEGATIVE values only.

    Non-negative values make validity monotone (a sub-window's sum can only
    be smaller). With negatives this is wrong — see the test.
    """
    left = s = best = 0
    for right, x in enumerate(a):
        s += x
        while s > limit:
            s -= a[left]
            left += 1
        best = max(best, right - left + 1)
    return best


# ------------------------------------------------------------------------ tests


def _brute_longest(a, valid):
    n = len(a)
    return max([j - i for i in range(n) for j in range(i + 1, n + 1) if valid(a[i:j])], default=0)


def test_examples():
    assert longest_no_repeat("abcabcbb") == 3
    assert longest_no_repeat("abba") == 2       # stale last[] needs the max()
    assert longest_at_most_k_distinct("eceba", 2) == 3
    assert total_fruit([1, 2, 3, 2, 2]) == 4
    assert character_replacement("AABABBA", 1) == 4
    assert longest_ones([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2) == 6


def test_string_windows_match_brute_force():
    import random

    rng = random.Random(1)
    for _ in range(400):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 12)))
        k = rng.randint(0, 3)
        assert longest_no_repeat(s) == _brute_longest(s, lambda w: len(set(w)) == len(w))
        assert longest_at_most_k_distinct(s, k) == _brute_longest(s, lambda w: len(set(w)) <= k)
        assert character_replacement(s, k) == _brute_longest(
            s, lambda w: len(w) - max(w.count(c) for c in set(w)) <= k)


def test_array_windows_match_brute_force():
    import random

    rng = random.Random(2)
    for _ in range(400):
        a = [rng.randint(0, 1) for _ in range(rng.randint(0, 12))]
        k = rng.randint(0, 3)
        assert longest_ones(a, k) == _brute_longest(a, lambda w: w.count(0) <= k)
        b = [rng.randint(0, 6) for _ in range(rng.randint(0, 12))]
        lim = rng.randint(0, 15)
        assert longest_sum_at_most(b, lim) == _brute_longest(b, lambda w: sum(w) <= lim)
        f = [rng.randint(0, 3) for _ in range(rng.randint(0, 12))]
        assert total_fruit(f) == _brute_longest(f, lambda w: len(set(w)) <= 2)


def test_negative_values_break_the_window():
    # [5, -10, 5]: whole array sums to 0 <= 0, but the window drops 5 at once.
    a, lim = [5, -10, 5], 0
    assert _brute_longest(a, lambda w: sum(w) <= lim) == 3
    assert longest_sum_at_most(a, lim) != 3


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
