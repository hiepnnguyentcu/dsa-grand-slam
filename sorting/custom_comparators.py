"""Custom ordering — key tuples, cmp_to_key, stable multi-pass, rank maps.

Signs: "sort by X then by Y", "order defined by another string/array",
       "arrange numbers to form the largest number", "sort by frequency",
       "letter-logs before digit-logs", ties must keep input order.
Approach:
  - Prefer a KEY: a tuple sorts field by field. Negate numeric fields for
    descending; for descending strings, sort twice (see below) or use cmp.
  - Pairwise rule that isn't a key (a + b vs b + a): functools.cmp_to_key.
    cmp(a, b) < 0 means a goes first.
  - Stability trick: sort by the secondary key first, then by the primary.
    Equal primaries keep the secondary order. Lets you mix asc/desc on
    strings without negation.
  - Order given by another sequence: rank = {ch: i}, key = rank.get(x, big).
Complexity: O(n log n) comparisons; each costs the key/cmp cost (O(L) for
            strings). Counting variants (custom sort string, relative sort
            array) are O(n + k).
Gotchas:
  - A cmp must be a consistent total order (transitive), or the result is
    garbage. a + b vs b + a is transitive; "a[0] vs b[0] else len" may not be.
  - Largest number: all zeros -> "0", not "000".
  - cmp_to_key returns a key class — pass it as key=, not cmp= (gone in Py3).
  - key=lambda x: -x fails for strings; reverse=True flips ties too, which
    breaks "keep input order on ties" unless you also reverse the input.

Run the tests at the bottom with:  python3 sorting/custom_comparators.py
"""

import random
from collections import Counter
from functools import cmp_to_key
from itertools import permutations


# ---------------------------------------------------------------- implementation


def largest_number(nums):
    """Concatenate to the largest number. a before b iff a + b > b + a."""
    strs = [str(x) for x in nums]
    strs.sort(key=cmp_to_key(lambda a, b: (b + a > a + b) - (b + a < a + b)))
    s = "".join(strs)
    return "0" if s and s[0] == "0" else s


def sort_people(people):
    """(name, age, city): age DESC, then name ASC. Negate the number."""
    return sorted(people, key=lambda p: (-p[1], p[0]))


def sort_two_pass(rows):
    """(name, score): name DESC, then score ASC — no negating strings.

    Sort by the secondary key first, then by the primary; stability keeps the
    secondary order inside equal primaries.
    """
    out = sorted(rows, key=lambda r: r[1])
    out.sort(key=lambda r: r[0], reverse=True)   # reverse=True is still stable
    return out


def reorder_log_files(logs):
    """Letter-logs first, sorted by (content, id); digit-logs after, in input order."""

    def key(log):
        ident, rest = log.split(" ", 1)
        if rest[0].isalpha():
            return (0, rest, ident)
        return (1,)                   # all digit-logs tie -> stable keeps order

    return sorted(logs, key=key)


def custom_sort_string(order, s):
    """Characters of s in the order given by `order`; others go at the end.

    Counting version: O(|s| + |order|). Key version: sorted(s, key=rank).
    """
    count = Counter(s)
    out = []
    for ch in order:
        out.append(ch * count.pop(ch, 0))
    for ch, c in count.items():
        out.append(ch * c)
    return "".join(out)


def frequency_sort(s):
    """Characters by frequency DESC; ties grouped (any order between groups)."""
    count = Counter(s)
    return "".join(ch * c for ch, c in sorted(count.items(), key=lambda t: -t[1]))


def relative_sort_array(arr1, arr2):
    """arr1 ordered like arr2; values not in arr2 go last, ascending."""
    rank = {x: i for i, x in enumerate(arr2)}
    return sorted(arr1, key=lambda x: (rank.get(x, len(arr2)), x))


# ------------------------------------------------------------------------ tests


def test_largest_number_examples():
    assert largest_number([10, 2]) == "210"
    assert largest_number([3, 30, 34, 5, 9]) == "9534330"
    assert largest_number([0, 0]) == "0"
    assert largest_number([0]) == "0"


