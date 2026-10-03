"""Wildcard search — add and search word, "." matches any one letter.

Signs: dictionary queried with patterns where some positions are "any
       character", word lengths are short, many queries.
Approach: store words in a trie. Search with DFS over (node, index): a real
          letter follows its one child; "." branches into every child. A hit
          needs index == len(pattern) *and* an end marker.
Complexity: add O(L). Search O(L) with no dots; worst case O(26^d * L) with d
            dots, bounded by the trie size — it never visits a node twice for
            one pattern position.
Gotchas:
  - "." matches exactly one character, never zero. "a." does not match "a".
  - Check the end marker at the last position; a prefix of a word is not a
    match.
  - Bucket words by length first if patterns are mostly dots — only same
    length words can match, which kills most branches.
  - If "*" (any run) is allowed, this becomes regex matching: use DP, not a
    trie (dynamic_programming/).

Run the tests at the bottom with:  python3 tries/wildcard_search.py
"""

import random
import re


# ---------------------------------------------------------------- implementation


class WordDictionary:
    END = "$"

    def __init__(self):
        self.root = {}

    def add_word(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node[self.END] = True

    def search(self, pattern):
        """True if some added word matches pattern ("." = any one letter)."""

        def go(node, i):
            if i == len(pattern):
                return self.END in node
            ch = pattern[i]
            if ch != ".":
                return ch in node and go(node[ch], i + 1)
            return any(go(child, i + 1)
                       for key, child in node.items() if key != self.END)

        return go(self.root, 0)

    def search_iterative(self, pattern):
        """Same answer, level by level: the set of nodes alive after each char."""
        frontier = [self.root]
        for ch in pattern:
            if ch == ".":
                frontier = [c for n in frontier for k, c in n.items() if k != self.END]
            else:
                frontier = [n[ch] for n in frontier if ch in n]
            if not frontier:
                return False
        return any(self.END in n for n in frontier)


# ------------------------------------------------------------------------ tests


def test_classic():
    d = WordDictionary()
    for w in ("bad", "dad", "mad"):
        d.add_word(w)
    assert not d.search("pad")
    assert d.search("bad")
    assert d.search(".ad")
    assert d.search("b..")
    assert not d.search("b.")              # dot is exactly one char
    assert not d.search("ba")              # prefix is not a word


def test_matches_regex_scan():
    random.seed(3)
    for _ in range(40):
        d, words = WordDictionary(), []
        for _ in range(random.randint(0, 20)):
            w = "".join(random.choice("abc") for _ in range(random.randint(1, 4)))
            d.add_word(w)
            words.append(w)
        for _ in range(30):
            p = "".join(random.choice("abc..") for _ in range(random.randint(1, 4)))
            want = any(re.fullmatch(p, w) for w in words)   # "." is regex "."
            assert d.search(p) == want
            assert d.search_iterative(p) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
