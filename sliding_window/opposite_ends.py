"""Two pointers from opposite ends — pair sums, k-sum, container, palindromes.

Signs: sorted input (or you may sort), "pair / triplet that sums to target",
       "closest sum", "max area between two lines", palindrome checks,
       squares of a sorted array, O(1) extra space wanted.
Approach: lo at the start, hi at the end. Look at the pair, then move the ONE
          pointer whose move can still help: sum too small -> lo += 1 (the
          only way up), too big -> hi -= 1. Each step discards a whole row of
          pairs that provably cannot be the answer, so n steps cover all n^2.
          k-sum = fix the first k-2 values in loops, two-pointer the rest.
Complexity: O(n) per two-pointer pass; 3sum O(n^2), 4sum O(n^3), plus the
            O(n log n) sort.
Gotchas:
  - Needs sorted order (or a monotone quantity like width). On unsorted
    input with "return indices", use a hash map instead of sorting.
  - Unique triplets: skip duplicate anchors (i > 0 and a[i] == a[i-1]) and
    skip duplicates after a hit, on BOTH pointers.
  - Container: move the SHORTER line. Moving the taller one can only shrink
    width without raising the min height.
  - Valid palindrome II: one mismatch allowed -> try skipping either side,
    once. Recursing with more skips is exponential.
  - Trapping rain water is the same pattern; it lives with its stack twin in
    stacks_heaps/histogram.py (trap_two_pointers).

Run the tests at the bottom with:  python3 sliding_window/opposite_ends.py
"""


# ---------------------------------------------------------------- implementation


def two_sum_sorted(a, target):
    """LC 167. 1-based indices [i, j] of a pair summing to target, or []."""
    lo, hi = 0, len(a) - 1
    while lo < hi:
        s = a[lo] + a[hi]
        if s == target:
            return [lo + 1, hi + 1]
        if s < target:
            lo += 1   # a[lo] + anything left of hi is too small: drop a[lo]
        else:
            hi -= 1   # a[hi] + anything right of lo is too big: drop a[hi]
    return []


def three_sum(a):
    """LC 15. All unique triplets summing to 0, each sorted, list sorted."""
    a = sorted(a)
    n, out = len(a), []
    for i in range(n - 2):
        if i > 0 and a[i] == a[i - 1]:
            continue          # same anchor -> same triplets
        if a[i] > 0:
            break             # smallest value positive: nothing sums to 0
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = a[i] + a[lo] + a[hi]
            if s < 0:
                lo += 1
            elif s > 0:
                hi -= 1
            else:
                out.append([a[i], a[lo], a[hi]])
                lo += 1
                hi -= 1
                while lo < hi and a[lo] == a[lo - 1]:
                    lo += 1
                while lo < hi and a[hi] == a[hi + 1]:
                    hi -= 1
    return out


def three_sum_closest(a, target):
    """LC 16. The triplet sum closest to target (len(a) >= 3)."""
    a = sorted(a)
    best = a[0] + a[1] + a[2]
    for i in range(len(a) - 2):
        lo, hi = i + 1, len(a) - 1
        while lo < hi:
            s = a[i] + a[lo] + a[hi]
            if abs(s - target) < abs(best - target):
                best = s
            if s == target:
                return s
            if s < target:
                lo += 1
            else:
                hi -= 1
    return best


def k_sum(a, target, k):
    """All unique k-tuples summing to target (LC 18 is k = 4). Sorted output.

    Recurse down to k == 2, then two pointers. Duplicates are skipped at every
    level by the same `a[i] == a[i-1]` rule.
    """
    a = sorted(a)

    def go(start, k, target):
        out = []
        if k == 2:
            lo, hi = start, len(a) - 1
            while lo < hi:
                s = a[lo] + a[hi]
                if s < target or (lo > start and a[lo] == a[lo - 1]):
                    lo += 1
                elif s > target or (hi < len(a) - 1 and a[hi] == a[hi + 1]):
                    hi -= 1
                else:
                    out.append([a[lo], a[hi]])
                    lo += 1
                    hi -= 1
            return out
        for i in range(start, len(a) - k + 1):
            if i > start and a[i] == a[i - 1]:
                continue
            for rest in go(i + 1, k - 1, target - a[i]):
                out.append([a[i]] + rest)
        return out

    return go(0, k, target)


def four_sum(a, target):
    """LC 18."""
    return k_sum(a, target, 4)


def max_area(h):
    """LC 11. Container with most water."""
    lo, hi, best = 0, len(h) - 1, 0
    while lo < hi:
        best = max(best, (hi - lo) * min(h[lo], h[hi]))
        if h[lo] < h[hi]:
            lo += 1   # h[lo] is the bottleneck for every narrower container
        else:
            hi -= 1
    return best


