"""Majority element — hash count, then Boyer–Moore voting in O(1) space.

Signs: "element appearing more than n/2 times", "all elements appearing more
       than n/3 times", "dominant value", follow-up "in O(1) space".
Approach: the obvious way is a Counter. Boyer–Moore pairs off different
          values and cancels them: keep a candidate and a count; same value
          -> count += 1, different -> count -= 1, count 0 -> adopt the new
          value. A true majority outnumbers everything else combined, so it
          survives. For > n/3 keep TWO candidates; at most two values can
          exceed n/3. A second pass verifies, because the vote always returns
          SOMETHING even when no majority exists.
Complexity: Counter O(n) time, O(n) space. Boyer–Moore O(n) time, O(1) space.
Gotchas:
  - Verify unless the problem promises a majority exists (LC 169 does).
  - n/3 version: test "x == c1" and "x == c2" BEFORE the "count == 0"
    branches, or one value can occupy both slots.
  - "More than" is strict: n = 4, [1, 1, 2, 2] has no > n/2 element.
  - Generalises: > n/k needs k - 1 candidates (Misra–Gries).

Run the tests at the bottom with:  python3 hashing_strings/majority_vote.py
"""

from collections import Counter


# ---------------------------------------------------------------- implementation


def majority_counter(a):
    """Value occurring > len(a) // 2 times, or None. O(n) space."""
    if not a:
        return None
    x, c = Counter(a).most_common(1)[0]
    return x if c > len(a) // 2 else None


def majority_vote(a):
    """LC 169 with verification. Boyer–Moore, O(1) space."""
    cand, count = None, 0
    for x in a:
        if count == 0:
            cand = x
        count += 1 if x == cand else -1
    return cand if a and a.count(cand) > len(a) // 2 else None


def majority_ii(a):
    """LC 229. All values occurring > len(a) // 3 times, sorted. O(1) space."""
    c1, c2, n1, n2 = None, None, 0, 0
    for x in a:
        if x == c1:
            n1 += 1
        elif x == c2:
            n2 += 1
        elif n1 == 0:
            c1, n1 = x, 1
        elif n2 == 0:
            c2, n2 = x, 1
        else:                       # x differs from both: cancel one of each
            n1 -= 1
            n2 -= 1
    return sorted(c for c in {c1, c2} if c is not None and a.count(c) > len(a) // 3)


# ------------------------------------------------------------------------ tests


def test_examples():
    assert majority_vote([3, 2, 3]) == 3
    assert majority_vote([2, 2, 1, 1, 1, 2, 2]) == 2
    assert majority_vote([1, 1, 2, 2]) is None       # tie is not a majority
    assert majority_vote([]) is None
    assert majority_ii([3, 2, 3]) == [3]
    assert majority_ii([1, 2]) == [1, 2]
    assert majority_ii([1, 1, 1, 2, 2, 3, 3, 3]) == [1, 3]


def test_vote_matches_counter():
    import random

    rng = random.Random(1)
    for _ in range(1000):
        a = [rng.randint(0, 3) for _ in range(rng.randint(0, 12))]
        if rng.random() < 0.5 and a:                  # bias towards a real majority
            a += [a[0]] * len(a)
            rng.shuffle(a)
        assert majority_vote(a) == majority_counter(a)


def test_majority_ii_matches_counter():
    import random

    rng = random.Random(2)
    for _ in range(1000):
        a = [rng.randint(0, 4) for _ in range(rng.randint(0, 15))]
        expect = sorted(x for x, c in Counter(a).items() if c > len(a) // 3)
        assert majority_ii(a) == expect


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
