"""Partitioning — cut a string into pieces that each pass a test.

Signs: "partition s so that every substring is ...", "all ways to split",
       "restore IP addresses", "split into the maximum number of unique
       substrings".
Approach: the choice at each level is *where the next piece ends*. From
          position `start`, try every end in start+1..n; if s[start:end] is a
          valid piece, add it and recurse from `end`. Complete when
          start == n.
            - Palindrome partitioning: precompute is_pal[i][j] in O(n^2) so
              each check is O(1).
            - Restore IP: exactly 4 pieces of length 1-3, each 0-255, no
              leading zero. Prune when the remaining length cannot fit in the
              remaining pieces (more than 3 each or fewer than 1 each).
            - Max unique split: pieces must be pairwise distinct; carry a
              `used` set, and prune when even all remaining single chars
              cannot beat the best found.
Complexity: O(2^(n-1) * n) — there are 2^(n-1) ways to cut a string.
Gotchas:
  - "0" is a valid IP octet; "00", "01" are not.
  - Want only the *minimum* number of cuts or a count? That is DP
    (dynamic_programming/palindrome_dp.py, string_segmentation.py).
  - Slicing s[start:end] costs O(len); fine at these sizes, but precompute
    checks when the validity test is expensive.

Run the tests at the bottom with:  python3 backtracking/partitioning.py
"""

import random


# ---------------------------------------------------------------- implementation


def palindrome_partition(s):
    """Every way to cut s so that each piece is a palindrome."""
    n = len(s)
    is_pal = [[False] * (n + 1) for _ in range(n + 1)]  # is_pal[i][j]: s[i:j]
    for i in range(n, -1, -1):
        for j in range(i, n + 1):
            is_pal[i][j] = j - i < 2 or (s[i] == s[j - 1] and is_pal[i + 1][j - 1])

    out, path = [], []

    def go(start):
        if start == n:
            out.append(path[:])
            return
        for end in range(start + 1, n + 1):
            if is_pal[start][end]:
                path.append(s[start:end])
                go(end)
                path.pop()
    go(0)
    return out


def restore_ip(s):
    """All valid IPv4 addresses formed by inserting three dots into s."""
    n, out, path = len(s), [], []

    def go(start):
        left = 4 - len(path)
        if left == 0:
            if start == n:
                out.append(".".join(path))
            return
        if not left <= n - start <= 3 * left:
            return                            # remainder cannot fit
        for end in range(start + 1, min(start + 3, n) + 1):
            part = s[start:end]
            if (len(part) > 1 and part[0] == "0") or int(part) > 255:
                break                         # longer pieces fail too
            path.append(part)
            go(end)
            path.pop()
    go(0)
    return out


def max_unique_split(s):
    """Max number of pieces in a split of s where all pieces are distinct."""
    n, used, best = len(s), set(), [0]

    def go(start):
        if len(used) + (n - start) <= best[0]:
            return                            # cannot beat best even with 1-char pieces
        if start == n:
            best[0] = len(used)
            return
        for end in range(start + 1, n + 1):
            piece = s[start:end]
            if piece in used:
                continue
            used.add(piece)
            go(end)
            used.discard(piece)
    go(0)
    return best[0]


# ------------------------------------------------------------------------ tests


def all_splits(s):
    """Brute force: each of the n-1 gaps is cut or not."""
    n = len(s)
    if n == 0:
        return [[]]
    out = []
    for mask in range(1 << (n - 1)):
        parts, last = [], 0
        for i in range(n - 1):
            if mask >> i & 1:
                parts.append(s[last:i + 1]); last = i + 1
        parts.append(s[last:])
        out.append(parts)
    return out


def valid_octet(p):
    return 1 <= len(p) <= 3 and str(int(p)) == p and int(p) <= 255


def test_palindrome_partition_classic():
    assert palindrome_partition("aab") == [["a", "a", "b"], ["aa", "b"]]
    assert palindrome_partition("a") == [["a"]]


def test_palindrome_partition_random_vs_brute_force():
    random.seed(6)
    for _ in range(80):
        s = "".join(random.choice("ab") for _ in range(random.randint(1, 11)))
        want = sorted(p for p in all_splits(s) if all(x == x[::-1] for x in p))
        assert sorted(palindrome_partition(s)) == want


def test_restore_ip_classic():
    assert sorted(restore_ip("25525511135")) == ["255.255.11.135", "255.255.111.35"]
    assert restore_ip("0000") == ["0.0.0.0"]
    assert sorted(restore_ip("101023")) == sorted(
        ["1.0.10.23", "1.0.102.3", "10.1.0.23", "10.10.2.3", "101.0.2.3"])


def test_restore_ip_random_vs_brute_force():
    random.seed(7)
    for _ in range(150):
        s = "".join(random.choice("0123459") for _ in range(random.randint(1, 13)))
        want = sorted(".".join(p) for p in all_splits(s) if len(p) == 4 and all(map(valid_octet, p)))
        assert sorted(restore_ip(s)) == want


def test_max_unique_split_classic():
    assert max_unique_split("ababccc") == 5   # a b ab c cc
    assert max_unique_split("aba") == 2
    assert max_unique_split("aa") == 1


def test_max_unique_split_random_vs_brute_force():
    random.seed(8)
    for _ in range(80):
        s = "".join(random.choice("abc") for _ in range(random.randint(1, 11)))
        want = max(len(p) for p in all_splits(s) if len(set(p)) == len(p))
        assert max_unique_split(s) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
