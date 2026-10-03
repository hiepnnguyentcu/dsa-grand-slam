"""Hash map / set lookups — complements, seen-before, first unique, bijections.

Signs: "find a pair that sums to target" on UNSORTED input with indices,
       "any duplicate", "duplicate within k positions", "first unique /
       first repeating", "same pattern" (isomorphic strings, word pattern),
       "how many pairs", intersection of two arrays.
Approach: trade O(n) memory for O(1) lookups. Walk once; before storing the
          current item, ask the map about the thing you NEED (target - x, or
          x itself). Store what a future item will ask for: value -> index
          for pairs, value -> last index for distance checks, value -> count
          for first-unique. For "same pattern", keep TWO maps (a -> b and
          b -> a): a bijection fails if either direction disagrees.
Complexity: O(n) time, O(n) space; O(1) average per lookup.
Gotchas:
  - Two sum: check BEFORE inserting, or x pairs with itself when 2x == target.
  - Pair counting with duplicates: add seen[target - x] to the answer, then
    bump seen[x]; never store only one index per value.
  - Isomorphic needs both directions: "ab" -> "aa" passes a one-way map.
  - Word pattern: split the words first and compare lengths.
  - Unhashable keys: lists -> tuple(lst); sets -> frozenset.
  - Sorted input + O(1) space -> two pointers (sliding_window/opposite_ends.py).
  - Subarray sum = k is prefix sums + this lookup (prefix_sums/prefix_hashmap.py).

Run the tests at the bottom with:  python3 hashing_strings/hash_lookup.py
"""

from collections import Counter


# ---------------------------------------------------------------- implementation


def two_sum(a, target):
    """LC 1. Indices [i, j] (i < j) with a[i] + a[j] == target, or []."""
    seen = {}  # value -> index
    for j, x in enumerate(a):
        if target - x in seen:          # ask first...
            return [seen[target - x], j]
        seen[x] = j                     # ...then store
    return []


def count_pairs(a, target):
    """Number of index pairs i < j with a[i] + a[j] == target."""
    seen, total = {}, 0
    for x in a:
        total += seen.get(target - x, 0)
        seen[x] = seen.get(x, 0) + 1
    return total


def contains_duplicate(a):
    """LC 217."""
    seen = set()
    for x in a:
        if x in seen:
            return True
        seen.add(x)
    return False


def contains_nearby_duplicate(a, k):
    """LC 219. Some i != j with a[i] == a[j] and |i - j| <= k."""
    last = {}  # value -> last index; the latest is always the closest
    for i, x in enumerate(a):
        if x in last and i - last[x] <= k:
            return True
        last[x] = i
    return False


def first_unique_char(s):
    """LC 387. Index of the first char that occurs once, or -1."""
    count = Counter(s)                  # pass 1: count
    for i, c in enumerate(s):           # pass 2: first with count 1
        if count[c] == 1:
            return i
    return -1


def first_repeating(a):
    """First value whose second occurrence comes earliest, or None."""
    seen = set()
    for x in a:
        if x in seen:
            return x
        seen.add(x)
    return None


def is_isomorphic(s, t):
    """LC 205. A one-to-one char mapping turns s into t."""
    if len(s) != len(t):
        return False
    fwd, back = {}, {}
    for a, b in zip(s, t):
        if fwd.setdefault(a, b) != b or back.setdefault(b, a) != a:
            return False
    return True


def word_pattern(pattern, s):
    """LC 290. Bijection between pattern letters and words of s."""
    words = s.split()
    if len(words) != len(pattern):
        return False
    fwd, back = {}, {}
    for c, w in zip(pattern, words):
        if fwd.setdefault(c, w) != w or back.setdefault(w, c) != c:
            return False
    return True


def first_occurrence_signature(seq):
    """Map each item to the index of its first appearance: "egg" -> [0, 1, 1].

    Two sequences follow the same pattern iff their signatures are equal —
    a one-line alternative to the two-map check.
    """
    first = {}
    return [first.setdefault(x, len(first)) for x in seq]


def intersection(a, b):
    """LC 349. Distinct values in both, sorted."""
    return sorted(set(a) & set(b))


