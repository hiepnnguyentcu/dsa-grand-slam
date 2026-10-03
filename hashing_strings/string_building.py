"""String building & parsing — reverse words, compression, encode/decode, LCP, zigzag.

Signs: "reverse the words", "compress runs (aaabb -> a3b2)", "serialise a
       list of strings into one string and back", "longest common prefix",
       "write the string in a zigzag and read row by row", any output built
       one piece at a time.
Approach: Python strings are immutable, so s += c in a loop can be O(n^2).
          Append pieces to a list and "".join once. When the input is a char
          array to edit IN PLACE, use a read pointer and a write pointer.
          Encode/decode: prefix each string with its length and a delimiter
          ("5#hello"); the decoder reads the number, then exactly that many
          chars, so any content (even "#") is safe. LCP: compare column by
          column across all strings, stop at the first mismatch or end.
          Zigzag: walk rows 0..R-1..0 and append each char to its row.
Complexity: O(total length) for all of these; LCP O(n * L) worst case.
Gotchas:
  - Reverse words: split() with no argument drops leading, trailing and
    repeated spaces; split(" ") keeps empty strings.
  - Compression in place (LC 443): counts >= 10 write several digit chars;
    a count of 1 writes no digit.
  - Delimiter-only encodings ("a,b") break when strings contain the
    delimiter; escaping works but length prefixes are simpler.
  - Zigzag with numRows == 1 must return s unchanged (the step never flips).
  - Roman numerals: math_algorithms/base_conversion.py. atoi with 32-bit
    clamping: math_algorithms/digits.py. Palindrome checks with skips:
    sliding_window/opposite_ends.py. LCP via a trie: tries/prefix_queries.py.

Run the tests at the bottom with:  python3 hashing_strings/string_building.py
"""


# ---------------------------------------------------------------- implementation


def reverse_words(s):
    """LC 151. Words in reverse order, single spaces, no padding."""
    return " ".join(reversed(s.split()))


def reverse_words_in_place(chars):
    """LC 186. chars is a list with single spaces; reverse word order in place.

    Reverse the whole list, then reverse each word back. O(1) extra space.
    """
    def rev(i, j):
        while i < j:
            chars[i], chars[j] = chars[j], chars[i]
            i, j = i + 1, j - 1

    rev(0, len(chars) - 1)
    start = 0
    for i in range(len(chars) + 1):
        if i == len(chars) or chars[i] == " ":
            rev(start, i - 1)
            start = i + 1
    return chars


def compress(chars):
    """LC 443. Run-length encode chars in place; return the new length."""
    write = read = 0
    while read < len(chars):
        c, start = chars[read], read
        while read < len(chars) and chars[read] == c:
            read += 1
        chars[write] = c
        write += 1
        run = read - start
        if run > 1:
            for d in str(run):
                chars[write] = d
                write += 1
    return write


def compress_string(s):
    """'aabcccccaaa' -> 'a2b1c5a3', or s itself if that isn't shorter."""
    out, i = [], 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(s[i] + str(j - i))
        i = j
    t = "".join(out)
    return t if len(t) < len(s) else s


def encode(strs):
    """LC 271. Length-prefixed: ['ab', ''] -> '2#ab0#'."""
    return "".join(f"{len(s)}#{s}" for s in strs)


def decode(s):
    out, i = [], 0
    while i < len(s):
        j = s.index("#", i)              # the length ends at the first '#'
        n = int(s[i:j])
        out.append(s[j + 1:j + 1 + n])   # then take exactly n chars, whatever they are
        i = j + 1 + n
    return out


def longest_common_prefix(strs):
    """LC 14. Vertical scan."""
    if not strs:
        return ""
    for i, c in enumerate(strs[0]):
        for s in strs[1:]:
            if i == len(s) or s[i] != c:
                return strs[0][:i]
    return strs[0]


