"""Grid DP — paths moving right/down, largest square, triangle, dungeon.

Signs: count paths or min path sum moving only right/down, obstacles, largest
       square of 1s, triangle minimum path, "minimum starting health so you
       never drop to 0".
Approach: the only-right/down rule makes the grid a DAG in row-major order, so
          dp[r][c] depends only on dp[r-1][c] (above) and dp[r][c-1] (left).
          A single row suffices: before the update dp[c] still holds the cell
          above, and dp[c-1] was already updated to the cell on the left.
            - obstacles: force the cell to 0 (count) or inf (cost)
            - largest square: 1 + min(top, left, top-left) if the cell is 1
            - a constraint on the *running* total (health must stay >= 1)
              depends on the future, not the past, so fill from the
              bottom-right backwards.
Complexity: O(R * C) time, O(C) space with a rolling row.
Gotchas:
  - Dungeon forwards does not work: the best path so far need not lead to the
    best continuation. Going backwards, "health needed from here" is a clean
    subproblem.
  - Largest square returns the *area*; the table holds side lengths.
  - With obstacles, the first row/column is not all 1s — a blocked cell cuts
    off everything after it. The rolling row handles this for free.

Run the tests at the bottom with:  python3 dynamic_programming/grid_dp.py
"""

import random
from itertools import combinations


INF = float("inf")


# ---------------------------------------------------------------- implementation


def unique_paths_obstacles(g):
    """Right/down paths from top-left to bottom-right; 1 marks a wall."""
    C = len(g[0])
    dp = [1] + [0] * (C - 1)
    for row in g:
        for c in range(C):
            if row[c] == 1:
                dp[c] = 0
            elif c:
                dp[c] += dp[c - 1]
    return dp[-1]


def min_path_sum(g):
    C = len(g[0])
    dp = [0] + [INF] * (C - 1)
    for row in g:
        dp[0] += row[0]
        for c in range(1, C):
            dp[c] = min(dp[c], dp[c - 1]) + row[c]
    return dp[-1]


def triangle_min_path(tri):
    """Top-to-bottom min sum, stepping to i or i + 1 on the next row.

    Bottom-up collapses the triangle into one row with no edge cases: each
    entry picks the better of its two children.
    """
    dp = list(tri[-1])
    for row in reversed(tri[:-1]):
        dp = [x + min(dp[i], dp[i + 1]) for i, x in enumerate(row)]
    return dp[0]


def largest_square(g):
    """Area of the largest all-'1' square. Cells may be '1'/'0' or 1/0."""
    R, C = len(g), len(g[0])
    dp = [[0] * (C + 1) for _ in range(R + 1)]  # padded: no bounds checks
    best = 0
    for r in range(R):
        for c in range(C):
            if str(g[r][c]) == "1":
                dp[r + 1][c + 1] = 1 + min(dp[r][c + 1], dp[r + 1][c], dp[r][c])
                best = max(best, dp[r + 1][c + 1])
    return best * best


def min_initial_health(g):
    """Least starting health to cross the dungeon with health >= 1 throughout.

    dp[r][c] = health needed on *entering* (r, c). From there you need enough
    to survive g[r][c] and still have the next cell's requirement, and never
    less than 1. The padded row/column is inf except the two cells beside the
    exit, which say "after the princess you need 1".
    """
    R, C = len(g), len(g[0])
    dp = [[INF] * (C + 1) for _ in range(R + 1)]
    dp[R][C - 1] = dp[R - 1][C] = 1
    for r in range(R - 1, -1, -1):
        for c in range(C - 1, -1, -1):
            dp[r][c] = max(1, min(dp[r + 1][c], dp[r][c + 1]) - g[r][c])
    return dp[0][0]


# ------------------------------------------------------------------------ tests


def monotone_paths(R, C):
    """Every right/down path as a list of cells: choose which steps go down."""
    steps = R + C - 2
    for downs in combinations(range(steps), R - 1):
        r = c = 0
        cells = [(0, 0)]
        for k in range(steps):
            if k in downs:
                r += 1
            else:
                c += 1
            cells.append((r, c))
        yield cells


