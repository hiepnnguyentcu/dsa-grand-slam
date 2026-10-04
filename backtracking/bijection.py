"""Bijection / mapping — word pattern II (segmentation unknown).

Signs: "pattern char -> substring", "bijective mapping", "isomorphic" with
       no separators.
Approach: two pointers as the slot: p_idx into pattern, s_idx into s.
          Pattern char already mapped -> s must continue with that word.
          Not mapped -> try every s[s_idx:i+1] not already taken by another
          char. State is a dict + a set -> undo with `del` / remove.
Complexity: exponential in len(pattern); fine for LC sizes (<= 20).
Gotchas:
  - Bijection needs both directions: char_word_m AND a used-words set,
    else 'ab' matches 'xx'.
  - Undo with `del char_word_m[char]`, not `= None` — a None entry still
    reads as "mapped".
  - 290 gives the words (split on space) -> no backtracking, one pass of two
    maps: hashing_strings/hash_lookup.py has it; baseline repeated here.

Run the tests at the bottom with:  python3 backtracking/bijection.py
"""

import random
from itertools import combinations


# ---------------------------------------------------------------- implementation


def word_pattern_match(pattern, s):
    """LC 291."""
    char_word_m = {}
    used_words = set()

    def dfs(p_idx, s_idx):
        if p_idx == len(pattern):
            return s_idx == len(s)
        if s_idx == len(s):
            return False

        char = pattern[p_idx]
        if char in char_word_m:
            word = char_word_m[char]
            if not s.startswith(word, s_idx):
                return False
            return dfs(p_idx + 1, s_idx + len(word))

        for i in range(s_idx, len(s)):
            word = s[s_idx:i + 1]
            if word in used_words:
                continue
            char_word_m[char] = word
            used_words.add(word)
            if dfs(p_idx + 1, i + 1):
                return True
            del char_word_m[char]
            used_words.remove(word)
        return False

    return dfs(0, 0)


def word_pattern(pattern, s):
    """LC 290. Words given -> one pass, two maps."""
    words = s.split()
    if len(words) != len(pattern):
        return False
    char_word_m, word_char_m = {}, {}
    for char, word in zip(pattern, words):
        if char_word_m.setdefault(char, word) != word:
            return False
        if word_char_m.setdefault(word, char) != char:
            return False
    return True


# ------------------------------------------------------------------------ tests


def brute_match(pattern, s):
    """Try every split of s into len(pattern) non-empty pieces."""
    k = len(pattern)
    for cuts in combinations(range(1, len(s)), k - 1):
        bounds = [0, *cuts, len(s)]
        words = [s[a:b] for a, b in zip(bounds, bounds[1:])]
        if word_pattern(pattern, " ".join(words)):
            return True
    return False


def test_word_pattern_match_examples():
    assert word_pattern_match("abab", "redblueredblue")
    assert word_pattern_match("aaaa", "asdasdasdasd")
    assert not word_pattern_match("aabb", "xyzabcxzyabc")
    assert not word_pattern_match("ab", "xx")


def test_word_pattern_match_vs_brute_force():
    random.seed(1)
    for _ in range(200):
        pattern = "".join(random.choice("ab") for _ in range(random.randint(1, 4)))
        s = "".join(random.choice("xy") for _ in range(random.randint(1, 8)))
        assert word_pattern_match(pattern, s) == brute_match(pattern, s)


def test_word_pattern_baseline():
    assert word_pattern("abba", "dog cat cat dog")
    assert not word_pattern("abba", "dog cat cat fish")
    assert not word_pattern("aaaa", "dog cat cat dog")
    assert not word_pattern("abba", "dog dog dog dog")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