def is_palindrome_alnum(s):
    """LC 125. Ignore non-alphanumerics and case."""
    lo, hi = 0, len(s) - 1
    while lo < hi:
        if not s[lo].isalnum():
            lo += 1
        elif not s[hi].isalnum():
            hi -= 1
        elif s[lo].lower() != s[hi].lower():
            return False
        else:
            lo, hi = lo + 1, hi - 1
    return True


def valid_palindrome_one_delete(s):
    """LC 680. Palindrome after deleting at most one character."""

    def is_pal(lo, hi):
        while lo < hi:
            if s[lo] != s[hi]:
                return False
            lo, hi = lo + 1, hi - 1
        return True

    lo, hi = 0, len(s) - 1
    while lo < hi:
        if s[lo] != s[hi]:
            return is_pal(lo + 1, hi) or is_pal(lo, hi - 1)  # the one skip
        lo, hi = lo + 1, hi - 1
    return True


def sorted_squares(a):
    """LC 977. Squares of a sorted array, sorted. Largest square is at an end."""
    n = len(a)
    out = [0] * n
    lo, hi = 0, n - 1
    for w in range(n - 1, -1, -1):  # fill from the back, biggest first
        if abs(a[lo]) > abs(a[hi]):
            out[w] = a[lo] * a[lo]
            lo += 1
        else:
            out[w] = a[hi] * a[hi]
            hi -= 1
    return out


# ------------------------------------------------------------------------ tests


def _brute_k_sum(a, target, k):
    from itertools import combinations

    return sorted({tuple(sorted(c)) for c in combinations(a, k) if sum(c) == target})


def test_examples():
    assert two_sum_sorted([2, 7, 11, 15], 9) == [1, 2]
    assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
    assert three_sum_closest([-1, 2, 1, -4], 1) == 2
    assert four_sum([1, 0, -1, 0, -2, 2], 0) == [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]
    assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert valid_palindrome_one_delete("abca") and not valid_palindrome_one_delete("abc")
    assert is_palindrome_alnum("A man, a plan, a canal: Panama")
    assert sorted_squares([-4, -1, 0, 3, 10]) == [0, 1, 9, 16, 100]


def test_two_sum_matches_brute_force():
    import random

    rng = random.Random(1)
    for _ in range(500):
        a = sorted(rng.randint(-10, 10) for _ in range(rng.randint(0, 12)))
        t = rng.randint(-20, 20)
        got = two_sum_sorted(a, t)
        exists = any(a[i] + a[j] == t for i in range(len(a)) for j in range(i + 1, len(a)))
        if exists:
            i, j = got
            assert i < j and a[i - 1] + a[j - 1] == t
        else:
            assert got == []


def test_k_sum_matches_brute_force():
    import random

    rng = random.Random(2)
    for _ in range(300):
        a = [rng.randint(-5, 5) for _ in range(rng.randint(0, 10))]
        assert [tuple(x) for x in three_sum(a)] == _brute_k_sum(a, 0, 3)
        t = rng.randint(-6, 6)
        assert [tuple(x) for x in four_sum(a, t)] == _brute_k_sum(a, t, 4)


def test_three_sum_closest_matches_brute_force():
    import random
    from itertools import combinations

    rng = random.Random(3)
    for _ in range(300):
        a = [rng.randint(-20, 20) for _ in range(rng.randint(3, 10))]
        t = rng.randint(-40, 40)
        best = min(abs(sum(c) - t) for c in combinations(a, 3))
        assert abs(three_sum_closest(a, t) - t) == best


def test_max_area_matches_brute_force():
    import random

    rng = random.Random(4)
    for _ in range(300):
        h = [rng.randint(0, 20) for _ in range(rng.randint(2, 15))]
        brute = max((j - i) * min(h[i], h[j]) for i in range(len(h)) for j in range(i + 1, len(h)))
        assert max_area(h) == brute


def test_palindromes_match_brute_force():
    import random

    rng = random.Random(5)
    for _ in range(500):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 9)))
        brute = s == s[::-1] or any((t := s[:i] + s[i + 1:]) == t[::-1] for i in range(len(s)))
        assert valid_palindrome_one_delete(s) == brute
        noisy = "".join(c + rng.choice(["", " ", ",", "!"]) for c in s)
        noisy = "".join(c.upper() if rng.random() < 0.5 else c for c in noisy)
        assert is_palindrome_alnum(noisy) == (s == s[::-1])


def test_sorted_squares_matches_sort():
    import random

    rng = random.Random(6)
    for _ in range(300):
        a = sorted(rng.randint(-10, 10) for _ in range(rng.randint(0, 12)))
        assert sorted_squares(a) == sorted(x * x for x in a)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
