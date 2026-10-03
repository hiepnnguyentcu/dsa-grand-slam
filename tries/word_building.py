"""Word building — longest word one char at a time, concatenated words, word break.

Signs: words made out of *other dictionary words*: "built one letter at a
       time", "made of at least two shorter words", "can s be split into
       dictionary words".
Approach:
  - Longest word: insert all words, then DFS from the root but only step into
    children that end a word. The deepest node reached is the answer; visit
    children in a-z order so the first deepest is the lexicographically
    smallest.
  - Word break (trie): dp[i] = s[i:] can be split. From each start i walk the
    trie forward along s; every end marker at j gives a candidate dp[j + 1].
    The walk stops as soon as no word continues, and no substring is sliced
    or hashed. The hash-set version lives in
    dynamic_programming/string_segmentation.py.
  - Concatenated words: sort by length. A word can only be built from shorter
    words, so check it with word break against the trie of words seen so far,
    then insert it.
Complexity: longest word O(total chars). Word break O(n * L), L = longest word
            (and usually far less: the walk dies early). Concatenated words
            O(sum of len(w) * L) plus the sort.
Gotchas:
  - Longest word: every prefix must itself be a word, single letters
    included. Stepping into a non-word child is the classic bug.
  - Concatenated words: the empty string is in the input on LeetCode; skip it
    or every word "splits" into empty pieces forever.
  - Concatenated words needs at least two pieces. Checking before inserting
    the word itself guarantees that.
  - Word break with one long word and a short string: the trie walk is
    bounded by the string, the set version by L. Both are fine; pick the trie
    when the dictionary is big and words share prefixes.

Run the tests at the bottom with:  python3 tries/word_building.py
"""

import random
from functools import cache


END = "$"


# ---------------------------------------------------------------- implementation


def build(words):
    root = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node[END] = w
    return root


def longest_word(words):
    """Longest word whose every prefix is a word; ties -> smallest. "" if none."""
    best = ""
    stack = [build(words)]
    while stack:
        node = stack.pop()
        w = node.get(END, "")
        if len(w) > len(best) or (len(w) == len(best) and w < best):
            best = w
        for ch, child in node.items():
            if ch != END and END in child:     # only through complete words
                stack.append(child)
    return best


def word_break(s, words):
    """True if s splits into dictionary words (reuse allowed)."""
    root = build(w for w in words if w)
    n = len(s)
    ok = [False] * (n + 1)
    ok[n] = True
    for i in range(n - 1, -1, -1):
        node = root
        for j in range(i, n):
            node = node.get(s[j])
            if node is None:
                break                          # no word continues: stop early
            if END in node and ok[j + 1]:
                ok[i] = True
                break
    return ok[0]


def concatenated_words(words):
    """Words made of at least two shorter words from the list."""
    root, out = {}, []

    for w in sorted(set(words), key=len):
        if not w:
            continue

        @cache
        def splits(i):                         # can w[i:] be split?
            if i == len(w):
                return True
            node = root
            for j in range(i, len(w)):
                node = node.get(w[j])
                if node is None:
                    return False
                if END in node and splits(j + 1):
                    return True
            return False

        if root and splits(0):                 # trie holds only shorter words
            out.append(w)
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node[END] = w
    return out


# ------------------------------------------------------------------------ tests


def rand_word(alpha="ab", lo=1, hi=4):
    return "".join(random.choice(alpha) for _ in range(random.randint(lo, hi)))


def brute_splittable(s, words, min_pieces=0):
    """Try every cut set: s splits into >= min_pieces words from `words`."""
    ws = set(words)

    @cache
    def go(i, pieces):
        if i == len(s):
            return pieces >= min_pieces
        return any(s[i:j] in ws and go(j, min(pieces + 1, min_pieces))
                   for j in range(i + 1, len(s) + 1))

    return go(0, 0)


def test_longest_word_classic():
    assert longest_word(["w", "wo", "wor", "worl", "world"]) == "world"
    assert longest_word(["a", "banana", "app", "appl", "ap", "apply", "apple"]) == "apple"
    assert longest_word(["abc", "bc"]) == ""              # no single letters


def test_longest_word_matches_brute_force():
    random.seed(9)
    for _ in range(200):
        words = [rand_word("abc", 1, 4) for _ in range(random.randint(0, 12))]
        ws = set(words)
        ok = [w for w in ws if all(w[:k] in ws for k in range(1, len(w)))]
        want = min(ok, key=lambda w: (-len(w), w)) if ok else ""
        assert longest_word(words) == want


def test_word_break_classic():
    assert word_break("leetcode", ["leet", "code"])
    assert word_break("applepenapple", ["apple", "pen"])
    assert not word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])
    assert word_break("", ["a"])


def test_word_break_matches_brute_force():
    random.seed(10)
    for _ in range(300):
        words = [rand_word("ab", 1, 3) for _ in range(random.randint(0, 4))]
        s = rand_word("ab", 0, 10)
        assert word_break(s, words) == brute_splittable(s, words)


def test_concatenated_classic():
    words = ["cat", "cats", "catsdogcats", "dog", "dogcatsdog",
             "hippopotamuses", "rat", "ratcatdogcat"]
    assert sorted(concatenated_words(words)) == ["catsdogcats", "dogcatsdog", "ratcatdogcat"]
    assert concatenated_words(["cat", "dog", "catdog", ""]) == ["catdog"]
    assert concatenated_words(["a"]) == []                # one piece is not enough


def test_concatenated_matches_brute_force():
    random.seed(11)
    for _ in range(150):
        words = list({rand_word("ab", 1, 5) for _ in range(random.randint(1, 10))})
        want = sorted(w for w in words
                      if brute_splittable(w, [x for x in words if x != w], 2))
        assert sorted(concatenated_words(words)) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
