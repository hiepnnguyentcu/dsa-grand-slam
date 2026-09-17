"""Palindrome DP — substring table, longest palindromic subsequence, min cuts.

Signs: longest palindromic subsequence, minimum cuts to split a string into
       palindromes, count palindromic substrings, "min insertions to make a
       palindrome" (n - LPS).
Approach:
  - Substring table: pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i+1][j-1]).
    The inner cell is a *shorter* span, so fill by length, or i from right to
    left, or (as in min cuts) by right end j.
  - Subsequence: dp[i][j] = dp[i+1][j-1] + 2 if the ends match,
                            else max(dp[i+1][j], dp[i][j-1]).
  - Min cuts: cuts[j] = min over palindromic s[i..j] of cuts[i-1] + 1, and 0 if
    the whole prefix s[0..j] is itself a palindrome.
Complexity: O(n^2) time and space.
Gotchas:
  - Filling i from left to right reads pal[i+1][...] before it exists.
  - LPS is also LCS(s, reversed(s)) — a good cross-check, not a faster method.
  - Longest palindromic *substring* is easier with expand-around-centre in
    O(1) space; the table only pays off when you query it many times.

Run the tests at the bottom with:  python3 dynamic_programming/palindrome_dp.py
"""

import random
from itertools import combinations

from two_sequence import lcs


# ---------------------------------------------------------------- implementation


def palindrome_table(s):
    """pal[i][j] is True iff s[i..j] (inclusive) is a palindrome."""
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1])
    return pal


def count_palindromic_substrings(s):
    return sum(map(sum, palindrome_table(s)))


def longest_pal_subseq(s):
    n = len(s)
    if not n:
        return 0
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1] + 2  # for j == i + 1 this reads the 0 below the diagonal
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]


def min_insertions_to_palindrome(s):
    """Whatever is not in the longest palindromic subsequence needs a mirror."""
    return len(s) - longest_pal_subseq(s)


def min_pal_cuts(s):
    """Fewest cuts so every piece is a palindrome."""
    n = len(s)
    if not n:
        return 0
    pal = [[False] * n for _ in range(n)]
    cuts = [0] * n
    for j in range(n):
        best = j  # cut between every character
        for i in range(j + 1):
            # pal[i+1][j-1] was filled while processing column j - 1
            if s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
                best = 0 if i == 0 else min(best, cuts[i - 1] + 1)
        cuts[j] = best
    return cuts[-1]


# ------------------------------------------------------------------------ tests


def is_pal(t):
    return t == t[::-1]


def brute_min_cuts(s):
    n = len(s)
    best = n
    for mask in range(1 << max(n - 1, 0)):
        cuts = [0] + [i + 1 for i in range(n - 1) if mask >> i & 1] + [n]
        if all(is_pal(s[a:b]) for a, b in zip(cuts, cuts[1:])):
            best = min(best, len(cuts) - 2)
    return best


def rand_str(alpha, lo, hi):
    return "".join(random.choice(alpha) for _ in range(random.randint(lo, hi)))


def test_classic():
    assert longest_pal_subseq("bbbab") == 4
    assert longest_pal_subseq("cbbd") == 2
    assert longest_pal_subseq("") == 0
    assert count_palindromic_substrings("abc") == 3
    assert count_palindromic_substrings("aaa") == 6
    assert min_pal_cuts("aab") == 1
    assert min_pal_cuts("a") == 0
    assert min_pal_cuts("ab") == 1
    assert min_pal_cuts("") == 0
    assert min_insertions_to_palindrome("mbadm") == 2
    assert min_insertions_to_palindrome("leetcode") == 5


def test_table_matches_slicing():
    random.seed(70)
    for _ in range(200):
        s = rand_str("ab", 0, 12)
        pal = palindrome_table(s)
        for i in range(len(s)):
            for j in range(i, len(s)):
                assert pal[i][j] == is_pal(s[i:j + 1])


def test_lps_matches_brute_force_and_lcs():
    random.seed(71)
    for _ in range(300):
        s = rand_str("abc", 0, 10)
        brute = max(
            k for k in range(len(s) + 1)
            for c in combinations(s, k) if is_pal(c)
        )
        assert longest_pal_subseq(s) == brute == lcs(s, s[::-1])


def test_min_cuts_matches_brute_force():
    random.seed(72)
    for _ in range(300):
        s = rand_str("ab", 0, 11)
        assert min_pal_cuts(s) == brute_min_cuts(s), s


def test_left_to_right_fill_is_the_trap():
    # Filling i ascending reads pal[i+1][j-1] while it is still False.
    def wrong_table(s):
        n = len(s)
        pal = [[False] * n for _ in range(n)]
        for i in range(n):
            for j in range(i, n):
                pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1])
        return pal

    assert palindrome_table("aba")[0][2]
    assert not wrong_table("aba")[0][2]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
