"""Stream matching — does some word end at the latest character? (reversed trie)

Signs: characters arrive one at a time; after each, ask whether any dictionary
       word is a *suffix* of what has arrived so far.
Approach: insert every word *reversed*. After each new letter, walk the trie
          from the newest letter backwards through the history. A word end
          marker on the way means some word ends right here. Keep only the
          last L letters (L = longest word): nothing older can matter.
Complexity: build O(total chars). Each query O(L) worst case, usually far
            less because the walk stops at the first missing child.
            Space O(total chars + L).
Gotchas:
  - A forward trie needs a set of "active" partial matches, one per possible
    start; that is O(L) pointers moved on every letter. The reversed trie
    does one walk and stops early.
  - Cap the history (deque(maxlen=L)) or memory grows with the stream.
  - Return True on the *first* end marker; do not keep walking for a longer
    match.
  - Many patterns in one fixed text, all at once, is Aho-Corasick territory;
    this file handles the online, query-per-letter version.

Run the tests at the bottom with:  python3 tries/stream_matching.py
"""

import random
from collections import deque


# ---------------------------------------------------------------- implementation


class StreamChecker:
    END = "$"

    def __init__(self, words):
        self.root = {}
        for w in words:
            node = self.root
            for ch in reversed(w):
                node = node.setdefault(ch, {})
            node[self.END] = True
        self.history = deque(maxlen=max(map(len, words), default=0))

    def query(self, letter):
        """Add letter to the stream; True if some word now ends at it."""
        self.history.append(letter)
        node = self.root
        for ch in reversed(self.history):        # newest first
            node = node.get(ch)
            if node is None:
                return False
            if self.END in node:
                return True
        return False


class ForwardStreamChecker:
    """The alternative: forward trie plus every partial match still alive."""

    END = "$"

    def __init__(self, words):
        self.root = {}
        for w in words:
            node = self.root
            for ch in w:
                node = node.setdefault(ch, {})
            node[self.END] = True
        self.active = []

    def query(self, letter):
        nxt = [n[letter] for n in self.active + [self.root] if letter in n]
        self.active = nxt
        return any(self.END in n for n in nxt)


# ------------------------------------------------------------------------ tests


def test_classic():
    sc = StreamChecker(["cd", "f", "kl"])
    got = [sc.query(ch) for ch in "abcdefghijkl"]
    assert got == [False, False, False, True, False, True,
                   False, False, False, False, False, True]


def test_history_is_capped():
    sc = StreamChecker(["abc", "x"])
    for ch in "zzzzzzzzzzab":
        sc.query(ch)
    assert len(sc.history) == 3
    assert sc.query("c")


def test_matches_suffix_scan_and_forward_trie():
    random.seed(12)
    for _ in range(60):
        words = ["".join(random.choice("abc") for _ in range(random.randint(1, 4)))
                 for _ in range(random.randint(1, 6))]
        rev, fwd, seen = StreamChecker(words), ForwardStreamChecker(words), ""
        for _ in range(40):
            ch = random.choice("abc")
            seen += ch
            want = any(seen.endswith(w) for w in words)
            assert rev.query(ch) == want
            assert fwd.query(ch) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
