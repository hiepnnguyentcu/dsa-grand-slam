"""Queue simulation — model a line of people, a round, or a deck with a deque.

Signs: "people stand in a line and go to the back", "each round, in order",
       "every k-th person is removed", "reveal the top card, move the next one
       to the bottom".
Approach: put the actors in a deque and replay the rules: popleft to act,
          append to go round again. Often the simulation is enough; sometimes
          it points at a closed form (tickets, Josephus) worth knowing.
Complexity: O(total moves). Tickets O(sum) simulated vs O(n) closed form;
            Josephus O(n k) simulated vs O(n) recurrence.
Gotchas:
  - Rounds: re-enqueue with index + n so "who acts first" stays comparable
    across rounds (Dota2 senate).
  - Reverse simulation: when you know the output order and need the input,
    simulate on *positions* rather than values (reveal cards).
  - Josephus recurrence is 0-indexed: f(1) = 0, f(n) = (f(n-1) + k) % n.

Run the tests at the bottom with:  python3 stacks_heaps/queue_simulation.py
"""

from collections import deque


# ---------------------------------------------------------------- implementation


def time_to_buy(tickets, k):
    """LC 2073. Seconds until person k is done; one ticket per trip to the front.

    People ahead of k (and k) buy at most tickets[k]; people behind buy at
    most tickets[k] - 1, because k finishes before their next turn.
    """
    t = tickets[k]
    return sum(min(x, t) if i <= k else min(x, t - 1) for i, x in enumerate(tickets))


def time_to_buy_sim(tickets, k):
    q, seconds = deque(enumerate(tickets)), 0
    while True:
        i, left = q.popleft()
        seconds += 1
        if left == 1:
            if i == k:
                return seconds
        else:
            q.append((i, left - 1))


def predict_party_victory(senate):
    """LC 649. Each senator bans the next opposing senator to act. 'R' or 'D'.

    Two queues of turn indices. The earlier of the two fronts bans the other
    and rejoins next round at index + n.
    """
    n = len(senate)
    r = deque(i for i, s in enumerate(senate) if s == "R")
    d = deque(i for i, s in enumerate(senate) if s == "D")
    while r and d:
        a, b = r.popleft(), d.popleft()
        if a < b:
            r.append(a + n)
        else:
            d.append(b + n)
    return "Radiant" if r else "Dire"


def predict_party_victory_sim(senate):
    """Literal rounds: walk the circle, each live senator bans the next opponent."""
    n, banned = len(senate), [False] * len(senate)
    while True:
        for i in range(n):
            if banned[i]:
                continue
            for step in range(1, n):
                j = (i + step) % n
                if not banned[j] and senate[j] != senate[i]:
                    banned[j] = True
                    break
            else:  # no opponent left
                return "Radiant" if senate[i] == "R" else "Dire"


def deck_revealed_increasing(deck):
    """LC 950. Order the deck so reveal-top, move-next-to-bottom gives sorted output.

    Simulate the process on positions 0..n-1: the k-th revealed position gets
    the k-th smallest card.
    """
    n = len(deck)
    pos, out = deque(range(n)), [0] * n
    for card in sorted(deck):
        out[pos.popleft()] = card
        if pos:
            pos.append(pos.popleft())
    return out


def reveal(deck):
    """Run the reveal process forwards — the check for deck_revealed_increasing."""
    q, out = deque(deck), []
    while q:
        out.append(q.popleft())
        if q:
            q.append(q.popleft())
    return out


def find_the_winner(n, k):
    """LC 1823 / Josephus. Friends 1..n in a circle, every k-th leaves. O(n)."""
    w = 0
    for size in range(2, n + 1):
        w = (w + k) % size
    return w + 1


def find_the_winner_sim(n, k):
    q = deque(range(1, n + 1))
    while len(q) > 1:
        q.rotate(-(k - 1))  # the k-1 people before the loser go to the back
        q.popleft()
    return q[0]


# ------------------------------------------------------------------------ tests


def test_tickets_example():
    assert time_to_buy([2, 3, 2], 2) == 6
    assert time_to_buy([5, 1, 1, 1], 0) == 8


def test_tickets_formula_matches_simulation():
    import random

    rng = random.Random(31)
    for _ in range(300):
        t = [rng.randint(1, 6) for _ in range(rng.randint(1, 10))]
        k = rng.randrange(len(t))
        assert time_to_buy(t, k) == time_to_buy_sim(t, k)


def test_senate_example():
    assert predict_party_victory("RD") == "Radiant"
    assert predict_party_victory("RDD") == "Dire"


def test_senate_matches_literal_rounds():
    import random

    rng = random.Random(32)
    for _ in range(500):
        s = "".join(rng.choice("RD") for _ in range(rng.randint(1, 12)))
        assert predict_party_victory(s) == predict_party_victory_sim(s)


def test_reveal_cards_example():
    assert deck_revealed_increasing([17, 13, 11, 2, 3, 5, 7]) == [2, 13, 3, 11, 5, 17, 7]


def test_reveal_cards_round_trips():
    import random

    rng = random.Random(33)
    for _ in range(200):
        deck = rng.sample(range(100), rng.randint(1, 15))
        assert reveal(deck_revealed_increasing(deck)) == sorted(deck)


def test_josephus_example():
    assert find_the_winner(5, 2) == 3
    assert find_the_winner(6, 5) == 1
    assert find_the_winner(1, 7) == 1


def test_josephus_recurrence_matches_simulation():
    for n in range(1, 25):
        for k in range(1, 10):
            assert find_the_winner(n, k) == find_the_winner_sim(n, k)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