def test_paths_classic():
    assert unique_paths_obstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2
    assert unique_paths_obstacles([[0, 1], [0, 0]]) == 1
    assert unique_paths_obstacles([[1]]) == 0
    assert unique_paths_obstacles([[0] * 7 for _ in range(3)]) == 28  # C(8, 2)
    assert min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
    assert min_path_sum([[5]]) == 5


def test_blocked_first_row_cuts_off_the_rest():
    # Initialising row 0 to all 1s would count a path through the wall.
    assert unique_paths_obstacles([[0, 1, 0]]) == 0
    assert unique_paths_obstacles([[0, 1, 0], [0, 0, 0]]) == 1


def test_paths_match_brute_force():
    random.seed(50)
    for _ in range(300):
        R, C = random.randint(1, 5), random.randint(1, 5)
        walls = [[int(random.random() < 0.25) for _ in range(C)] for _ in range(R)]
        costs = [[random.randint(0, 9) for _ in range(C)] for _ in range(R)]
        paths = list(monotone_paths(R, C))
        assert unique_paths_obstacles(walls) == sum(
            all(walls[r][c] == 0 for r, c in p) for p in paths
        )
        assert min_path_sum(costs) == min(sum(costs[r][c] for r, c in p) for p in paths)


def test_triangle():
    assert triangle_min_path([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]) == 11
    assert triangle_min_path([[-10]]) == -10
    random.seed(51)
    for _ in range(100):
        n = random.randint(1, 7)
        tri = [[random.randint(-5, 9) for _ in range(r + 1)] for r in range(n)]
        best = INF
        for mask in range(1 << (n - 1)):  # bit k: step right on row k + 1
            i, total = 0, tri[0][0]
            for k in range(n - 1):
                i += mask >> k & 1
                total += tri[k + 1][i]
            best = min(best, total)
        assert triangle_min_path(tri) == best


def test_largest_square():
    g = [list("10100"), list("10111"), list("11111"), list("10010")]
    assert largest_square(g) == 4
    assert largest_square([["0"]]) == 0
    assert largest_square([[1, 1], [1, 1]]) == 4
    random.seed(52)
    for _ in range(200):
        R, C = random.randint(1, 6), random.randint(1, 6)
        g = [[random.choice("0111") for _ in range(C)] for _ in range(R)]
        best = 0
        for r in range(R):
            for c in range(C):
                for k in range(1, min(R - r, C - c) + 1):
                    if all(g[r + i][c + j] == "1" for i in range(k) for j in range(k)):
                        best = max(best, k * k)
        assert largest_square(g) == best


def test_dungeon():
    assert min_initial_health([[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]) == 7
    assert min_initial_health([[0]]) == 1
    assert min_initial_health([[100]]) == 1
    random.seed(53)
    for _ in range(300):
        R, C = random.randint(1, 4), random.randint(1, 4)
        g = [[random.randint(-10, 10) for _ in range(C)] for _ in range(R)]
        best = INF
        for p in monotone_paths(R, C):
            run, low = 0, 0
            for r, c in p:
                run += g[r][c]
                low = min(low, run)
            best = min(best, 1 - low)  # health + low must stay >= 1
        assert min_initial_health(g) == best


def test_dungeon_forward_dp_is_the_trap():
    # Forward DP keeps, per cell, the arrival with the lowest starting health
    # needed (ties: most health left). It is not a valid subproblem: at (2, 1)
    # it prefers "need 1, health 1" over "need 2, health 6", then the -5 at
    # the exit costs 5 more. Going through the +5 needs only 2 in total.
    def forward(g):
        R, C = len(g), len(g[0])
        best = {}
        for r in range(R):
            for c in range(C):
                came = [best[p] for p in ((r - 1, c), (r, c - 1)) if p in best] or [(1, 1)]
                opts = []
                for need, hp in came:
                    hp += g[r][c]
                    if hp < 1:
                        need, hp = need + 1 - hp, 1
                    opts.append((need, -hp))
                need, neg = min(opts)
                best[r, c] = (need, -neg)
        return best[R - 1, C - 1][0]

    g = [[0, 0, 1], [-1, 0, -5], [5, 0, -5]]
    assert forward(g) == 6
    assert min_initial_health(g) == 2  # down, down, right, right


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
