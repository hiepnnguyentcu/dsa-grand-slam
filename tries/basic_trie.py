"""Trie (prefix tree) — insert / search / startsWith, counts, deletion.

Signs: many lookups by *prefix* ("any word starting with", autocomplete, "is
       this a prefix of something"), a fixed dictionary queried many times,
       shared prefixes worth storing once.
Approach: a tree where each edge is one character and each node is a prefix.
          A word is a path from the root plus an end marker on its last node.
            - Trie: node class with `children` dict, `end` count of words
              ending here, `pass_` count of words passing through. Counts give
              countWordsEqualTo / countWordsStartingWith in O(L), and make
              deletion safe with duplicates.
            - DictTrie: nested dicts, "$" as the end marker. Shortest code;
              the interview default.
            - ArrayTrie: flat arrays of 26 child slots. Fastest for a-z,
              wasteful for sparse or large alphabets.
Complexity: O(L) per insert / search / prefix query, L = word length.
            Space O(total characters) nodes; ArrayTrie spends 26 slots each.
Gotchas:
  - search vs startsWith differ only in the final end-marker check. Forgetting
    it makes "app" found after inserting only "apple".
  - Deletion must not cut a branch another word still uses: decrement pass
    counts on the way down and drop the child whose count hits 0.
  - Erasing a word that is not there must be a no-op — check before touching
    counts.
  - Dict-of-dicts: never use a key that could also be a real character as the
    end marker ("$" fails if words may contain "$").
  - For a single lookup a set is simpler and faster. Reach for a trie when
    prefixes matter or one walk serves many words (see
    backtracking/grid_search.py, Word Search II).

Run the tests at the bottom with:  python3 tries/basic_trie.py
"""

import random
from collections import Counter


# ---------------------------------------------------------------- implementation


class TrieNode:
    __slots__ = ("children", "end", "pass_")

    def __init__(self):
        self.children = {}
        self.end = 0     # words ending exactly here
        self.pass_ = 0   # words whose path goes through here (incl. ending)


class Trie:
    """Node-class trie with multiplicity counts and pruning delete."""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        node.pass_ += 1
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
            node.pass_ += 1
        node.end += 1

    def _walk(self, s):
        """Node for prefix s, or None if no stored word starts with s."""
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.end > 0

    def starts_with(self, prefix):
        node = self._walk(prefix)
        return node is not None and node.pass_ > 0

    def count_words_equal_to(self, word):
        node = self._walk(word)
        return node.end if node else 0

    def count_words_starting_with(self, prefix):
        node = self._walk(prefix)
        return node.pass_ if node else 0

    def erase(self, word):
        """Remove one copy of word. Returns False (and changes nothing) if absent.

        Walk down decrementing pass counts; the first child whose count drops
        to 0 is unlinked, which frees its whole subtree at once.
        """
        if not self.search(word):
            return False
        node = self.root
        node.pass_ -= 1
        for ch in word:
            child = node.children[ch]
            child.pass_ -= 1
            if child.pass_ == 0:
                del node.children[ch]   # prune: nobody else uses this branch
                return True
            node = child
        node.end -= 1
        return True

    def node_count(self):
        stack, n = [self.root], 0
        while stack:
            node = stack.pop()
            n += 1
            stack.extend(node.children.values())
        return n


class DictTrie:
    """Nested-dict trie: the shortest version. "$" marks a word end."""

    END = "$"

    def __init__(self):
        self.root = {}

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node[self.END] = True

    def _walk(self, s):
        node = self.root
        for ch in s:
            if ch not in node:
                return None
            node = node[ch]
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and self.END in node

    def starts_with(self, prefix):
        return self._walk(prefix) is not None


class ArrayTrie:
    """Lowercase a-z trie stored as flat arrays: child[node][c] = node id, 0 = none.

    No per-node objects or hashing: one list of 26 ints per node. Node 0 is
    the root, so 0 can double as "no child".
    """

    def __init__(self):
        self.child = [[0] * 26]
        self.end = [False]

    def insert(self, word):
        v = 0
        for ch in word:
            c = ord(ch) - 97
            if not self.child[v][c]:
                self.child[v][c] = len(self.child)
                self.child.append([0] * 26)
                self.end.append(False)
            v = self.child[v][c]
        self.end[v] = True

    def _walk(self, s):
        v = 0
        for ch in s:
            v = self.child[v][ord(ch) - 97]
            if not v:
                return -1
        return v

    def search(self, word):
        v = self._walk(word)
        return v != -1 and self.end[v]

    def starts_with(self, prefix):
        return self._walk(prefix) != -1


# ------------------------------------------------------------------------ tests


def rand_word(alpha="abc", lo=0, hi=5):
    return "".join(random.choice(alpha) for _ in range(random.randint(lo, hi)))


def test_classic_insert_search_prefix():
    for cls in (Trie, DictTrie, ArrayTrie):
        t = cls()
        t.insert("apple")
        assert t.search("apple")
        assert not t.search("app")        # prefix, not a word
        assert t.starts_with("app")
        t.insert("app")
        assert t.search("app")
        assert not t.starts_with("b")


def test_empty_string_and_root():
    t = Trie()
    assert not t.starts_with("")          # no stored word starts with ""
    assert t.count_words_starting_with("") == 0
    t.insert("")
    assert t.search("") and t.count_words_starting_with("") == 1


def test_all_three_variants_match_set_scan():
    random.seed(1)
    for _ in range(30):
        words = [rand_word(lo=1) for _ in range(random.randint(0, 25))]
        tries = [cls() for cls in (Trie, DictTrie, ArrayTrie)]
        for w in words:
            for t in tries:
                t.insert(w)
        stored = set(words)
        for _ in range(40):
            q = rand_word()
            want_word = q in stored
            want_prefix = any(w.startswith(q) for w in stored)
            for t in tries:
                assert t.search(q) == want_word
                if q or stored:
                    assert t.starts_with(q) == want_prefix


def test_counts_match_counter_under_inserts_and_erases():
    random.seed(2)
    t, bag = Trie(), Counter()
    for _ in range(2000):
        w = rand_word("ab", 0, 4)
        if random.random() < 0.6:
            t.insert(w)
            bag[w] += 1
        else:
            assert t.erase(w) == (bag[w] > 0)
            if bag[w]:
                bag[w] -= 1
        q = rand_word("ab", 0, 4)
        assert t.count_words_equal_to(q) == bag[q]
        assert t.count_words_starting_with(q) == sum(
            k for w2, k in bag.items() if w2.startswith(q))


def test_erase_prunes_unused_branches():
    t = Trie()
    t.insert("abc")
    t.insert("abd")
    before = t.node_count()               # root a b c d
    t.erase("abc")
    assert t.node_count() == before - 1   # only "c" goes; "ab" still shared
    assert t.search("abd") and not t.search("abc")
    t.erase("abd")
    assert t.node_count() == 1            # back to the bare root
    assert not t.starts_with("a")


def test_erase_keeps_duplicates_and_prefix_words():
    t = Trie()
    for w in ("app", "app", "apple"):
        t.insert(w)
    t.erase("app")
    assert t.search("app") and t.count_words_equal_to("app") == 1
    t.erase("app")
    assert not t.search("app") and t.search("apple")
    assert t.erase("app") is False        # absent: no-op
    assert t.count_words_starting_with("ap") == 1


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