def intersect_with_counts(a, b):
    """LC 350. Multiset intersection, sorted."""
    ca = Counter(a)
    out = []
    for x in b:
        if ca[x] > 0:
            ca[x] -= 1
            out.append(x)
    return sorted(out)


# ------------------------------------------------------------------------ tests


def test_examples():
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum([3, 3], 6) == [0, 1]
    assert two_sum([3, 2, 4], 6) == [1, 2]       # 3 must not pair with itself
    assert first_unique_char("loveleetcode") == 2
    assert first_unique_char("aabb") == -1
    assert is_isomorphic("egg", "add") and is_isomorphic("paper", "title")
    assert not is_isomorphic("foo", "bar")
    assert not is_isomorphic("ab", "aa")         # one-way map would pass this
    assert not is_isomorphic("aa", "ab")
    assert word_pattern("abba", "dog cat cat dog")
    assert not word_pattern("abba", "dog dog dog dog")
    assert not word_pattern("aaa", "dog dog")


def test_two_sum_and_count_pairs_match_brute_force():
    import random

    rng = random.Random(1)
    for _ in range(400):
        a = [rng.randint(-5, 5) for _ in range(rng.randint(0, 12))]
        t = rng.randint(-6, 6)
        pairs = [(i, j) for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] + a[j] == t]
        got = two_sum(a, t)
        if pairs:
            i, j = got
            assert i < j and a[i] + a[j] == t
        else:
            assert got == []
        assert count_pairs(a, t) == len(pairs)


def test_duplicates_match_brute_force():
    import random

    rng = random.Random(2)
    for _ in range(400):
        a = [rng.randint(0, 9) for _ in range(rng.randint(0, 12))]
        k = rng.randint(0, 5)
        n = len(a)
        assert contains_duplicate(a) == (len(set(a)) < n)
        assert contains_nearby_duplicate(a, k) == any(
            a[i] == a[j] for i in range(n) for j in range(i + 1, min(n, i + k + 1)))
        dup_end = [j for j in range(n) if a[j] in a[:j]]
        assert first_repeating(a) == (a[dup_end[0]] if dup_end else None)


def test_first_unique_matches_count_scan():
    import random

    rng = random.Random(3)
    for _ in range(300):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 10)))
        expect = next((i for i, c in enumerate(s) if s.count(c) == 1), -1)
        assert first_unique_char(s) == expect


def test_isomorphic_matches_signature_and_brute_force():
    import random
    from itertools import permutations

    def brute(s, t):  # try every injective map from s's letters into t's alphabet
        if len(s) != len(t):
            return False
        letters = sorted(set(s))
        for img in permutations("abc", len(letters)):
            m = dict(zip(letters, img))
            if "".join(m[c] for c in s) == t:
                return True
        return False

    rng = random.Random(4)
    for _ in range(500):
        n = rng.randint(0, 6)
        s = "".join(rng.choice("abc") for _ in range(n))
        t = "".join(rng.choice("abc") for _ in range(n + rng.choice([0, 0, 0, 1])))
        expect = brute(s, t)
        assert is_isomorphic(s, t) == expect
        assert (len(s) == len(t) and first_occurrence_signature(s) == first_occurrence_signature(t)) == expect


def test_word_pattern_matches_signature():
    import random

    rng = random.Random(5)
    for _ in range(300):
        p = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
        words = [rng.choice(["dog", "cat", "fish"]) for _ in range(len(p) + rng.choice([0, 0, 1]))]
        expect = len(words) == len(p) and first_occurrence_signature(p) == first_occurrence_signature(words)
        assert word_pattern(p, " ".join(words)) == expect


def test_intersections_match_brute_force():
    import random

    rng = random.Random(6)
    for _ in range(300):
        a = [rng.randint(0, 6) for _ in range(rng.randint(0, 8))]
        b = [rng.randint(0, 6) for _ in range(rng.randint(0, 8))]
        assert intersection(a, b) == sorted(x for x in set(a) if x in b)
        expect = sorted(x for x in set(a) for _ in range(min(a.count(x), b.count(x))))
        assert intersect_with_counts(a, b) == expect


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
