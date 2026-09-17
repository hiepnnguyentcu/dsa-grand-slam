"""Pattern matching DP — wildcard (? and *) and regex (. and x*).

Signs: match a whole string against a pattern with `?`/`*` wildcards or
       `.`/`x*` regex operators.
Approach: dp[i][j] = does s[:i] match p[:j].
  - Wildcard `*` matches any run: dp[i][j] = dp[i][j-1]   (* matches empty)
                                          or dp[i-1][j]   (* eats s[i-1] and
                                                           stays available)
  - Regex `x*` is zero or more of x, and the star belongs to the char before:
        dp[i][j] = dp[i][j-2]                               (zero copies)
                or (x matches s[i-1] and dp[i-1][j])        (one more copy)
  - Row 0 (empty s): only patterns made entirely of `*` (wildcard) or of
    `x*` pairs (regex) match it. Forgetting this row is the classic bug.
Complexity: O(m * n) time and space.
Gotchas:
  - Regex `*` never stands alone; a leading `*` is malformed, so it is
    rejected up front rather than silently reading p[-1].
  - The match is anchored at both ends — "aa" does not match "a".
  - Wildcard `*` and regex `.*` behave the same; wildcard `*` and regex `*`
    do not.

Run the tests at the bottom with:  python3 dynamic_programming/pattern_matching.py
"""

import fnmatch
import random
import re
from functools import cache


# ---------------------------------------------------------------- implementation


def wildcard_match(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):
        if p[j - 1] == "*":
            dp[0][j] = dp[0][j - 1]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == "*":
                dp[i][j] = dp[i][j - 1] or dp[i - 1][j]
            elif p[j - 1] in ("?", s[i - 1]):
                dp[i][j] = dp[i - 1][j - 1]
    return dp[m][n]


def regex_match(s, p):
    """Full match of s against p, where p uses only '.' and 'x*'."""
    if p.startswith("*") or "**" in p:
        raise ValueError(f"malformed pattern: {p!r}")
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(2, n + 1):
        if p[j - 1] == "*":
            dp[0][j] = dp[0][j - 2]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == "*":
                dp[i][j] = dp[i][j - 2] or (p[j - 2] in (".", s[i - 1]) and dp[i - 1][j])
            else:
                dp[i][j] = p[j - 1] in (".", s[i - 1]) and dp[i - 1][j - 1]
    return dp[m][n]


def regex_match_top_down(s, p):
    """Same recurrence read left to right with memoisation — often easier to
    get right first in an interview, then convert."""
    @cache
    def f(i, j):
        if j == len(p):
            return i == len(s)
        first = i < len(s) and p[j] in (".", s[i])
        if j + 1 < len(p) and p[j + 1] == "*":
            return f(i, j + 2) or (first and f(i + 1, j))
        return first and f(i + 1, j + 1)

    return f(0, 0)


# ------------------------------------------------------------------------ tests


def rand_str(alpha, lo, hi):
    return "".join(random.choice(alpha) for _ in range(random.randint(lo, hi)))


def rand_regex():
    out = []
    for _ in range(random.randint(0, 4)):
        out.append(random.choice("ab."))
        if random.random() < 0.4:
            out.append("*")
    return "".join(out)


def test_wildcard_classic():
    assert not wildcard_match("aa", "a")
    assert wildcard_match("aa", "*")
    assert not wildcard_match("cb", "?a")
    assert wildcard_match("adceb", "*a*b")
    assert not wildcard_match("acdcb", "a*c?b")
    assert wildcard_match("", "***")
    assert not wildcard_match("", "?")


def test_regex_classic():
    assert not regex_match("aa", "a")
    assert regex_match("aa", "a*")
    assert regex_match("ab", ".*")
    assert regex_match("aab", "c*a*b")
    assert not regex_match("mississippi", "mis*is*p*.")
    assert regex_match("", "a*b*.*")
    assert not regex_match("", ".")


def test_wildcard_matches_fnmatch():
    # fnmatchcase implements the same ? and * semantics (no [] used here).
    random.seed(40)
    for _ in range(2000):
        s, p = rand_str("ab", 0, 7), rand_str("ab?*", 0, 6)
        assert wildcard_match(s, p) == fnmatch.fnmatchcase(s, p), (s, p)


def test_regex_matches_re_module():
    random.seed(41)
    for _ in range(2000):
        s, p = rand_str("ab", 0, 7), rand_regex()
        expected = re.fullmatch(p, s) is not None
        assert regex_match(s, p) == expected, (s, p)
        assert regex_match_top_down(s, p) == expected, (s, p)


def test_empty_string_base_row():
    # Without the row-0 initialisation these all come out False.
    assert regex_match("", "a*")
    assert regex_match("", "a*.*b*")
    assert not regex_match("", "a*b")
    assert wildcard_match("", "*")
    assert not wildcard_match("", "*a")


def test_star_means_different_things():
    assert wildcard_match("xyz", "*")
    assert not regex_match("xyz", "x*")  # x* is only x's
    assert regex_match("xyz", ".*")


def test_malformed_regex_rejected():
    for bad in ("*a", "a**"):
        try:
            regex_match("a", bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{bad!r} should be rejected")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
