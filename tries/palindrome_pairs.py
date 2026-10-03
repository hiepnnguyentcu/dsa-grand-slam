"""Palindrome pairs — all (i, j) with words[i] + words[j] a palindrome.

Signs: pairs of strings whose concatenation is a palindrome; n up to 5000,
       so the O(n^2 * L) pair check is too slow.
Approach: insert every word *reversed*. For word u to pair with w (u + w is a
          palindrome), u must start with reverse(w) and the leftover of u must
          be a palindrome — or u is a prefix of reverse(w) and the leftover
          of reverse(w) is a palindrome. So:
            - At insert, record on each node the indices whose *remaining*
              part (the rest of the reversed word below that node) is a
              palindrome. The end node records the word itself (empty rest).
            - Walk u down the trie. At every node where some word w ends,
              pair (u, w) if the unread rest of u is a palindrome.
            - If u is fully consumed, pair u with every index recorded on the
              final node.
Complexity: O(n * L^2): each of the n * L node visits checks one palindrome of
            length <= L. Space O(n * L) nodes, plus index lists.
Gotchas:
  - Skip i == j: a palindrome word paired with itself is not a pair.
  - Case 1 runs only at nodes *before* u is used up; equal lengths belong to
    case 2 alone. Checking a word end in both reports ("abc", "cba") twice.
  - The empty string ends at the root: case 1 pairs every palindrome u with
    it, and case 2 for u = "" pairs it with every palindrome (root.pal_below).
  - The simpler hash-map version: for each word and each cut, look up the
    reverse of one side when the other side is a palindrome. Same
    complexity, more edge cases with duplicates of the empty cut.

Run the tests at the bottom with:  python3 tries/palindrome_pairs.py
"""

import random


def is_pal(s, lo=0):
    hi = len(s) - 1
    while lo < hi:
        if s[lo] != s[hi]:
            return False
        lo, hi = lo + 1, hi - 1
    return True


# ---------------------------------------------------------------- implementation


class Node:
    __slots__ = ("children", "word", "pal_below")

    def __init__(self):
        self.children = {}
        self.word = -1        # index of the word whose reverse ends here
        self.pal_below = []   # indices whose rest (below here) is a palindrome


def palindrome_pairs(words):
    root = Node()
    for i, w in enumerate(words):
        node = root
        r = w[::-1]
        for k, ch in enumerate(r):
            if is_pal(r, k):                   # r[k:] still to come is a palindrome
                node.pal_below.append(i)
            node = node.children.setdefault(ch, Node())
        node.word = i
        node.pal_below.append(i)               # empty rest is a palindrome

    out = []
    for i, u in enumerate(words):
        node = root
        for k, ch in enumerate(u):
            if node.word not in (-1, i) and is_pal(u, k):
                out.append([i, node.word])     # case 1: w shorter, u's rest is a palindrome
            node = node.children.get(ch)
            if node is None:
                break
        else:
            for j in node.pal_below:           # case 2: u used up
                if j != i:
                    out.append([i, j])
    return out


# ------------------------------------------------------------------------ tests


def brute(words):
    return sorted([i, j] for i, a in enumerate(words) for j, b in enumerate(words)
                  if i != j and is_pal(a + b))


def test_classic():
    assert sorted(palindrome_pairs(["abcd", "dcba", "lls", "s", "sssll"])) == \
        [[0, 1], [1, 0], [2, 4], [3, 2]]
    assert sorted(palindrome_pairs(["bat", "tab", "cat"])) == [[0, 1], [1, 0]]
    assert sorted(palindrome_pairs(["a", ""])) == [[0, 1], [1, 0]]


def test_matches_brute_force():
    random.seed(16)
    for _ in range(300):
        words = list({"".join(random.choice("ab") for _ in range(random.randint(0, 4)))
                      for _ in range(random.randint(1, 10))})
        got = sorted(palindrome_pairs(words))
        assert got == brute(words)             # also proves no duplicates


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
