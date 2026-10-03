"""Partitioning — cut as early as the constraint allows.

Signs: "split into as many parts as possible so that ...", "each letter in at
       most one part", "balanced substrings", "group cards into runs of W
       consecutive values".
Approach: a cut at position i is legal on its own terms (no letter on both
          sides, prefix balanced), independent of other cuts. So the most parts
          = take every legal cut, which is exactly "cut the moment you can".
  - Partition labels: record each letter's last index; extend the current
    part's end to the max last index seen; cut when i == end.
  - Balanced split: running L - R count; cut whenever it returns to 0.
  - Hand of straights: the smallest remaining card must *start* a run (nothing
    smaller can contain it), so peel runs from the smallest value up.
Complexity: labels and balanced split O(n); straights O(n log n) for sorting
            the distinct values, then O(n * W) worst case.
Gotchas:
  - Partition labels returns part *sizes*, not the strings.
  - Hand of straights: len(hand) % W != 0 is an instant False.
  - Straights: subtract the count of the starting card from all W values at
    once — it is the same as peeling one run at a time, but O(distinct * W).

Run the tests at the bottom with:  python3 greedy/partitioning.py
"""

import random
from collections import Counter
from functools import cache
from itertools import product


# ---------------------------------------------------------------- implementation


def partition_labels(s):
    """Sizes of the most parts such that each letter appears in one part."""
    last = {c: i for i, c in enumerate(s)}
    sizes, start, end = [], 0, 0
    for i, c in enumerate(s):
        end = max(end, last[c])
        if i == end:
            sizes.append(end - start + 1)
            start = i + 1
    return sizes


def balanced_split(s):
    """Most pieces of an 'L'/'R' string where each piece has equal L and R."""
    bal = pieces = 0
    for c in s:
        bal += 1 if c == "L" else -1
        if bal == 0:
            pieces += 1
    return pieces


def hand_of_straights(hand, W):
    """Can the cards be split into groups of W consecutive values?"""
    if len(hand) % W:
        return False
    count = Counter(hand)
    for v in sorted(count):
        k = count[v]
        if k == 0:
            continue
        for x in range(v, v + W):  # k runs start at v
            if count[x] < k:
                return False
            count[x] -= k
    return True


# ------------------------------------------------------------------------ tests


def brute_cuts(s, legal):
    """Finest split of s whose parts satisfy legal(parts), over all cut sets."""
    best = None
    for mask in product([0, 1], repeat=max(0, len(s) - 1)):
        parts, start = [], 0
        for i, cut in enumerate(mask):
            if cut:
                parts.append(s[start:i + 1])
                start = i + 1
        parts.append(s[start:])
        if legal(parts) and (best is None or len(parts) > len(best)):
            best = parts
    return best


def brute_labels(s):
    def disjoint(parts):
        return sum(len(set(p)) for p in parts) == len(set(s))

    return [len(p) for p in brute_cuts(s, disjoint)] if s else []


def brute_balanced(s):
    if not s:
        return 0
    return len(brute_cuts(s, lambda parts: all(p.count("L") == p.count("R") for p in parts)))


def brute_straights(hand, W):
    """Try removing a run starting at *any* present value, not just the min."""

    @cache
    def go(cards):  # sorted tuple
        if not cards:
            return True
        for start in set(cards):
            rest = list(cards)
            ok = True
            for x in range(start, start + W):
                if x not in rest:
                    ok = False
                    break
                rest.remove(x)
            if ok and go(tuple(rest)):
                return True
        return False

    return go(tuple(sorted(hand)))


def test_partition_labels_example():
    assert partition_labels("ababcbacadefegdehijhklij") == [9, 7, 8]
    assert partition_labels("eccbbbbdec") == [10]


def test_partition_labels_matches_brute_force():
    random.seed(15)
    for _ in range(300):
        s = "".join(random.choice("abcd") for _ in range(random.randint(0, 10)))
        assert partition_labels(s) == brute_labels(s)


def test_balanced_split():
    assert balanced_split("RLRRLLRLRL") == 4
    assert balanced_split("LLLLRRRR") == 1
    random.seed(16)
    for _ in range(200):
        half = random.randint(0, 6)
        chars = list("L" * half + "R" * half)
        random.shuffle(chars)
        s = "".join(chars)
        assert balanced_split(s) == brute_balanced(s)


def test_hand_of_straights():
    assert hand_of_straights([1, 2, 3, 6, 2, 3, 4, 7, 8], 3)
    assert not hand_of_straights([1, 2, 3, 4, 5], 4)
    random.seed(17)
    for _ in range(400):
        W = random.randint(1, 3)
        hand = [random.randint(1, 6) for _ in range(W * random.randint(1, 3))]
        assert hand_of_straights(hand, W) == brute_straights(hand, W)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
