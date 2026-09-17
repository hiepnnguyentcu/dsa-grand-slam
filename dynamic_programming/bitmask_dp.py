"""Bitmask DP — travelling salesman, smallest team, assignment.

Signs: n <= 20 (often <= 16), choose or visit a subset, assignment problems,
       travelling salesman, "cover all skills with the fewest people".
Approach: the chosen set is an integer mask; bit i set means element i is in.
          State is dp[mask] or dp[mask][last]. Transition by adding one
          element not yet in the mask. Plain increasing order over masks is a
          valid topological order, because adding a bit always makes the
          number larger.
Complexity: O(2^n * n) for dp[mask]; O(2^n * n^2) for dp[mask][last].
Gotchas:
  - Precedence: in Python, arithmetic binds tighter than shifts, and shifts
    tighter than &, so `1 << n - 1` is 1 << (n - 1) and `x + 1 << 2` is
    (x + 1) << 2. (Unlike C, `mask & 1 == 0` is fine here.) Bracket anyway.
  - ~mask is negative (-mask - 1). The complement within n bits is FULL ^ mask.
  - TSP start: fix city 0 in the start mask (dp[1][0] = 0), or every rotation
    of the same tour is counted separately — harmless for min, wrong for
    counting.
  - dp[mask] as a *list of people* (team cover) is fine for n people and 16
    skills; store a parent pointer instead if lists get long.

Run the tests at the bottom with:  python3 dynamic_programming/bitmask_dp.py
"""

import random
from itertools import combinations, permutations


INF = float("inf")


# ---------------------------------------------------------------- implementation


def tsp(dist):
    """Shortest tour visiting every city once and returning to city 0."""
    n = len(dist)
    FULL = 1 << n
    dp = [[INF] * n for _ in range(FULL)]  # dp[mask][u]: visited mask, standing at u
    dp[1][0] = 0
    for mask in range(1, FULL, 2):  # every useful mask contains city 0
        for u in range(n):
            if dp[mask][u] == INF:
                continue
            for v in range(n):
                if mask >> v & 1:
                    continue
                nm = mask | 1 << v
                dp[nm][v] = min(dp[nm][v], dp[mask][u] + dist[u][v])
    return min(dp[FULL - 1][u] + dist[u][0] for u in range(n))


def min_team_cover(req_skills, people):
    """Smallest list of people indices whose skills cover req_skills.

    dp[mask] = smallest team reaching exactly that skill mask. The items() list
    is a snapshot, so each person is added at most once per team — a 0/1
    knapsack over people with masks as the "capacity".
    """
    idx = {s: i for i, s in enumerate(req_skills)}
    FULL = (1 << len(req_skills)) - 1
    dp = {0: []}
    for p, skills in enumerate(people):
        pm = 0
        for s in skills:
            if s in idx:
                pm |= 1 << idx[s]
        for mask, team in list(dp.items()):
            nm = mask | pm
            if nm not in dp or len(dp[nm]) > len(team) + 1:
                dp[nm] = team + [p]
    return dp.get(FULL)


def min_assignment_cost(cost):
    """Assign n workers to n jobs one-to-one, minimising total cost.

    dp[mask] = best cost when the jobs in mask are taken by the first
    popcount(mask) workers — the worker index is implied, so no second
    dimension is needed.
    """
    n = len(cost)
    dp = [INF] * (1 << n)
    dp[0] = 0
    for mask in range(1 << n):
        if dp[mask] == INF:
            continue
        w = mask.bit_count()  # next worker to place
        if w == n:
            continue
        for j in range(n):
            if not mask >> j & 1:
                nm = mask | 1 << j
                dp[nm] = min(dp[nm], dp[mask] + cost[w][j])
    return dp[-1]


def iter_submasks(mask):
    """Every submask of mask, largest first, ending with 0.

    `sub = (sub - 1) & mask` clears the lowest set bit and refills everything
    below it that mask allows — this is what makes the "sum over all submasks
    of all masks" loop O(3^n) instead of O(4^n).
    """
    sub = mask
    while True:
        yield sub
        if sub == 0:
            return
        sub = (sub - 1) & mask


# ------------------------------------------------------------------------ tests


def brute_tsp(dist):
    n = len(dist)
    best = INF
    for perm in permutations(range(1, n)):
        tour = (0,) + perm + (0,)
        best = min(best, sum(dist[a][b] for a, b in zip(tour, tour[1:])))
    return best


def test_tsp_classic():
    dist = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
    assert tsp(dist) == 80
    assert tsp([[0]]) == 0
    assert tsp([[0, 3], [4, 0]]) == 7


def test_tsp_matches_brute_force():
    random.seed(110)
    for _ in range(60):
        n = random.randint(1, 7)
        dist = [[0 if i == j else random.randint(1, 30) for j in range(n)] for i in range(n)]
        assert tsp(dist) == brute_tsp(dist)  # asymmetric distances too


def test_team_cover():
    team = min_team_cover(["java", "nodejs", "reactjs"], [["java"], ["nodejs"], ["nodejs", "reactjs"]])
    assert sorted(team) == [0, 2]
    random.seed(111)
    for _ in range(200):
        k = random.randint(1, 5)
        skills = [f"s{i}" for i in range(k)]
        people = [random.sample(skills + ["junk"], random.randint(0, k)) for _ in range(random.randint(1, 7))]
        team = min_team_cover(skills, people)
        best = None
        for size in range(len(people) + 1):
            for c in combinations(range(len(people)), size):
                if set(skills) <= {s for p in c for s in people[p]}:
                    best = size
                    break
            if best is not None:
                break
        if best is None:
            assert team is None
        else:
            assert len(team) == best
            assert set(skills) <= {s for p in team for s in people[p]}


def test_assignment_matches_brute_force():
    random.seed(112)
    for _ in range(100):
        n = random.randint(0, 7)
        cost = [[random.randint(0, 20) for _ in range(n)] for _ in range(n)]
        best = min(sum(cost[w][j] for w, j in enumerate(p)) for p in permutations(range(n)))
        assert min_assignment_cost(cost) == best


def test_submasks():
    assert list(iter_submasks(0b101)) == [0b101, 0b100, 0b001, 0]
    for mask in range(64):
        subs = list(iter_submasks(mask))
        assert sorted(subs) == [s for s in range(64) if s & mask == s]
    # total work over all masks of n bits is 3^n
    n = 8
    assert sum(len(list(iter_submasks(m))) for m in range(1 << n)) == 3 ** n


def test_bit_operator_traps():
    n, x = 4, 3
    assert 1 << n - 1 == 8          # 1 << (n - 1), not (1 << n) - 1 == 15
    assert (1 << n) - 1 == 0b1111
    assert x + 1 << 2 == 16         # (x + 1) << 2
    mask, FULL = 0b0101, 0b1111
    assert ~mask == -6              # not the complement you wanted
    assert FULL ^ mask == 0b1010
    assert (0b10 & 1 == 0) is True  # Python: & before ==, unlike C


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