def zigzag_convert(s, num_rows):
    """LC 6."""
    if num_rows == 1 or num_rows >= len(s):
        return s
    rows = [[] for _ in range(num_rows)]
    r, step = 0, 1
    for c in s:
        rows[r].append(c)
        if r == 0:
            step = 1
        elif r == num_rows - 1:
            step = -1
        r += step
    return "".join("".join(row) for row in rows)


# ------------------------------------------------------------------------ tests


def test_examples():
    assert reverse_words("  the sky   is blue ") == "blue is sky the"
    assert "".join(reverse_words_in_place(list("the sky is blue"))) == "blue is sky the"
    chars = list("abbbbbbbbbbbbc")
    assert compress(chars) == 5 and chars[:5] == list("ab12c")
    assert compress_string("aabcccccaaa") == "a2b1c5a3"
    assert compress_string("abc") == "abc"
    assert decode(encode(["lint", "code", "", "#3#", "5#x"])) == ["lint", "code", "", "#3#", "5#x"]
    assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"
    assert longest_common_prefix(["dog", "racecar", "car"]) == ""
    assert zigzag_convert("PAYPALISHIRING", 3) == "PAHNAPLSIIGYIR"
    assert zigzag_convert("PAYPALISHIRING", 4) == "PINALSIGYAHRPI"
    assert zigzag_convert("AB", 1) == "AB"


def test_reverse_words_both_ways_agree():
    import random

    rng = random.Random(1)
    for _ in range(300):
        words = ["".join(rng.choice("ab") for _ in range(rng.randint(1, 3)))
                 for _ in range(rng.randint(1, 5))]
        padded = (" " * rng.randint(0, 2)
                  + "".join(w + " " * rng.randint(1, 3) for w in words) + " " * rng.randint(0, 2))
        assert reverse_words(padded) == " ".join(words[::-1])
        assert "".join(reverse_words_in_place(list(" ".join(words)))) == " ".join(words[::-1])


def test_compress_matches_groupby():
    import random
    from itertools import groupby

    rng = random.Random(2)
    for _ in range(300):
        s = "".join(rng.choice("ab") * rng.randint(1, 12) for _ in range(rng.randint(0, 4)))
        expect = "".join(k + (str(n) if n > 1 else "")
                         for k, n in ((k, len(list(g))) for k, g in groupby(s)))
        chars = list(s)
        n = compress(chars)
        assert "".join(chars[:n]) == expect
        full = "".join(k + str(len(list(g))) for k, g in groupby(s))
        assert compress_string(s) == (full if len(full) < len(s) else s)


def test_encode_decode_round_trips_hostile_strings():
    import random

    rng = random.Random(3)
    for _ in range(500):
        strs = ["".join(rng.choice("a#1 ") for _ in range(rng.randint(0, 6)))
                for _ in range(rng.randint(0, 5))]
        assert decode(encode(strs)) == strs


def test_lcp_matches_brute_force():
    import random

    rng = random.Random(4)
    for _ in range(500):
        strs = ["".join(rng.choice("ab") for _ in range(rng.randint(0, 4)))
                for _ in range(rng.randint(1, 4))]
        k = max(k for k in range(len(min(strs, key=len)) + 1)
                if all(s[:k] == strs[0][:k] for s in strs))
        assert longest_common_prefix(strs) == strs[0][:k]


def test_zigzag_matches_grid_simulation():
    import random

    def grid(s, r):  # place chars on an explicit 2D grid, read row by row
        if r == 1:
            return s
        cells, row, col, down = {}, 0, 0, True
        for c in s:
            cells[(row, col)] = c
            if down and row == r - 1:
                down = False
            elif not down and row == 0:
                down = True
            if down:
                row += 1
            else:
                row, col = row - 1, col + 1
        return "".join(cells[k] for k in sorted(cells))

    rng = random.Random(5)
    for _ in range(300):
        s = "".join(rng.choice("abcdef") for _ in range(rng.randint(1, 20)))
        r = rng.randint(1, 6)
        assert zigzag_convert(s, r) == grid(s, r)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
