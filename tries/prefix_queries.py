"""Prefix queries — LCP, replace words, search suggestions, map sum, prefix+suffix.

Signs: "shortest root that prefixes this word", "top-k suggestions as the user
       types", "sum of values whose key starts with", "words with this prefix
       AND this suffix". Each answer is a property of a prefix node.
Approach: the trie node for a prefix stands for every word below it, so cache
          the answer *on the node* at insert time and a query becomes one walk.
            - Longest common prefix: walk from the root while there is exactly
              one child and no word ends here.
            - Replace words: walk each word; stop at the first end marker.
            - Search suggestions: each node keeps the 3 smallest words below
              it (insert in sorted order, keep the first 3).
            - Map sum: each node keeps the sum of values below it. On
              overwrite, add the *delta* (new - old) along the path.
            - Prefix + suffix: insert "suffix{word" for every suffix of every
              word ("{" sorts after "z"); query "suffix{prefix". Each node
              keeps the largest index that passed through.
Complexity: LCP O(total chars). Replace words O(total chars). Suggestions
            O(total chars * 3) build, O(len(search word)) answer. Map sum O(L)
            per op. Prefix+suffix O(N * L^2) build, O(L) query.
Gotchas:
  - Replace words wants the *shortest* root: stop at the first end marker,
    not the deepest.
  - Suggestions: once the typed prefix leaves the trie, every later prefix is
    empty too — keep returning [].
  - Map sum: inserting a key twice overwrites. Adding the full value again
    double counts; keep a key -> value map to compute the delta.
  - Prefix+suffix: the separator must not be a real letter, and later words
    win ties, so overwrite the index rather than keeping the first.
  - The two-trie alternative (prefix trie and suffix trie, intersect index
    sets) is O(N) per query in the worst case.

Run the tests at the bottom with:  python3 tries/prefix_queries.py
"""

import bisect
import random


# ---------------------------------------------------------------- implementation


def longest_common_prefix(words):
    """Longest prefix shared by every word ("" for no words)."""
    if not words:
        return ""
    root, END = {}, "$"
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node[END] = True
    out, node = [], root
    while len(node) == 1 and END not in node:   # one child, nobody stops here
        ch, node = next(iter(node.items()))
        out.append(ch)
    return "".join(out)


def replace_words(roots, sentence):
    """Replace each word by its shortest root that is a prefix of it."""
    trie, END = {}, "$"
    for r in roots:
        node = trie
        for ch in r:
            node = node.setdefault(ch, {})
        node[END] = r

    def shortest_root(word):
        node = trie
        for ch in word:
            if ch not in node:
                return word
            node = node[ch]
            if END in node:
                return node[END]               # first end marker = shortest
        return word

    return " ".join(shortest_root(w) for w in sentence.split())


def suggested_products(products, search_word):
    """After each typed character, up to 3 lexicographically smallest matches."""
    root = {}
    for p in sorted(products):
        node = root
        for ch in p:
            node = node.setdefault(ch, {"#": []})
            if len(node["#"]) < 3:             # sorted insert -> first 3 win
                node["#"].append(p)
    out, node = [], root
    for ch in search_word:
        node = node.get(ch) if node else None
        out.append(node["#"] if node else [])
    return out


def suggested_products_bisect(products, search_word):
    """No-trie alternative: sort once, binary search each prefix."""
    products = sorted(products)
    out, prefix = [], ""
    for ch in search_word:
        prefix += ch
        i = bisect.bisect_left(products, prefix)
        out.append([p for p in products[i:i + 3] if p.startswith(prefix)])
    return out


