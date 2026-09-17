"""String prefix DP — decode ways and word break.

Signs: number of ways to decode/split a string, "can s be segmented into
       dictionary words", fewest pieces, each step consumes a chunk of the
       string subject to validity rules.
Approach: dp[i] = answer for the prefix s[:i]. Look at the *last* chunk that
          ends at i: for decoding it is 1 or 2 characters long, for word break
          it is any dictionary word. dp[i] combines dp[i - len(chunk)] over the
          valid chunks — OR for "possible", + for "how many", min for "fewest".
Complexity: decode O(n); word break O(n * L) substring checks, L = longest word
            (each check itself costs O(L) to slice and hash).
Gotchas:
  - '0' cannot be decoded on its own, and "06" is not a valid two-char chunk
    even though int("06") == 6 is in range. Check the leading character.
  - dp[0] = 1 (or True): the empty prefix has exactly one decoding, the empty
    one. Getting this base wrong zeroes the whole table.
  - Cap the inner loop at i - L; without the cap word break is O(n^2) slices.

Run the tests at the bottom with:  python3 dynamic_programming/string_segmentation.py
"""

import random
from functools import cache


# ---------------------------------------------------------------- implementation


def decode_ways(s):
    """Ways to decode a digit string with A=1 .. Z=26."""
    prev2, prev1 = 0, 1  # dp[i - 2], dp[i - 1]; dp[0] = 1, dp[-1] unused
    for i, ch in enumerate(s):
        cur = prev1 if ch != "0" else 0
        if i and s[i - 1] != "0" and int(s[i - 1 : i + 1]) <= 26:
            cur += prev2
        prev2, prev1 = prev1, cur
    return prev1


def word_break(s, words):
    """Can s be written as a concatenation of words (reuse allowed)?"""
    ws, L = set(words), max(map(len, words), default=0)
    dp = [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        for j in range(max(0, i - L), i):
            if dp[j] and s[j:i] in ws:
                dp[i] = True
                break
    return dp[-1]


def word_break_count(s, words):
    """Number of distinct segmentations. Same table, + instead of OR."""
    ws, L = set(words), max(map(len, words), default=0)
    dp = [1] + [0] * len(s)
    for i in range(1, len(s) + 1):
        dp[i] = sum(dp[j] for j in range(max(0, i - L), i) if s[j:i] in ws)
    return dp[-1]


def word_break_min_pieces(s, words):
    """Fewest words to build s, or -1 if impossible."""
    ws, L = set(words), max(map(len, words), default=0)
    INF = float("inf")
    dp = [0] + [INF] * len(s)
    for i in range(1, len(s) + 1):
        for j in range(max(0, i - L), i):
            if dp[j] + 1 < dp[i] and s[j:i] in ws:
                dp[i] = dp[j] + 1
    return dp[-1] if dp[-1] < INF else -1


def word_break_all(s, words):
    """Every segmentation as a sentence. Output can be exponential in size.

    Listing is backtracking, not DP — memoising on the suffix only avoids
    re-exploring it, it does not shrink the answer. Prune with word_break first
    so dead suffixes are not expanded.
    """
    ws = set(words)

    @cache
    def go(i):
        if i == len(s):
            return [[]]
        out = []
        for j in range(i + 1, len(s) + 1):
            if s[i:j] in ws:
                out.extend([s[i:j]] + rest for rest in go(j))
        return out

    return [" ".join(p) for p in go(0)]


# ------------------------------------------------------------------------ tests


def brute_decodings(s):
    """Every decoding, built by trying both chunk sizes."""
    if not s:
        return [""]
    out = []
    for k in (1, 2):
        chunk = s[:k]
        if len(chunk) == k and chunk[0] != "0" and 1 <= int(chunk) <= 26:
            letter = chr(ord("A") + int(chunk) - 1)
            out += [letter + rest for rest in brute_decodings(s[k:])]
    return out


def brute_splits(s, ws):
    """All segmentations, by trying every one of the 2^(n-1) cut sets."""
    n, out = len(s), []
    for mask in range(1 << max(n - 1, 0)):
        cuts = [0] + [i + 1 for i in range(n - 1) if mask >> i & 1] + [n]
        parts = [s[a:b] for a, b in zip(cuts, cuts[1:])]
        if all(p in ws for p in parts):
            out.append(parts)
    return out if s else [[]]


def test_decode_classic():
    assert decode_ways("12") == 2
    assert decode_ways("226") == 3
    assert decode_ways("11106") == 2
    assert decode_ways("") == 1


def test_decode_zero_traps():
    assert decode_ways("0") == 0
    assert decode_ways("06") == 0   # int("06") is 6, but a leading 0 is invalid
    assert decode_ways("100") == 0  # the second 0 has nothing to pair with
    assert decode_ways("27") == 1   # 27 is out of range
    assert decode_ways("10") == 1


def test_decode_matches_brute_force():
    random.seed(4)
    for _ in range(500):
        s = "".join(random.choice("0123456789" if random.random() < 0.3 else "12")
                    for _ in range(random.randint(0, 12)))
        decs = brute_decodings(s)
        assert len(decs) == len(set(decs))  # distinct splits give distinct text
        assert decode_ways(s) == len(decs), s


def test_word_break_classic():
    assert word_break("leetcode", ["leet", "code"])
    assert word_break("applepenapple", ["apple", "pen"])
    assert not word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])
    assert word_break("", [])
    assert not word_break("a", [])


def test_word_break_all_classic():
    got = word_break_all("catsanddog", ["cat", "cats", "and", "sand", "dog"])
    assert sorted(got) == ["cat sand dog", "cats and dog"]


def test_word_break_family_matches_brute_force():
    random.seed(5)
    for _ in range(300):
        words = list({"".join(random.choice("ab") for _ in range(random.randint(1, 3)))
                      for _ in range(random.randint(0, 4))})
        s = "".join(random.choice("ab") for _ in range(random.randint(0, 10)))
        splits = brute_splits(s, set(words))
        assert word_break(s, words) == bool(splits)
        assert word_break_count(s, words) == len(splits)
        assert word_break_min_pieces(s, words) == (min(map(len, splits)) if splits else -1)
        assert sorted(word_break_all(s, words)) == sorted(" ".join(p) for p in splits)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
