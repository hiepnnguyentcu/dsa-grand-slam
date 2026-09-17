"""Randomized algorithms — shuffle, reservoir sampling, weighted pick, rejection.

Signs: "return a uniformly random ...", shuffle an array, random node of a
       linked list / stream of unknown length, pick index i with probability
       w[i] / sum(w), build rand10() from rand7().
Approach:
  - Fisher-Yates: for i from the end, swap a[i] with a[j], j uniform in
    [0, i]. The choices multiply to n!, one per permutation.
  - Reservoir: keep the i-th item (1-indexed) with probability 1/i. By
    induction every item seen so far is held with probability 1/i. The k-item
    version replaces a random slot with probability k/i.
  - Weighted pick: prefix sums, draw x uniform in [0, total), and binary
    search for the first prefix > x.
  - Rejection sampling: combine calls into a larger uniform range, keep the
    largest multiple of the target size, and retry on the rest.
Complexity: shuffle and reservoir O(n); weighted pick O(n) build, O(log n) per
            pick; rand10 O(1) expected (49/40 rounds of two rand7 calls).
Gotchas:
  - Shuffle "swap with any j in [0, n)" looks fine and is biased: it has n^n
    equally likely outcomes, which n! does not divide.
  - Weighted pick needs bisect_right; bisect_left returns zero-weight items
    when x lands exactly on a prefix boundary.
  - Rejection: (rand7() * rand7()) is not uniform; (rand7() - 1) * 7 + rand7()
    is. Never "fold" the rejected values back with %.
  - Every function takes an `rng` so tests can be deterministic.

Run the tests at the bottom with:  python3 math_algorithms/randomized.py
"""

import random
from bisect import bisect_right


# ---------------------------------------------------------------- implementation


def shuffle(a, rng=random):
    """Fisher-Yates, in place."""
    for i in range(len(a) - 1, 0, -1):
        j = rng.randrange(i + 1)  # j in [0, i]: may swap with itself
        a[i], a[j] = a[j], a[i]


def naive_shuffle(a, rng=random):
    """The biased version, kept for the test that proves it biased."""
    n = len(a)
    for i in range(n):
        j = rng.randrange(n)
        a[i], a[j] = a[j], a[i]


def reservoir(stream, rng=random):
    """One uniformly random item from an iterable of unknown length (None if empty)."""
    chosen = None
    for i, x in enumerate(stream, 1):
        if rng.randrange(i) == 0:  # probability 1/i
            chosen = x
    return chosen


def reservoir_k(stream, k, rng=random):
    """k items, every k-subset equally likely (fewer if the stream is short)."""
    res = []
    for i, x in enumerate(stream):
        if i < k:
            res.append(x)
        else:
            j = rng.randrange(i + 1)
            if j < k:  # probability k / (i + 1)
                res[j] = x
    return res


class WeightedPicker:
    """Pick index i with probability w[i] / sum(w). Weights >= 0, sum > 0."""

    def __init__(self, w, rng=random):
        self.pre, total = [], 0
        for x in w:
            total += x
            self.pre.append(total)
        self.rng = rng
        self.exact = all(isinstance(x, int) for x in w)

    def pick(self):
        total = self.pre[-1]
        if self.exact:
            x = self.rng.randrange(total)  # integer weights: no rounding at all
        else:
            x = self.rng.random() * total  # < total even after float rounding
        return bisect_right(self.pre, x)


def rand10_from_rand7(rand7):
    while True:
        v = (rand7() - 1) * 7 + rand7()  # uniform on 1..49
        if v <= 40:  # 40 = largest multiple of 10 that fits
            return (v - 1) % 10 + 1


# ------------------------------------------------------------------------ tests


class Scripted:
    """A fake rng that returns pre-chosen values, so every outcome can be enumerated."""

    def __init__(self, values):
        self.values = list(values)
        self.pos = 0

    def randrange(self, n):
        v = self.values[self.pos]
        self.pos += 1
        assert 0 <= v < n, (v, n)
        return v

    def done(self):
        return self.pos == len(self.values)


def _chi_square(counts, expected):
    return sum((c - e) ** 2 / e for c, e in zip(counts, expected))


def _chi_square_ok(counts, expected):
    # mean of chi-square is df, sd is sqrt(2 df); 8 sd is far beyond chance,
    # and the seed makes the run deterministic anyway.
    df = len(counts) - 1
    return _chi_square(counts, expected) < df + 8 * (2 * df) ** 0.5


def test_shuffle_every_choice_sequence_gives_each_permutation_once():
    from collections import Counter
    from itertools import product

    for n in range(0, 6):
        choices = [range(i + 1) for i in range(n - 1, 0, -1)]  # order the loop asks
        seen = Counter()
        for seq in product(*choices):
            a = list(range(n))
            rng = Scripted(seq)
            shuffle(a, rng)
            assert rng.done()
            seen[tuple(a)] += 1
        assert len(seen) == [1, 1, 2, 6, 24, 120][n]
        assert set(seen.values()) == {1}


def test_naive_shuffle_is_provably_biased():
    from collections import Counter
    from itertools import product

    n = 3
    seen = Counter()
    for seq in product(range(n), repeat=n):  # 27 equally likely runs
        a = list(range(n))
        naive_shuffle(a, Scripted(seq))
        seen[tuple(a)] += 1
    assert len(seen) == 6
    assert sorted(seen.values()) == [4, 4, 4, 5, 5, 5]  # 27 cannot split evenly into 6


