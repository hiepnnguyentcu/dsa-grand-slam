"""String matching — Rabin–Karp rolling hash and the KMP prefix function.

Signs: "find needle in haystack" (strStr) when the naive O(n*m) is too slow,
       "repeated substrings of length k" (DNA sequences), "longest substring
       that occurs twice", "shortest palindrome by adding to the front",
       "is s a repetition of a smaller block".
Approach: Rabin–Karp hashes every length-m window in O(1) each by rolling:
          drop the left char's contribution, multiply by the base, add the
          new char. Equal hashes are CANDIDATES; confirm with a slice compare.
          With binary search on the length (a duplicate of length L implies
          one of length L - 1), it finds the longest duplicate substring.
          KMP precomputes pi[i] = length of the longest proper prefix of
          p[:i+1] that is also a suffix. On a mismatch, jump to pi[j - 1]
          instead of restarting, so the text pointer never moves back.
Complexity: Rabin–Karp O(n + m) expected; KMP O(n + m) worst case, O(m) space.
            Longest duplicate O(n log n) expected.
Gotchas:
  - Always verify a hash hit (or use two moduli) — collisions happen.
  - Python ints don't overflow, but take % mod every step or they grow huge.
  - Remove the left char with its weight base^(m-1), precomputed once.
  - pi is built by matching p against itself: same loop as the search.
  - Repeated block: s is a repetition iff n % (n - pi[-1]) == 0 and pi[-1] > 0.
  - Short fixed k (DNA, k = 10): a set of slices s[i:i+k] is simpler and fine.

Run the tests at the bottom with:  python3 hashing_strings/string_matching.py
"""


# ---------------------------------------------------------------- implementation

BASE, MOD = 131, (1 << 61) - 1


def rabin_karp(text, pat):
    """LC 28. First index of pat in text, or -1."""
    n, m = len(text), len(pat)
    if m == 0:
        return 0
    if m > n:
        return -1
    high = pow(BASE, m - 1, MOD)              # weight of the char leaving the window
    hp = hw = 0
    for i in range(m):
        hp = (hp * BASE + ord(pat[i])) % MOD
        hw = (hw * BASE + ord(text[i])) % MOD
    for i in range(n - m + 1):
        if hw == hp and text[i:i + m] == pat:  # hash hit -> verify
            return i
        if i + m < n:
            hw = ((hw - ord(text[i]) * high) * BASE + ord(text[i + m])) % MOD
    return -1


def repeated_dna(s, k=10):
    """LC 187. Length-k substrings occurring more than once, sorted."""
    seen, dup = set(), set()
    for i in range(len(s) - k + 1):
        t = s[i:i + k]
        (dup if t in seen else seen).add(t)
    return sorted(dup)


def _dup_of_length(s, L):
    """Start of some substring of length L that occurs twice, or -1."""
    if L == 0:
        return 0
    high = pow(BASE, L - 1, MOD)
    h = 0
    for i in range(L):
        h = (h * BASE + ord(s[i])) % MOD
    seen = {h: [0]}
    for i in range(1, len(s) - L + 1):
        h = ((h - ord(s[i - 1]) * high) * BASE + ord(s[i + L - 1])) % MOD
        for j in seen.get(h, ()):
            if s[j:j + L] == s[i:i + L]:     # verify against collisions
                return i
        seen.setdefault(h, []).append(i)
    return -1


def longest_dup_substring(s):
    """LC 1044. Binary search the length, rolling hash to test it."""
    lo, hi, best = 1, len(s) - 1, ""
    while lo <= hi:
        mid = (lo + hi) // 2
        i = _dup_of_length(s, mid)
        if i >= 0:
            best, lo = s[i:i + mid], mid + 1
        else:
            hi = mid - 1
    return best


def prefix_function(p):
    """pi[i] = longest proper prefix of p[:i+1] that is also its suffix."""
    pi = [0] * len(p)
    k = 0
    for i in range(1, len(p)):
        while k and p[i] != p[k]:
            k = pi[k - 1]                     # fall back to the next shorter border
        if p[i] == p[k]:
            k += 1
        pi[i] = k
    return pi


