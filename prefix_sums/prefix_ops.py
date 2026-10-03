"""Prefix XOR, prefix counts, prefix products — the same trick, other operators.

Signs: XOR of a subarray, "how many vowels / plates / 1s between l and r",
       per-letter counts in a substring, product of everything except a[i].
Approach: any operator with an inverse works like +:
          XOR undoes itself  -> xor(a[l..r]) = px[r + 1] ^ px[l].
          counts are sums of 0/1 indicators -> one prefix per thing counted.
          Products have no safe inverse (zeros), so combine a prefix pass and
          a suffix pass instead of dividing.
Complexity: O(n) build, O(1) per query; per-letter counts cost O(26 n).
Gotchas:
  - Product except self: never divide. A single zero breaks it and two zeros
    make every answer 0.
  - min / max have no inverse: prefix min answers [0..r] only, never [l..r].
    For arbitrary ranges use a sparse table or a segment tree.
  - Counting with a condition ("plates between candles") often needs a prefix
    count plus nearest-candle arrays to snap the range inward.

Run the tests at the bottom with:  python3 prefix_sums/prefix_ops.py
"""

import random
from math import prod


# ---------------------------------------------------------------- implementation


def product_except_self(a):
    """out[i] = product of every a[j] with j != i, no division.

    First pass leaves out[i] = product of a[:i]; the second multiplies in the
    product of a[i+1:] using one running variable.
    """
    n = len(a)
    out = [1] * n
    for i in range(1, n):
        out[i] = out[i - 1] * a[i - 1]
    suffix = 1
    for i in range(n - 1, -1, -1):
        out[i] *= suffix
        suffix *= a[i]
    return out


def xor_queries(a, queries):
    """XOR of a[l..r] for each (l, r)."""
    px = [0] * (len(a) + 1)
    for i, x in enumerate(a):
        px[i + 1] = px[i] ^ x
    return [px[r + 1] ^ px[l] for l, r in queries]


def vowel_strings(words, queries):
    """How many words in words[l..r] start and end with a vowel."""
    p = [0]
    for w in words:
        p.append(p[-1] + (w[0] in "aeiou" and w[-1] in "aeiou"))
    return [p[r + 1] - p[l] for l, r in queries]


def plates_between_candles(s, queries):
    """Plates '*' strictly between the outermost candles '|' inside s[l..r].

    Snap l right to the first candle and r left to the last candle, then count
    plates between them with a prefix count.
    """
    n = len(s)
    plates = [0] * (n + 1)
    for i, c in enumerate(s):
        plates[i + 1] = plates[i] + (c == "*")
    right = [n] * (n + 1)              # first candle at index >= i
    for i in range(n - 1, -1, -1):
        right[i] = i if s[i] == "|" else right[i + 1]
    left = [-1] * n                    # last candle at index <= i
    for i in range(n):
        left[i] = i if s[i] == "|" else (left[i - 1] if i else -1)
    out = []
    for l, r in queries:
        a, b = right[l], left[r]
        out.append(plates[b] - plates[a] if a < b else 0)
    return out


def can_make_palindrome(s, queries):
    """For (l, r, k): can s[l..r] be rearranged, with <= k letter swaps, into a palindrome?

    Per-letter prefix counts give each letter's count in O(26). Letters with
    an odd count must pair up; one replacement fixes two of them.
    """
    counts = [[0] * 26]
    for c in s:
        row = counts[-1][:]
        row[ord(c) - 97] += 1
        counts.append(row)
    out = []
    for l, r, k in queries:
        odd = sum((counts[r + 1][c] - counts[l][c]) % 2 for c in range(26))
        out.append(odd // 2 <= k)
    return out


# ------------------------------------------------------------------------ tests


def test_product_except_self_examples():
    assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
    assert product_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
    assert product_except_self([0, 0, 5]) == [0, 0, 0]


def test_product_except_self_matches_brute_force():
    random.seed(11)
    for _ in range(300):
        a = [random.randint(-3, 3) for _ in range(random.randint(1, 8))]
        want = [prod(a[:i] + a[i + 1:]) for i in range(len(a))]
        assert product_except_self(a) == want


def test_xor_queries_matches_brute_force():
    random.seed(12)
    assert xor_queries([1, 3, 4, 8], [(0, 1), (1, 2), (0, 3), (3, 3)]) == [2, 7, 14, 8]
    for _ in range(200):
        a = [random.randint(0, 63) for _ in range(random.randint(1, 12))]
        qs = [(l, random.randint(l, len(a) - 1)) for l in
              (random.randrange(len(a)) for _ in range(5))]
        want = []
        for l, r in qs:
            x = 0
            for v in a[l:r + 1]:
                x ^= v
            want.append(x)
        assert xor_queries(a, qs) == want


def test_vowel_strings_example():
    words = ["aba", "bcb", "ece", "aa", "e"]
    assert vowel_strings(words, [(0, 2), (1, 4), (1, 1)]) == [2, 3, 0]


def test_plates_between_candles_matches_brute_force():
    random.seed(13)
    assert plates_between_candles("**|**|***|", [(2, 5), (5, 9)]) == [2, 3]

    def brute(s, l, r):
        sub = s[l:r + 1]
        if sub.count("|") < 2:
            return 0
        return sub[sub.index("|"):sub.rindex("|")].count("*")

    for _ in range(300):
        s = "".join(random.choice("*|") for _ in range(random.randint(1, 12)))
        qs = [(l, random.randint(l, len(s) - 1)) for l in
              (random.randrange(len(s)) for _ in range(5))]
        assert plates_between_candles(s, qs) == [brute(s, l, r) for l, r in qs]


def test_can_make_palindrome_matches_brute_force():
    random.seed(14)
    s = "abcda"
    assert can_make_palindrome(s, [(3, 3, 0), (1, 2, 0), (0, 3, 1), (0, 3, 2), (0, 4, 1)]) == \
        [True, False, False, True, True]
    for _ in range(200):
        s = "".join(random.choice("abc") for _ in range(random.randint(1, 10)))
        qs = []
        for _ in range(5):
            l = random.randrange(len(s))
            qs.append((l, random.randint(l, len(s) - 1), random.randint(0, 3)))
        want = []
        for l, r, k in qs:
            sub = s[l:r + 1]
            odd = sum(sub.count(c) % 2 for c in set(sub))
            want.append(odd // 2 <= k)
        assert can_make_palindrome(s, qs) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