class MapSum:
    """insert(key, val) overwrites; sum(prefix) adds values of keys under prefix."""

    def __init__(self):
        self.root = {"#": 0}
        self.vals = {}

    def insert(self, key, val):
        delta = val - self.vals.get(key, 0)
        self.vals[key] = val
        node = self.root
        node["#"] += delta
        for ch in key:
            node = node.setdefault(ch, {"#": 0})
            node["#"] += delta

    def sum(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node:
                return 0
            node = node[ch]
        return node["#"]


class WordFilter:
    """f(prefix, suffix) -> largest index of a word with both, else -1."""

    SEP = "{"   # sorts after "z", never a real letter

    def __init__(self, words):
        self.root = {}
        for idx, w in enumerate(words):
            key = w + self.SEP + w
            for start in range(len(w) + 1):    # every suffix of w, incl. ""
                node = self.root
                for ch in key[start:]:
                    node = node.setdefault(ch, {})
                    node["#"] = idx            # later index overwrites

    def f(self, prefix, suffix):
        node = self.root
        for ch in suffix + self.SEP + prefix:
            if ch not in node:
                return -1
            node = node[ch]
        return node["#"]


# ------------------------------------------------------------------------ tests


def rand_word(alpha="abc", lo=1, hi=5):
    return "".join(random.choice(alpha) for _ in range(random.randint(lo, hi)))


def brute_lcp(words):
    if not words:
        return ""
    s = min(words, key=len)
    while not all(w.startswith(s) for w in words):
        s = s[:-1]
    return s


def test_lcp_classic_and_edges():
    assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"
    assert longest_common_prefix(["dog", "racecar", "car"]) == ""
    assert longest_common_prefix(["ab", "abc"]) == "ab"     # stop at word end
    assert longest_common_prefix(["", "a"]) == ""
    assert longest_common_prefix([]) == ""


def test_lcp_matches_brute_force():
    random.seed(4)
    for _ in range(200):
        words = [rand_word("ab", 0, 5) for _ in range(random.randint(1, 6))]
        assert longest_common_prefix(words) == brute_lcp(words)


def test_replace_words_classic():
    got = replace_words(["cat", "bat", "rat"], "the cattle was rattled by the battery")
    assert got == "the cat was rat by the bat"
    assert replace_words(["a", "aa"], "aaa b") == "a b"      # shortest root


def test_replace_words_matches_brute_force():
    random.seed(5)
    for _ in range(100):
        roots = [rand_word("ab", 1, 3) for _ in range(random.randint(0, 5))]
        words = [rand_word("ab", 1, 5) for _ in range(6)]
        want = []
        for w in words:
            hits = [r for r in roots if w.startswith(r)]
            want.append(min(hits, key=len) if hits else w)
        assert replace_words(roots, " ".join(words)) == " ".join(want)


def test_suggestions_classic():
    products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"]
    assert suggested_products(products, "mouse") == [
        ["mobile", "moneypot", "monitor"],
        ["mobile", "moneypot", "monitor"],
        ["mouse", "mousepad"],
        ["mouse", "mousepad"],
        ["mouse", "mousepad"],
    ]
    assert suggested_products(["havana"], "tatiana") == [[]] * 7


def test_suggestions_match_bisect_and_scan():
    random.seed(6)
    for _ in range(100):
        products = [rand_word("abc", 1, 5) for _ in range(random.randint(0, 15))]
        q = rand_word("abc", 1, 5)
        got = suggested_products(products, q)
        assert got == suggested_products_bisect(products, q)
        for i in range(len(q)):
            assert got[i] == sorted(p for p in products if p.startswith(q[:i + 1]))[:3]


def test_map_sum_classic():
    m = MapSum()
    m.insert("apple", 3)
    assert m.sum("ap") == 3
    m.insert("app", 2)
    assert m.sum("ap") == 5
    m.insert("apple", 1)                  # overwrite, not add
    assert m.sum("ap") == 3
    assert m.sum("b") == 0


def test_map_sum_matches_dict_scan():
    random.seed(7)
    m, ref = MapSum(), {}
    for _ in range(1000):
        k, v = rand_word("ab", 1, 4), random.randint(-5, 9)
        m.insert(k, v)
        ref[k] = v
        q = rand_word("ab", 0, 4)
        assert m.sum(q) == sum(val for key, val in ref.items() if key.startswith(q))


def test_word_filter_classic():
    wf = WordFilter(["apple"])
    assert wf.f("a", "e") == 0
    assert wf.f("b", "") == -1
    wf = WordFilter(["abc", "xbc", "abc"])
    assert wf.f("a", "bc") == 2           # largest index wins
    assert wf.f("", "") == 2


def test_word_filter_matches_scan():
    random.seed(8)
    for _ in range(40):
        words = [rand_word("ab", 1, 4) for _ in range(random.randint(1, 12))]
        wf = WordFilter(words)
        for _ in range(30):
            p, s = rand_word("ab", 0, 3), rand_word("ab", 0, 3)
            want = max((i for i, w in enumerate(words)
                        if w.startswith(p) and w.endswith(s)), default=-1)
            assert wf.f(p, s) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
