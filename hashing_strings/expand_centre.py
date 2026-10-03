"""Expand around centre — longest palindromic substring, count palindromes.

Signs: "longest palindromic SUBSTRING" (contiguous), "how many palindromic
       substrings", n up to a few thousand, O(1) extra space wanted.
Approach: every palindrome has a centre: a char (odd length) or the gap
          between two chars (even length). There are 2n - 1 centres. From
          each, grow lo -= 1, hi += 1 while s[lo] == s[hi]. Each successful
          step is one more palindrome, so counting is the same loop.
Complexity: O(n^2) time worst case ("aaaa..."), O(1) space. The DP table is
            also O(n^2) but needs O(n^2) memory; Manacher is O(n) but rarely
            expected.
Gotchas:
  - Do BOTH centres: expand(i, i) and expand(i, i + 1). Forgetting the even
    case misses "abba".
  - After the loop lo and hi have gone one step too far: the palindrome is
    s[lo + 1:hi], length hi - lo - 1.
  - Subsequence (not substring) palindromes need DP:
    dynamic_programming/palindrome_dp.py. Palindrome check with one deletion:
    sliding_window/opposite_ends.py.

Run the tests at the bottom with:  python3 hashing_strings/expand_centre.py
"""


# ---------------------------------------------------------------- implementation


def _expand(s, lo, hi):
    """Grow from (lo, hi) while it stays a palindrome; return the final bounds."""
    while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
        lo, hi = lo - 1, hi + 1
    return lo + 1, hi          # s[lo + 1:hi] is the palindrome


def longest_palindrome(s):
    """LC 5. Leftmost longest palindromic substring."""
    best = (0, 0)
    for i in range(len(s)):
        for lo, hi in (_expand(s, i, i), _expand(s, i, i + 1)):
            if hi - lo > best[1] - best[0]:
                best = (lo, hi)
    return s[best[0]:best[1]]


def count_palindromes(s):
    """LC 647. Number of palindromic substrings (by position)."""
    total = 0
    for c in range(2 * len(s) - 1):           # centre c: char c//2, or gap after it
        lo, hi = c // 2, c // 2 + c % 2
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            total += 1
            lo, hi = lo - 1, hi + 1
    return total


def longest_palindrome_manacher(s):
    """O(n) Manacher, for reference: same answer as longest_palindrome."""
    t = "^#" + "#".join(s) + "#$"             # sentinels: no bounds checks needed
    p = [0] * len(t)                          # p[i] = radius around t[i]
    centre = right = 0
    for i in range(1, len(t) - 1):
        if i < right:
            p[i] = min(right - i, p[2 * centre - i])   # mirror's radius, capped
        while t[i + p[i] + 1] == t[i - p[i] - 1]:
            p[i] += 1
        if i + p[i] > right:
            centre, right = i, i + p[i]
    if not s:
        return ""
    r, i = max((r, -i) for i, r in enumerate(p))
    start = (-i - r) // 2
    return s[start:start + r]


# ------------------------------------------------------------------------ tests


def _is_pal(t):
    return t == t[::-1]


def _brute_longest(s):
    best = ""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if j - i > len(best) and _is_pal(s[i:j]):
                best = s[i:j]
    return best


def test_examples():
    assert longest_palindrome("babad") == "bab"
    assert longest_palindrome("cbbd") == "bb"     # even centre
    assert longest_palindrome("") == ""
    assert count_palindromes("abc") == 3
    assert count_palindromes("aaa") == 6


def test_longest_matches_brute_force_and_manacher():
    import random

    rng = random.Random(1)
    for _ in range(500):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 14)))
        expect = _brute_longest(s)
        assert longest_palindrome(s) == expect
        assert longest_palindrome_manacher(s) == expect


def test_count_matches_brute_force():
    import random

    rng = random.Random(2)
    for _ in range(500):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 14)))
        expect = sum(_is_pal(s[i:j]) for i in range(len(s)) for j in range(i + 1, len(s) + 1))
        assert count_palindromes(s) == expect


def test_worst_case_all_same_char():
    s = "a" * 300
    assert longest_palindrome(s) == s
    assert count_palindromes(s) == 300 * 301 // 2


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
