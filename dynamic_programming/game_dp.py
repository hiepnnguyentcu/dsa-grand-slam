"""Game theory DP — minimax on score difference.

Signs: two players alternately take from the ends of a row or from piles, both
       play optimally, "can player 1 win", "what is the final score".
Approach: store the score *difference* from the point of view of whoever is
          to move: dp[l][r] = (my total - opponent's total) on a[l..r].
          Taking a[l] leaves the opponent to move on a[l+1..r], and their best
          difference counts against me:
              dp[l][r] = max(a[l] - dp[l+1][r], a[r] - dp[l][r-1])
          One table serves both players, with no "whose turn" flag.
Complexity: O(n^2) time; O(n) space since length L only reads length L - 1.
Gotchas:
  - Tracking two separate totals with a turn flag doubles the state and is
    easy to get wrong; the difference form is symmetric by construction.
  - Greedy "take the bigger end" loses: see the test.
  - The 1D roll overwrites dp[l] in place. That works because the right-hand
    side is evaluated first, while dp[l] still holds a[l..r-1].

Run the tests at the bottom with:  python3 dynamic_programming/game_dp.py
"""

import random
from functools import cache


# ---------------------------------------------------------------- implementation


def first_player_margin(a):
    """Optimal (first - second) score when players take from either end."""
    n = len(a)
    if not n:
        return 0
    dp = a[:]  # length 1: the mover takes the only element
    for length in range(2, n + 1):
        for l in range(n - length + 1):
            r = l + length - 1
            # dp[l + 1] is (l+1..r) from this round, dp[l] still (l..r-1)
            dp[l] = max(a[l] - dp[l + 1], a[r] - dp[l])
    return dp[0]


def first_player_wins(a):
    """Ties count as a win (the LeetCode "Predict the Winner" convention)."""
    return first_player_margin(a) >= 0


def stone_game_take_1_to_3(values):
    """Each turn take 1, 2 or 3 stones from the front; margin for the mover.

    Same difference trick on a suffix: dp[i] = max over k of
    (sum of the k stones taken) - dp[i + k].
    """
    n = len(values)
    dp = [0] * (n + 4)
    for i in range(n - 1, -1, -1):
        taken, best = 0, float("-inf")
        for k in range(1, 4):
            if i + k > n:
                break
            taken += values[i + k - 1]
            best = max(best, taken - dp[i + k])
        dp[i] = best
    return dp[0]


# ------------------------------------------------------------------------ tests


def brute_margin(a):
    """Explicit minimax with two totals and a turn flag — the slow, obvious way."""
    @cache
    def play(l, r, first_to_move):
        if l > r:
            return 0
        options = [(a[l], l + 1, r), (a[r], l, r - 1)]
        if first_to_move:
            return max(v + play(nl, nr, False) for v, nl, nr in options)
        return min(-v + play(nl, nr, True) for v, nl, nr in options)

    return play(0, len(a) - 1, True)


def test_classic():
    assert first_player_wins([1, 5, 233, 7])
    assert not first_player_wins([1, 5, 2])
    assert first_player_margin([5, 3, 4, 5]) == 1
    assert first_player_margin([7]) == 7
    assert first_player_margin([]) == 0
    assert stone_game_take_1_to_3([1, 2, 3, 7]) == -1   # Bob wins
    assert stone_game_take_1_to_3([1, 2, 3, -9]) == 15  # Alice takes 6, Bob is left the -9
    assert stone_game_take_1_to_3([1, 2, 3, 6]) == 0    # tie


def test_margin_matches_explicit_minimax():
    random.seed(90)
    for _ in range(300):
        a = [random.randint(0, 20) for _ in range(random.randint(0, 10))]
        assert first_player_margin(a) == brute_margin(a)


def test_even_length_first_player_never_loses():
    # With an even count, player 1 can force taking all even- or all
    # odd-indexed elements, whichever sum is larger.
    random.seed(91)
    for _ in range(200):
        a = [random.randint(0, 20) for _ in range(2 * random.randint(1, 6))]
        assert first_player_margin(a) >= abs(sum(a[0::2]) - sum(a[1::2])) >= 0


def test_greedy_bigger_end_is_the_trap():
    def greedy(a):
        a, sign, total = list(a), 1, 0
        while a:
            total += sign * (a.pop(0) if a[0] >= a[-1] else a.pop())
            sign = -sign
        return total

    a = [8, 15, 3, 7]
    assert greedy(a) == -3               # 8 + 7 vs 15 + 3: taking 8 exposes the 15
    assert first_player_margin(a) == 11  # take 7 first; 15 is yours next turn
    assert brute_margin(a) == 11


def test_take_1_to_3_matches_brute_force():
    @cache
    def brute(vals):
        if not vals:
            return 0
        return max(sum(vals[:k]) - brute(vals[k:]) for k in range(1, min(3, len(vals)) + 1))

    random.seed(92)
    for _ in range(200):
        vals = tuple(random.randint(-9, 9) for _ in range(random.randint(1, 12)))
        assert stone_game_take_1_to_3(list(vals)) == brute(vals)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