def kmp_find_all(text, pat):
    """Every start index of pat in text (overlaps included)."""
    if not pat:
        return list(range(len(text) + 1))
    pi, out, k = prefix_function(pat), [], 0
    for i, c in enumerate(text):
        while k and c != pat[k]:
            k = pi[k - 1]
        if c == pat[k]:
            k += 1
        if k == len(pat):
            out.append(i - k + 1)
            k = pi[k - 1]
    return out


def repeated_substring_pattern(s):
    """LC 459. s is some block repeated at least twice."""
    b = prefix_function(s)[-1] if s else 0
    return b > 0 and len(s) % (len(s) - b) == 0


def shortest_palindrome(s):
    """LC 214. Shortest palindrome made by adding chars to the FRONT of s."""
    b = prefix_function(s + "#" + s[::-1])[-1]   # longest palindromic prefix
    return s[b:][::-1] + s


# ------------------------------------------------------------------------ tests


def test_examples():
    assert rabin_karp("sadbutsad", "sad") == 0
    assert rabin_karp("leetcode", "leeto") == -1
    assert repeated_dna("AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT") == ["AAAAACCCCC", "CCCCCAAAAA"]
    assert longest_dup_substring("banana") == "ana"
    assert longest_dup_substring("abcd") == ""
    assert prefix_function("aabaaab") == [0, 1, 0, 1, 2, 2, 3]
    assert kmp_find_all("aaaa", "aa") == [0, 1, 2]
    assert repeated_substring_pattern("abab") and not repeated_substring_pattern("aba")
    assert shortest_palindrome("aacecaaa") == "aaacecaaa"
    assert shortest_palindrome("abcd") == "dcbabcd"


def test_search_matches_str_find():
    import random

    rng = random.Random(1)
    for _ in range(1000):
        text = "".join(rng.choice("ab") for _ in range(rng.randint(0, 15)))
        pat = "".join(rng.choice("ab") for _ in range(rng.randint(0, 4)))
        assert rabin_karp(text, pat) == text.find(pat)
        expect = [i for i in range(len(text) - len(pat) + 1) if text.startswith(pat, i)]
        assert kmp_find_all(text, pat) == expect


def test_prefix_function_matches_brute_force():
    import random

    rng = random.Random(2)
    for _ in range(500):
        p = "".join(rng.choice("ab") for _ in range(rng.randint(1, 12)))
        expect = [max(k for k in range(i + 1) if p[:k] == p[i + 1 - k:i + 1]) for i in range(len(p))]
        assert prefix_function(p) == expect


def test_dna_and_longest_dup_match_brute_force():
    import random

    rng = random.Random(3)
    for _ in range(300):
        s = "".join(rng.choice("ACGT"[:rng.randint(1, 4)]) for _ in range(rng.randint(0, 14)))
        k = rng.randint(1, 4)
        subs = [s[i:i + k] for i in range(len(s) - k + 1)]
        assert repeated_dna(s, k) == sorted({t for t in subs if subs.count(t) > 1})
        best_len = max([L for L in range(1, len(s)) for i in range(len(s) - L + 1)
                        if s.find(s[i:i + L], i + 1) != -1], default=0)
        got = longest_dup_substring(s)
        assert len(got) == best_len
        if got:
            first = s.find(got)
            assert s.find(got, first + 1) != -1


def test_repeat_and_shortest_palindrome_match_brute_force():
    import random

    rng = random.Random(4)
    for _ in range(500):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 10)))
        expect = any(len(s) % d == 0 and s[:d] * (len(s) // d) == s for d in range(1, len(s)))
        assert repeated_substring_pattern(s) == expect
        b = max(k for k in range(len(s) + 1) if s[:k] == s[:k][::-1])
        assert shortest_palindrome(s) == s[b:][::-1] + s
        t = shortest_palindrome(s)
        assert t == t[::-1] and t.endswith(s)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
