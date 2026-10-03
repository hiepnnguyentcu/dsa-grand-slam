"""Two-pass constraints — satisfy one side, then the other.

Signs: each element must beat its neighbours on some key (candy by rating),
       "make every count unique with fewest deletions", "rebuild the queue from
       (height, people taller in front)".
Approach: split a two-sided rule into passes that each handle one side, or
          process in an order where earlier choices can't be broken later.
  - Candy: left-to-right gives c[i] = c[i-1] + 1 on a rise; right-to-left
    takes max(c[i], c[i+1] + 1) on a fall. Each value is the longest
    increasing run ending there from either side — a lower bound, so minimal.
  - Unique frequencies: sort counts descending; each count may be at most
    one below the previous kept count. Delete the excess (floored at 0).
  - Queue reconstruction: tallest first (ties: smaller k first), insert each
    person at index k. Shorter people inserted later are invisible to taller
    ones, so earlier placements stay correct.
Complexity: candy O(n); unique frequencies O(n + A log A) for A distinct
            letters; queue O(n^2) from list inserts.
Gotchas:
  - Candy: a single pass can't see a long decreasing run coming — you need
    both directions, and the second pass takes the max, not an overwrite.
  - Unique frequencies: once the cap reaches 0, every remaining letter is
    deleted entirely (count 0 may repeat).
  - Queue: sort key is (-h, k). Sorting by (h, k) ascending breaks it.

Run the tests at the bottom with:  python3 greedy/two_pass.py
"""

import random
from collections import Counter
from itertools import permutations, product


# ---------------------------------------------------------------- implementation


def candy(ratings):
    """Fewest candies: everyone >= 1, higher rating than a neighbour -> more."""
    n = len(ratings)
    c = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            c[i] = max(c[i], c[i + 1] + 1)
    return sum(c)


def min_deletions_unique_freq(s):
    """Fewest deletions so no two letters present have the same count."""
    deleted, cap = 0, float("inf")
    for f in sorted(Counter(s).values(), reverse=True):
        keep = max(0, min(f, cap))
        deleted += f - keep
        cap = keep - 1
    return deleted


def reconstruct_queue(people):
    """people = [(h, k)]: k people of height >= h stand in front. Rebuild the line."""
    queue = []
    for h, k in sorted(people, key=lambda p: (-p[0], p[1])):
        queue.insert(k, (h, k))
    return queue


# ------------------------------------------------------------------------ tests


def brute_candy(ratings):
    n = len(ratings)
    best = float("inf")
    for c in product(range(1, n + 1), repeat=n):
        if all(
            (ratings[i] <= ratings[i - 1] or c[i] > c[i - 1])
            and (ratings[i - 1] <= ratings[i] or c[i - 1] > c[i])
            for i in range(1, n)
        ):
            best = min(best, sum(c))
    return best if n else 0


def brute_unique_freq(s):
    freqs = list(Counter(s).values())
    best = float("inf")
    for kept in product(*[range(f + 1) for f in freqs]):
        nonzero = [k for k in kept if k]
        if len(nonzero) == len(set(nonzero)):
            best = min(best, sum(freqs) - sum(kept))
    return best if freqs else 0


def valid_queue(q):
    return all(sum(1 for h2, _ in q[:i] if h2 >= h) == k for i, (h, k) in enumerate(q))


def test_candy_examples():
    assert candy([1, 0, 2]) == 5
    assert candy([1, 2, 2]) == 4
    assert candy([]) == 0


def test_candy_matches_brute_force():
    random.seed(18)
    for _ in range(150):
        ratings = [random.randint(0, 3) for _ in range(random.randint(1, 5))]
        assert candy(ratings) == brute_candy(ratings)


def test_unique_freq_examples():
    assert min_deletions_unique_freq("aab") == 0
    assert min_deletions_unique_freq("aaabbbcc") == 2
    assert min_deletions_unique_freq("ceabaacb") == 2


def test_unique_freq_matches_brute_force():
    random.seed(19)
    for _ in range(300):
        s = "".join(random.choice("abcd") for _ in range(random.randint(0, 10)))
        assert min_deletions_unique_freq(s) == brute_unique_freq(s)


def test_queue_example():
    people = [(7, 0), (4, 4), (7, 1), (5, 0), (6, 1), (5, 2)]
    assert reconstruct_queue(people) == [(5, 0), (7, 0), (5, 2), (6, 1), (4, 4), (7, 1)]


def test_queue_matches_brute_force():
    random.seed(20)
    for _ in range(200):
        line = [random.randint(1, 4) for _ in range(random.randint(1, 6))]
        people = [(h, sum(1 for h2 in line[:i] if h2 >= h)) for i, h in enumerate(line)]
        random.shuffle(people)
        got = reconstruct_queue(people)
        assert valid_queue(got) and sorted(got) == sorted(people)
        assert any(list(p) == got for p in permutations(people) if valid_queue(p))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