def test_shuffle_is_a_permutation_and_roughly_uniform():
    from collections import Counter
    from itertools import permutations

    rng = random.Random(39)
    a = list(range(50))
    shuffle(a, rng)
    assert sorted(a) == list(range(50))

    trials = 60_000
    counts = Counter()
    for _ in range(trials):
        b = [0, 1, 2, 3]
        shuffle(b, rng)
        counts[tuple(b)] += 1
    perms = list(permutations(range(4)))
    assert _chi_square_ok([counts[p] for p in perms], [trials / 24] * 24)


def test_shuffle_trivial_inputs():
    for a in ([], [7]):
        b = list(a)
        shuffle(b, random.Random(0))
        assert b == a


def test_reservoir_every_choice_sequence_is_fair():
    from collections import Counter
    from itertools import product

    for n in range(1, 7):
        seen = Counter()
        for seq in product(*[range(i) for i in range(1, n + 1)]):  # n! runs
            rng = Scripted(seq)
            seen[reservoir(range(n), rng)] += 1
            assert rng.done()
        assert len(seen) == n and len(set(seen.values())) == 1


def test_reservoir_empty_and_single():
    assert reservoir([], random.Random(0)) is None
    assert reservoir(iter(["only"]), random.Random(0)) == "only"


def test_reservoir_roughly_uniform_on_a_generator():
    rng = random.Random(40)
    n, trials = 10, 50_000
    counts = [0] * n
    for _ in range(trials):
        counts[reservoir((x for x in range(n)), rng)] += 1
    assert _chi_square_ok(counts, [trials / n] * n)


def test_reservoir_k_every_subset_equally_often():
    from collections import Counter
    from itertools import product
    from math import comb, factorial

    for n in range(0, 7):
        for k in range(0, n + 2):
            seen = Counter()
            ranges = [range(i + 1) for i in range(k, n)]
            for seq in product(*ranges):
                rng = Scripted(seq)
                res = reservoir_k(range(n), k, rng)
                assert rng.done()
                assert len(res) == min(k, n) and len(set(res)) == len(res)
                seen[frozenset(res)] += 1
            if k <= n:
                # n! / k! runs spread over C(n, k) subsets: (n - k)! each
                assert len(seen) == comb(n, k)
                assert set(seen.values()) == {factorial(n - k)}
            else:
                assert list(seen) == [frozenset(range(n))]


def test_weighted_pick_exact_counts_over_every_draw():
    for w in ([1], [1, 3], [0, 2, 0, 5, 1], [4, 0], [0, 0, 7], [3, 3, 3]):
        total = sum(w)
        counts = [0] * len(w)
        for x in range(total):  # every value randrange can return, once
            picker = WeightedPicker(w, Scripted([x]))
            counts[picker.pick()] += 1
        assert counts == w  # zero-weight entries are never returned


def test_weighted_pick_bisect_left_would_be_wrong():
    from bisect import bisect_left

    pre = [0, 2]  # weights [0, 2]
    assert bisect_right(pre, 0) == 1  # correct: skips the zero-weight index
    assert bisect_left(pre, 0) == 0  # wrong: returns an impossible index


def test_weighted_pick_float_weights_roughly_proportional():
    w = [0.5, 0.0, 2.5, 1.0, 6.0]
    picker = WeightedPicker(w, random.Random(41))
    trials = 100_000
    counts = [0] * len(w)
    for _ in range(trials):
        counts[picker.pick()] += 1
    assert counts[1] == 0
    nz = [i for i, x in enumerate(w) if x]
    assert _chi_square_ok([counts[i] for i in nz], [trials * w[i] / sum(w) for i in nz])


def test_weighted_pick_float_top_of_range():
    class Top:
        def random(self):
            return 1 - 2**-53  # the largest value random() can return

    for w in ([0.1, 0.2], [0.3, 0.0, 0.7], [1e-300, 1e300], [3.0]):
        i = WeightedPicker(w, Top()).pick()
        assert i < len(w) and w[i] > 0


def test_rand10_exact_distribution():
    from collections import Counter

    seen = Counter()
    for a in range(1, 8):
        for b in range(1, 8):
            v = (a - 1) * 7 + b
            if v <= 40:
                calls = iter([a, b])
                seen[rand10_from_rand7(lambda: next(calls))] += 1
            else:
                calls = iter([a, b, 1, 1])  # rejected, then (1, 1) -> 1
                assert rand10_from_rand7(lambda: next(calls)) == 1
                assert next(calls, None) is None
    assert seen == {d: 4 for d in range(1, 11)}


def test_rand10_roughly_uniform_and_cheap():
    rng = random.Random(42)
    calls = 0

    def rand7():
        nonlocal calls
        calls += 1
        return rng.randint(1, 7)

    trials = 50_000
    counts = [0] * 10
    for _ in range(trials):
        counts[rand10_from_rand7(rand7) - 1] += 1
    assert _chi_square_ok(counts, [trials / 10] * 10)
    # expected 2 * 49 / 40 = 2.45 calls per number
    assert 2.35 < calls / trials < 2.55


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
