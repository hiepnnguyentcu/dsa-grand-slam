"""Multi-pointer sequence generation — ugly / super-ugly numbers.

Signs: "the n-th number whose only prime factors are ...", merge the multiples
       of several bases into one sorted, duplicate-free stream.
Approach: every smooth number > 1 is a smaller smooth number times one of the
          factors. So keep the answer list and one pointer per factor into it:
          factor i's next candidate is res[ptr[i]] * f_i. Append the smallest
          candidate and advance *every* pointer that produced it — that is what
          removes duplicates like 6 = 2*3 = 3*2.
Complexity: O(n * k) time for k factors, O(n) space. A heap version is
            O(n log k) and pays off only for large k.
Gotchas:
  - Advance all tied pointers, not just the first; `elif` produces duplicates.
  - The factors must be distinct and > 1, or the sequence stalls.
  - 1 is the first term by convention (empty product).

Run the tests at the bottom with:  python3 math_algorithms/smooth_numbers.py
"""

import heapq


# ---------------------------------------------------------------- implementation


def smooth_sequence(n, factors=(2, 3, 5)):
    """The first n smooth numbers, ascending, starting from 1."""
    if n <= 0:
        return []
    res, ptr = [1], [0] * len(factors)
    for _ in range(n - 1):
        cands = [res[ptr[i]] * f for i, f in enumerate(factors)]
        nxt = min(cands)
        res.append(nxt)
        for i, c in enumerate(cands):
            if c == nxt:
                ptr[i] += 1
    return res


def nth_smooth(n, factors=(2, 3, 5)):
    """n-th (1-indexed) number whose prime factors all lie in `factors`."""
    return smooth_sequence(n, factors)[-1]


def nth_smooth_heap(n, factors=(2, 3, 5)):
    """Same answer via a min-heap of (value, factor index, list index).

    Each factor contributes one live entry. Popping the smallest and pushing
    that factor's next candidate is the k-way merge the pointer loop does by
    hand; ties are skipped by only appending strictly larger values.
    """
    res = [1]
    heap = [(f, i, 0) for i, f in enumerate(factors)]
    heapq.heapify(heap)
    while len(res) < n:
        val, i, j = heapq.heappop(heap)
        if val > res[-1]:
            res.append(val)
        heapq.heappush(heap, (res[j + 1] * factors[i], i, j + 1))
    return res[n - 1]


# ------------------------------------------------------------------------ tests


def _smooth_brute(limit, factors):
    out = []
    for x in range(1, limit + 1):
        y = x
        for f in factors:
            while y % f == 0:
                y //= f
        if y == 1:
            out.append(x)
    return out


def test_ugly_numbers_against_brute_force():
    brute = _smooth_brute(20_000, (2, 3, 5))
    seq = smooth_sequence(len(brute))
    assert seq == brute
    assert seq[:10] == [1, 2, 3, 4, 5, 6, 8, 9, 10, 12]


def test_no_duplicates_and_strictly_increasing():
    seq = smooth_sequence(3000, (2, 3, 5, 7))
    assert all(a < b for a, b in zip(seq, seq[1:]))


def test_super_ugly_against_brute_force():
    import random

    rng = random.Random(14)
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    for _ in range(30):
        factors = tuple(sorted(rng.sample(small_primes, rng.randint(1, 5))))
        brute = _smooth_brute(5000, factors)
        assert smooth_sequence(len(brute), factors) == brute


def test_heap_version_agrees():
    for factors in [(2, 3, 5), (2, 7, 13, 19), (3,), (5, 2)]:
        seq = smooth_sequence(500, factors)
        for n in (1, 2, 3, 50, 499, 500):
            assert nth_smooth(n, factors) == seq[n - 1]
            assert nth_smooth_heap(n, factors) == seq[n - 1]


def test_known_values_and_edges():
    assert nth_smooth(1) == 1
    assert nth_smooth(10) == 12
    assert nth_smooth(1690) == 2_123_366_400  # LeetCode's largest ugly-number test
    assert smooth_sequence(0) == []
    assert smooth_sequence(5, (2,)) == [1, 2, 4, 8, 16]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
