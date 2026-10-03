"""Frequency counting & canonical keys — anagrams, ransom note, grouping.

Signs: "is t an anagram of s", "can s be built from t's letters", "group
       strings that are rearrangements / shifts of each other", "values in
       1..n, find the ones seen twice", "min changes to make an anagram".
Approach: two strings are the same multiset iff their counts match. Compare
          Counters, or keep ONE count array: +1 for s, -1 for t, all zero at
          the end. To GROUP, map each item to a canonical key that is equal
          exactly for items in the same class — sorted(word), a 26-count
          tuple, or a shift-normalised tuple — and bucket in a dict of lists.
          Values in 1..n can use the array itself as the hash table: mark
          index v - 1 by negating it.
Complexity: counting O(n) time, O(k) space for an alphabet of k. Group
            anagrams: sorted key O(m * L log L), count key O(m * (L + 26)).
            In-place marking O(n) time, O(1) extra space.
Gotchas:
  - Keys must be hashable: tuple(count), "".join(sorted(w)) — not a list.
  - Count-tuple key wins for long words over a small alphabet; sorted key is
    simpler and fine for short words or Unicode.
  - Ransom note is one-directional: magazine may have extra letters.
  - Negation marking destroys the input; restore with abs() if needed.
  - Top-k frequent (heap / bucket sort) lives in stacks_heaps/top_k.py.
  - Anagram windows inside a longer string: sliding_window/fixed_window.py.

Run the tests at the bottom with:  python3 hashing_strings/frequency_signatures.py
"""

from collections import Counter, defaultdict


# ---------------------------------------------------------------- implementation


def is_anagram(s, t):
    """LC 242. One count array: +1 for s, -1 for t."""
    if len(s) != len(t):
        return False
    count = defaultdict(int)
    for a, b in zip(s, t):
        count[a] += 1
        count[b] -= 1
    return all(v == 0 for v in count.values())


def can_construct(ransom, magazine):
    """LC 383. Every letter of ransom available in magazine (each used once)."""
    have = Counter(magazine)
    for c in ransom:
        if have[c] == 0:
            return False
        have[c] -= 1
    return True


def min_steps_to_anagram(s, t):
    """LC 1347. Chars of t to replace so t becomes an anagram of s (same length)."""
    return sum((Counter(s) - Counter(t)).values())


def group_anagrams_sorted(words):
    """LC 49 with key = sorted letters. O(m * L log L)."""
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)
    return list(groups.values())


def group_anagrams_count(words):
    """LC 49 with key = 26-letter count tuple. O(m * (L + 26)), lowercase a-z."""
    groups = defaultdict(list)
    for w in words:
        count = [0] * 26
        for c in w:
            count[ord(c) - 97] += 1
        groups[tuple(count)].append(w)
    return list(groups.values())


def group_shifted(words):
    """LC 249. Group strings equal up to a Caesar shift: key = gaps mod 26."""
    groups = defaultdict(list)
    for w in words:
        key = tuple((ord(c) - ord(w[0])) % 26 for c in w)
        groups[key].append(w)
    return list(groups.values())


def find_duplicates(a):
    """LC 442. Values in 1..n appearing twice, in order of second sighting.

    Index v - 1 is v's slot; a negative slot means "seen". O(1) extra space.
    Mutates a and restores it before returning.
    """
    out = []
    for x in a:
        i = abs(x) - 1
        if a[i] < 0:
            out.append(abs(x))
        else:
            a[i] = -a[i]
    for i in range(len(a)):
        a[i] = abs(a[i])
    return out


def find_disappeared(a):
    """LC 448. Values in 1..n that never appear. Same marking trick."""
    for x in a:
        i = abs(x) - 1
        a[i] = -abs(a[i])
    out = [i + 1 for i, x in enumerate(a) if x > 0]
    for i in range(len(a)):
        a[i] = abs(a[i])
    return out


# ------------------------------------------------------------------------ tests


def _canon(groups):
    return sorted(sorted(g) for g in groups)


def _rand_word(rng, alpha="abc", hi=5):
    return "".join(rng.choice(alpha) for _ in range(rng.randint(0, hi)))


def test_examples():
    assert is_anagram("anagram", "nagaram") and not is_anagram("rat", "car")
    assert can_construct("aa", "aab") and not can_construct("aa", "ab")
    assert min_steps_to_anagram("leetcode", "practice") == 5
    assert _canon(group_anagrams_sorted(["eat", "tea", "tan", "ate", "nat", "bat"])) == \
        [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
    assert _canon(group_shifted(["abc", "bcd", "acef", "xyz", "az", "ba", "a", "z"])) == \
        [["a", "z"], ["abc", "bcd", "xyz"], ["acef"], ["az", "ba"]]
    assert find_duplicates([4, 3, 2, 7, 8, 2, 3, 1]) == [2, 3]
    assert find_disappeared([4, 3, 2, 7, 8, 2, 3, 1]) == [5, 6]


def test_anagram_and_ransom_match_sorting():
    import random

    rng = random.Random(1)
    for _ in range(500):
        s, t = _rand_word(rng), _rand_word(rng)
        assert is_anagram(s, t) == (sorted(s) == sorted(t))
        assert can_construct(s, t) == all(s.count(c) <= t.count(c) for c in s)


def test_min_steps_matches_greedy_count():
    import random

    rng = random.Random(2)
    for _ in range(300):
        n = rng.randint(0, 7)
        s = "".join(rng.choice("abc") for _ in range(n))
        t = "".join(rng.choice("abc") for _ in range(n))
        # chars of t that can stay = multiset overlap
        keep = sum(min(s.count(c), t.count(c)) for c in "abc")
        assert min_steps_to_anagram(s, t) == n - keep


def test_both_group_keys_agree_with_pairwise_check():
    import random

    rng = random.Random(3)
    for _ in range(200):
        words = [_rand_word(rng, "abcd", 4) for _ in range(rng.randint(0, 10))]
        a, b = _canon(group_anagrams_sorted(words)), _canon(group_anagrams_count(words))
        assert a == b
        # brute force: union words pairwise by sorted equality
        groups = []
        for w in words:
            for g in groups:
                if sorted(g[0]) == sorted(w):
                    g.append(w)
                    break
            else:
                groups.append([w])
        assert a == _canon(groups)


def test_group_shifted_matches_brute_force():
    import random

    def shift(w, k):
        return "".join(chr((ord(c) - 97 + k) % 26 + 97) for c in w)

    rng = random.Random(4)
    for _ in range(200):
        words = [_rand_word(rng, "abyz", 3) or "a" for _ in range(rng.randint(0, 8))]
        groups = []
        for w in words:
            for g in groups:
                if any(shift(g[0], k) == w for k in range(26)):
                    g.append(w)
                    break
            else:
                groups.append([w])
        assert _canon(group_shifted(words)) == _canon(groups)


def test_marking_matches_counter_and_restores_input():
    import random

    rng = random.Random(5)
    for _ in range(300):
        n = rng.randint(1, 10)
        a = [rng.randint(1, n) for _ in range(n)]
        while any(v > 2 for v in Counter(a).values()):   # LC 442: at most twice
            a = [rng.randint(1, n) for _ in range(n)]
        orig = a[:]
        seen, expect = set(), []
        for x in a:
            if x in seen:
                expect.append(x)
            seen.add(x)
        assert find_duplicates(a) == expect and a == orig
        assert find_disappeared(a) == [v for v in range(1, n + 1) if v not in orig] and a == orig


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
