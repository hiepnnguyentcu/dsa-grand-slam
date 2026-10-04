"""Partitioning — cut a string into valid pieces.

Signs: "partition s so every piece is a palindrome", "restore IP addresses",
       "all ways to split into dictionary words".
Approach: loop from start -> start is where the next piece begins; i is where
          it ends. Piece = s[start:i+1]; if valid, recurse i + 1.
          start == len(s) -> every char is covered -> record.
Complexity: O(2^n * n) — n-1 gaps, each cut or not.
Gotchas:
  - Base case is start == len(s), not len(temp) == something (except IP:
    exactly 4 parts AND all chars used).
  - IP octet: no leading zero unless it IS "0"; value <= 255; length <= 3.
  - 140: memo on start if the dict is huge, else the tree explodes on
    "aaaa...ab".
  - Fewest cuts (132) is DP: dynamic_programming/palindrome_dp.py.

Run the tests at the bottom with:  python3 backtracking/partitioning.py
"""

import random
from itertools import product


# ---------------------------------------------------------------- implementation


def partition(s):
    """LC 131."""
    n = len(s)
    res = []

    def is_palindrome(piece):
        return piece == piece[::-1]

    def dfs(start, res, temp):
        if start == n:
            res.append(temp.copy())
            return
        for i in range(start, n):
            piece = s[start:i + 1]
            if not is_palindrome(piece):
                continue
            temp.append(piece)
            dfs(i + 1, res, temp)
            temp.pop()
    dfs(0, res, [])
    return res


def restore_ip_addresses(s):
    """LC 93."""
    n = len(s)
    res = []

    def is_valid(piece):
        if len(piece) > 1 and piece[0] == "0":
            return False
        return int(piece) <= 255

    def dfs(start, res, temp):
        if len(temp) == 4:
            if start == n:
                res.append(".".join(temp))
            return
        for i in range(start, min(start + 3, n)):
            piece = s[start:i + 1]
            if not is_valid(piece):
                continue
            temp.append(piece)
            dfs(i + 1, res, temp)
            temp.pop()
    dfs(0, res, [])
    return res


def word_break(s, word_dict):
    """LC 140. Every sentence s can be split into."""
    n = len(s)
    words = set(word_dict)
    res = []

    def dfs(start, res, temp):
        if start == n:
            res.append(" ".join(temp))
            return
        for i in range(start, n):
            piece = s[start:i + 1]
            if piece not in words:
                continue
            temp.append(piece)
            dfs(i + 1, res, temp)
            temp.pop()
    dfs(0, res, [])
    return res


# ------------------------------------------------------------------------ tests


def all_splits(s):
    """Every way to cut s, via a cut/no-cut bit per gap."""
    out = []
    for bits in product([0, 1], repeat=max(len(s) - 1, 0)):
        pieces, start = [], 0
        for i, b in enumerate(bits, 1):
            if b:
                pieces.append(s[start:i]); start = i
        pieces.append(s[start:])
        out.append(pieces)
    return out


def test_partition_vs_brute_force():
    assert sorted(partition("aab")) == [["a", "a", "b"], ["aa", "b"]]
    random.seed(1)
    for _ in range(50):
        s = "".join(random.choice("ab") for _ in range(random.randint(1, 10)))
        want = sorted(p for p in all_splits(s) if all(x == x[::-1] for x in p))
        assert sorted(partition(s)) == want


def test_restore_ip_addresses_vs_brute_force():
    assert sorted(restore_ip_addresses("25525511135")) == ["255.255.11.135", "255.255.111.35"]
    assert restore_ip_addresses("0000") == ["0.0.0.0"]
    random.seed(2)
    for _ in range(100):
        s = "".join(random.choice("0125") for _ in range(random.randint(4, 12)))
        want = sorted(".".join(p) for p in all_splits(s) if len(p) == 4 and all(
            len(x) <= 3 and (x == "0" or x[0] != "0") and int(x) <= 255 for x in p))
        assert sorted(restore_ip_addresses(s)) == want


def test_word_break_vs_brute_force():
    got = word_break("catsanddog", ["cat", "cats", "and", "sand", "dog"])
    assert sorted(got) == ["cat sand dog", "cats and dog"]
    random.seed(3)
    for _ in range(50):
        words = list({"".join(random.choice("ab") for _ in range(random.randint(1, 3))) for _ in range(4)})
        s = "".join(random.choice(words) for _ in range(random.randint(1, 4)))
        want = sorted(" ".join(p) for p in all_splits(s) if all(x in words for x in p))
        assert sorted(word_break(s, words)) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
