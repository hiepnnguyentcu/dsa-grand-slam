"""Implicit neighbour generation — the graph is never built, only walked.

Signs: nodes are strings, tuples or board states; word ladders, gene mutations,
       lock combinations, puzzles. The "graph" would have astronomically many
       edges if you wrote it down.
Approach: replace the adjacency lookup with a function that *computes* the
          neighbours of a state by applying every allowed transformation. BFS
          does not care where its neighbours come from.
Complexity: whatever neighbour generation costs, times the states reached. That
            cost is usually the thing worth optimising, not the BFS itself.
Gotchas: generating a neighbour is not the same as it being legal — filter
         against the allowed set. And the cost of generation is easy to get
         wrong: for word ladders the naive "try 26 letters in every position"
         is O(26 x L) per word, while wildcard buckets are O(L) amortised.

Run the tests at the bottom with:  python3 graphs/implicit_neighbors.py
"""

from collections import defaultdict, deque


# ---------------------------------------------------------------- implementation


def wildcard_buckets(words):
    """{'h*t': ['hot', 'hat'], ...} — words grouped by every one-hole pattern.

    Two words are one edit apart iff they share a bucket. Building this costs
    O(N x L) once and turns neighbour generation into a dict lookup, instead of
    testing 26 substitutions per position against the dictionary.
    """
    buckets = defaultdict(list)
    for w in words:
        for i in range(len(w)):
            buckets[w[:i] + "*" + w[i + 1:]].append(w)
    return buckets


def word_ladder(begin, end, words):
    """Length of the shortest transformation sequence, counting both ends.

    Returns 0 when there is no such sequence — 0 is unambiguous here because a
    real answer always counts at least the start word.

    The `buckets[key] = []` clear is what keeps this linear: once a bucket has
    been expanded, every word in it is queued, so anyone who reaches that
    pattern later has nothing left to learn from it.
    """
    words = set(words)
    if end not in words:
        return 0

    L = len(begin)
    buckets = wildcard_buckets(words)
    q, seen = deque([(begin, 1)]), {begin}
    while q:
        w, d = q.popleft()
        if w == end:
            return d
        for i in range(L):
            key = w[:i] + "*" + w[i + 1:]
            for nxt in buckets.get(key, ()):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, d + 1))
            buckets[key] = []  # each pattern is only ever useful once
    return 0


def word_ladder_naive(begin, end, words):
    """Same answer, generating neighbours by brute substitution.

    Kept for contrast: this is the obvious way, and it is a factor of ~26
    slower per step. Worth writing first and optimising only if asked.
    """
    words = set(words)
    if end not in words:
        return 0

    from string import ascii_lowercase

    q, seen = deque([(begin, 1)]), {begin}
    while q:
        w, d = q.popleft()
        if w == end:
            return d
        for i in range(len(w)):
            for ch in ascii_lowercase:
                if ch == w[i]:
                    continue
                cand = w[:i] + ch + w[i + 1:]
                if cand in words and cand not in seen:
                    seen.add(cand)
                    q.append((cand, d + 1))
    return 0


def min_mutation(start, end, bank):
    """Fewest single-character mutations from start to end, or -1.

    Unlike the word ladder this counts *steps*, so 0 is a legitimate answer
    (start == end) and -1 has to mean "impossible".
    """
    bank = set(bank)
    if end not in bank:
        return -1

    q, seen = deque([(start, 0)]), {start}
    while q:
        gene, d = q.popleft()
        if gene == end:
            return d
        for i in range(len(gene)):
            for ch in "ACGT":
                if ch == gene[i]:
                    continue
                cand = gene[:i] + ch + gene[i + 1:]
                if cand in bank and cand not in seen:
                    seen.add(cand)
                    q.append((cand, d + 1))
    return -1


def transform_neighbors(state, alphabet):
    """Every state one single-character substitution away. The generic shape."""
    for i, cur in enumerate(state):
        for ch in alphabet:
            if ch != cur:
                yield state[:i] + ch + state[i + 1:]


# ------------------------------------------------------------------------ tests


WORDS = ["hot", "dot", "dog", "lot", "log", "cog"]


def test_word_ladder():
    # hit -> hot -> dot -> dog -> cog
    assert word_ladder("hit", "cog", WORDS) == 5


def test_word_ladder_unreachable():
    assert word_ladder("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
    assert word_ladder("hit", "cog", []) == 0


def test_word_ladder_trivial():
    assert word_ladder("a", "c", ["a", "b", "c"]) == 2   # a -> c directly
    assert word_ladder("hot", "hot", ["hot"]) == 1       # already there


def test_both_ladder_implementations_agree():
    import random
    from string import ascii_lowercase

    random.seed(29)
    for _ in range(40):
        vocab = ["".join(random.choice("abc") for _ in range(3)) for _ in range(12)]
        begin = "".join(random.choice("abc") for _ in range(3))
        end = random.choice(vocab)
        assert word_ladder(begin, end, vocab) == word_ladder_naive(begin, end, vocab)


def test_buckets_group_one_edit_neighbours():
    b = wildcard_buckets(["hot", "dot", "dog"])
    assert sorted(b["*ot"]) == ["dot", "hot"]   # differ only in position 0
    assert sorted(b["do*"]) == ["dog", "dot"]
    assert b["h*t"] == ["hot"]                   # nothing else shares this hole


def test_gene_mutation():
    assert min_mutation("AACCGGTT", "AACCGGTA", ["AACCGGTA"]) == 1
    assert min_mutation(
        "AACCGGTT", "AAACGGTA", ["AACCGGTA", "AACCGCTA", "AAACGGTA"]
    ) == 2


def test_gene_mutation_unreachable():
    assert min_mutation("AACCGGTT", "AACCGGTA", []) == -1
    assert min_mutation("AAAAACCC", "AACCCCCC", ["AAAACCCC", "AAACCCCC"]) == -1


def test_gene_mutation_zero_steps_is_a_real_answer():
    assert min_mutation("AACCGGTT", "AACCGGTT", ["AACCGGTT"]) == 0


def test_transform_neighbors_count():
    # length 3, alphabet of 4 -> 3 positions x 3 other letters
    assert len(list(transform_neighbors("aaa", "abcd"))) == 9
    assert set(transform_neighbors("ab", "ab")) == {"aa", "bb"}


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
