"""Two-sequence DP — LCS, edit distance, distinct subsequences, interleaving.

Signs: compare two strings, longest common subsequence, minimum edits or
       deletions to turn one into the other, count occurrences of t as a
       subsequence of s, "is c an interleaving of a and b".
Approach: dp[i][j] = answer for the prefixes a[:i] and b[:j]. Row 0 and column
          0 are the empty prefixes, which is what makes the base cases trivial.
          Each cell looks at the last characters a[i-1], b[j-1]:
            LCS:   match -> dp[i-1][j-1] + 1, else max(dp[i-1][j], dp[i][j-1])
            Edit:  match -> dp[i-1][j-1],
                   else 1 + min(delete dp[i-1][j], insert dp[i][j-1],
                                replace dp[i-1][j-1])
            Count: dp[i][j] = dp[i-1][j] + (dp[i-1][j-1] if they match)
Complexity: O(m * n) time; O(min(m, n)) space with a rolling row.
Gotchas:
  - Off-by-one: dp is (m+1) x (n+1) and cell (i, j) compares a[i-1], b[j-1].
  - Rolling rows lose dp[i-1][j-1] once cur[j-1] is written. Either keep two
    lists (prev, cur) or save the diagonal in a variable before overwriting.
  - 1D count of subsequences must iterate j *backwards* — same reason as 0/1
    knapsack: each character of s may be used once per placement.
  - Edit distance base row is dp[0][j] = j (insert j chars), not 0.

Run the tests at the bottom with:  python3 dynamic_programming/two_sequence.py
"""

import random
from functools import cache
from itertools import combinations


# ---------------------------------------------------------------- implementation


def lcs(a, b):
    """Length of the longest common subsequence."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def lcs_string(a, b):
    """One actual LCS, recovered by walking the full table back from (m, n)."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    out, i, j = [], m, n
    while i and j:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i, j = i - 1, j - 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(out))


def lcs_rolling(a, b):
    """LCS in O(min(m, n)) space, keeping the diagonal in a variable."""
    if len(a) < len(b):
        a, b = b, a
    row = [0] * (len(b) + 1)
    for x in a:
        diag = 0  # dp[i-1][j-1]
        for j in range(1, len(b) + 1):
            above = row[j]
            row[j] = diag + 1 if x == b[j - 1] else max(above, row[j - 1])
            diag = above
    return row[-1]


def edit_distance(a, b):
    """Levenshtein distance (insert, delete, replace each cost 1)."""
    m, n = len(a), len(b)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return prev[n]


def min_delete_to_equal(a, b):
    """Fewest deletions from both strings to make them equal.

    Whatever survives is a common subsequence, so keep the longest one.
    """
    return len(a) + len(b) - 2 * lcs(a, b)


def count_subsequence_occurrences(s, t):
    """How many index sets of s spell t (distinct subsequences)."""
    dp = [1] + [0] * len(t)  # dp[j] = ways to form t[:j] so far
    for ch in s:
        for j in range(len(t), 0, -1):  # backwards: ch is used at most once
            if ch == t[j - 1]:
                dp[j] += dp[j - 1]
    return dp[-1]


def is_interleave(a, b, c):
    """Is c formed by merging a and b while keeping each one's order?"""
    m, n = len(a), len(b)
    if m + n != len(c):
        return False
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for i in range(m + 1):
        for j in range(n + 1):
            if i and a[i - 1] == c[i + j - 1] and dp[i - 1][j]:
                dp[i][j] = True
            if j and b[j - 1] == c[i + j - 1] and dp[i][j - 1]:
                dp[i][j] = True
    return dp[m][n]


# ------------------------------------------------------------------------ tests


def subseqs(s):
    return {"".join(c) for k in range(len(s) + 1) for c in combinations(s, k)}


@cache
def edit_brute(a, b):
    """Plain recursion on the first characters — no table to get wrong."""
    if not a or not b:
        return len(a) + len(b)
    if a[0] == b[0]:
        return edit_brute(a[1:], b[1:])
    return 1 + min(edit_brute(a[1:], b), edit_brute(a, b[1:]), edit_brute(a[1:], b[1:]))


def rand_str(alpha, lo, hi):
    return "".join(random.choice(alpha) for _ in range(random.randint(lo, hi)))


def test_classic():
    assert lcs("abcde", "ace") == 3
    assert lcs("abc", "def") == 0
    assert edit_distance("horse", "ros") == 3
    assert edit_distance("intention", "execution") == 5
    assert edit_distance("", "abc") == 3
    assert min_delete_to_equal("sea", "eat") == 2
    assert count_subsequence_occurrences("rabbbit", "rabbit") == 3
    assert count_subsequence_occurrences("babgbag", "bag") == 5
    assert count_subsequence_occurrences("abc", "") == 1
    assert is_interleave("aabcc", "dbbca", "aadbbcbcac")
    assert not is_interleave("aabcc", "dbbca", "aadbbbaccc")
    assert is_interleave("", "", "")


def test_lcs_matches_brute_force():
    random.seed(30)
    for _ in range(300):
        a, b = rand_str("abc", 0, 8), rand_str("abc", 0, 8)
        best = max(len(s) for s in subseqs(a) & subseqs(b))
        assert lcs(a, b) == lcs_rolling(a, b) == best
        got = lcs_string(a, b)
        assert len(got) == best and got in subseqs(a) and got in subseqs(b)


def test_edit_distance_matches_recursion():
    random.seed(31)
    for _ in range(300):
        a, b = rand_str("abc", 0, 8), rand_str("abc", 0, 8)
        d = edit_distance(a, b)
        assert d == edit_brute(a, b)
        assert d == edit_distance(b, a)  # symmetric
        assert abs(len(a) - len(b)) <= d <= max(len(a), len(b))


def test_count_subsequences_matches_brute_force():
    random.seed(32)
    for _ in range(300):
        s, t = rand_str("ab", 0, 10), rand_str("ab", 0, 3)
        brute = sum(
            1 for idx in combinations(range(len(s)), len(t))
            if "".join(s[i] for i in idx) == t
        )
        assert count_subsequence_occurrences(s, t) == brute


def test_forward_rolling_count_is_the_trap():
    # Forward j lets one 'a' of s fill both t[0] and t[1].
    def wrong(s, t):
        dp = [1] + [0] * len(t)
        for ch in s:
            for j in range(1, len(t) + 1):
                if ch == t[j - 1]:
                    dp[j] += dp[j - 1]
        return dp[-1]

    assert count_subsequence_occurrences("a", "aa") == 0
    assert wrong("a", "aa") == 1


def test_interleave_matches_brute_force():
    random.seed(33)
    for _ in range(300):
        a, b = rand_str("ab", 0, 5), rand_str("ab", 0, 5)
        n = len(a) + len(b)
        merges = set()
        for pos in combinations(range(n), len(a)):  # where a's chars go
            ita, itb, ps = iter(a), iter(b), set(pos)
            merges.add("".join(next(ita) if k in ps else next(itb) for k in range(n)))
        for c in list(merges)[:5]:
            assert is_interleave(a, b, c)
        c = rand_str("ab", n, n)
        assert is_interleave(a, b, c) == (c in merges)
        assert not is_interleave(a, b, c + "a")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