def test_largest_number_matches_permutations():
    random.seed(41)
    for _ in range(200):
        a = [random.choice([0, 1, 3, 9, 10, 30, 34, 121, 12, 5])
             for _ in range(random.randint(1, 6))]
        brute = max(int("".join(map(str, p))) for p in permutations(a))
        assert largest_number(a) == str(brute)


def test_sort_people_multi_key():
    random.seed(42)
    names = ["ann", "bob", "cat", "dan"]
    for _ in range(100):
        ppl = [(random.choice(names), random.randint(20, 23), i) for i in range(10)]
        got = sort_people(ppl)
        for x, y in zip(got, got[1:]):
            assert x[1] > y[1] or (x[1] == y[1] and x[0] <= y[0])
        # stability: full ties keep input order (third field = input index)
        for x, y in zip(got, got[1:]):
            if x[:2] == y[:2]:
                assert x[2] < y[2]


def test_two_pass_equals_cmp_version():
    random.seed(43)

    def cmp(a, b):
        if a[0] != b[0]:
            return -1 if a[0] > b[0] else 1
        return a[1] - b[1]

    for _ in range(200):
        rows = [(random.choice("abc"), random.randint(0, 3), i) for i in range(12)]
        assert sort_two_pass(rows) == sorted(rows, key=cmp_to_key(cmp))


def test_reorder_log_files():
    logs = ["dig1 8 1 5 1", "let1 art can", "dig2 3 6", "let2 own kit dig", "let3 art zero"]
    assert reorder_log_files(logs) == [
        "let1 art can", "let3 art zero", "let2 own kit dig", "dig1 8 1 5 1", "dig2 3 6"]
    logs = ["a1 9 2 3 1", "g1 act car", "zo4 4 7", "ab1 off key dog", "a8 act zoo", "a2 act car"]
    assert reorder_log_files(logs) == [
        "a2 act car", "g1 act car", "a8 act zoo", "ab1 off key dog", "a1 9 2 3 1", "zo4 4 7"]


def test_custom_sort_string_matches_key_sort():
    assert custom_sort_string("cba", "abcd") == "cbad"
    random.seed(44)
    for _ in range(200):
        order = "".join(random.sample("abcdef", random.randint(0, 6)))
        s = "".join(random.choice("abcdefgh") for _ in range(random.randint(0, 15)))
        got = custom_sort_string(order, s)
        rank = {c: i for i, c in enumerate(order)}
        assert sorted(got) == sorted(s)
        ranks = [rank.get(c, len(order)) for c in got]
        assert ranks == sorted(ranks)


def test_frequency_sort():
    random.seed(45)
    assert frequency_sort("") == ""
    for _ in range(200):
        s = "".join(random.choice("aAbc1") for _ in range(random.randint(0, 20)))
        got = frequency_sort(s)
        assert sorted(got) == sorted(s)
        c = Counter(s)
        freqs = [c[ch] for ch in got]
        assert freqs == sorted(freqs, reverse=True)
        groups = [ch for i, ch in enumerate(got) if i == 0 or got[i - 1] != ch]
        assert len(groups) == len(set(groups))      # each char is contiguous


def test_relative_sort_array():
    assert relative_sort_array([2, 3, 1, 3, 2, 4, 6, 7, 9, 2, 19],
                               [2, 1, 4, 3, 9, 6]) == [2, 2, 2, 1, 4, 3, 3, 9, 6, 7, 19]
    random.seed(46)
    for _ in range(100):
        arr2 = random.sample(range(10), random.randint(0, 6))
        arr1 = [random.randrange(12) for _ in range(random.randint(0, 20))]
        got = relative_sort_array(arr1, arr2)
        head = [x for x in got if x in arr2]
        tail = [x for x in got if x not in arr2]
        assert got == head + tail and tail == sorted(tail)
        assert head == [x for x in arr2 for _ in range(arr1.count(x))]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
