"""Direction-array simulation — robots, snakes and walkers on a plane or grid.

Signs: "G / L / R instructions", "turn left 90 degrees", "obstacles block the
       robot", "does the robot stay in a circle", "snake eats food and grows",
       "simulate step by step and report the position / distance".
Approach: state = (position, direction index). DIRS = [N, E, S, W] in
  clockwise order, so turn right = (d + 1) % 4, turn left = (d + 3) % 4.
  Move one cell at a time when anything can block mid-move (obstacles, the
  snake's own body); hash the blockers in a set for O(1) checks.
  Bounded robot: after one pass of the instructions the robot is either back
  at the origin, or facing a new direction - then 2 or 4 passes bring it back.
  Only "not at origin and still facing north" drifts away forever.
  Snake: deque of body cells (head at the left) + set of the same cells.
Complexity: O(total steps) with set lookups. Bounded robot: O(len(s)).
            Snake: O(1) per move.
Gotchas:
  - (x, y) with north = +y (robot problems) versus (r, c) with up = -r (grid
    problems). Write DIRS for the problem's axes and never mix them.
  - Obstacle checks per unit step, not per command: "move 5" can stop at 2.
  - Snake: pop the tail before the self-collision check, so moving into the
    cell the tail is leaving is legal. Eating food skips the pop.
  - Walker on an R x C grid with repeating moves: if the state (pos, dir)
    repeats, it loops - cycle-detect instead of simulating 10^9 steps.

Run the tests at the bottom with:  python3 matrix_simulation/robot_simulation.py
"""

import random
from collections import deque


# ---------------------------------------------------------------- implementation

DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # (dx, dy): N, E, S, W — clockwise


def walk(instructions, x=0, y=0, d=0):
    """Apply 'G' / 'L' / 'R' once. Returns the final (x, y, d)."""
    for ch in instructions:
        if ch == "G":
            x, y = x + DIRS[d][0], y + DIRS[d][1]
        elif ch == "R":
            d = (d + 1) % 4
        else:
            d = (d + 3) % 4
    return x, y, d


def is_robot_bounded(instructions):
    """Robot Bounded In Circle: repeating forever stays in a bounded region?"""
    x, y, d = walk(instructions)
    return (x, y) == (0, 0) or d != 0


def robot_sim(commands, obstacles):
    """Walking Robot Simulation: -2 = left, -1 = right, k > 0 = forward k unit
    steps, each stopped by an obstacle. Returns the max squared distance."""
    blocked = set(map(tuple, obstacles))
    x = y = d = best = 0
    for cmd in commands:
        if cmd == -1:
            d = (d + 1) % 4
        elif cmd == -2:
            d = (d + 3) % 4
        else:
            dx, dy = DIRS[d]
            for _ in range(cmd):
                if (x + dx, y + dy) in blocked:
                    break
                x, y = x + dx, y + dy
            best = max(best, x * x + y * y)
    return best


class SnakeGame:
    """Design Snake Game on a height x width grid; moves 'U', 'D', 'L', 'R'."""

    MOVES = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}  # (dr, dc)

    def __init__(self, width, height, food):
        self.W, self.H = width, height
        self.food = deque(map(tuple, food))
        self.body = deque([(0, 0)])  # head at body[0]
        self.cells = {(0, 0)}
        self.score = 0

    def move(self, direction):
        """New score, or -1 once the snake hits a wall or itself."""
        dr, dc = self.MOVES[direction]
        r, c = self.body[0][0] + dr, self.body[0][1] + dc
        if not (0 <= r < self.H and 0 <= c < self.W):
            return -1
        if self.food and self.food[0] == (r, c):
            self.food.popleft()
            self.score += 1
        else:
            self.cells.discard(self.body.pop())  # tail leaves first
        if (r, c) in self.cells:
            return -1
        self.body.appendleft((r, c))
        self.cells.add((r, c))
        return self.score


# ------------------------------------------------------------------------ tests


def test_bounded_examples():
    assert is_robot_bounded("GGLLGG")       # back at origin
    assert not is_robot_bounded("GG")       # straight line north
    assert is_robot_bounded("GL")           # square loop


def test_bounded_matches_long_simulation():
    rng = random.Random(70)
    for _ in range(500):
        s = "".join(rng.choice("GGLR") for _ in range(rng.randint(1, 10)))
        x, y, d = 0, 0, 0
        positions = []
        for _ in range(40):  # 40 passes, tracking where each pass ends
            x, y, d = walk(s, x, y, d)
            positions.append((x, y))
        back_every_4 = all(positions[k] == (0, 0) for k in range(3, 40, 4))
        drifts = abs(x) + abs(y) >= 40  # unbounded = net shift of >= 1 per pass
        assert is_robot_bounded(s) == back_every_4
        assert is_robot_bounded(s) != drifts


def robot_sim_ray(commands, obstacles):
    """Reference: per command, find the nearest obstacle on the ray by scanning
    the obstacle list, then jump straight to the cell before it."""
    x = y = d = best = 0
    for cmd in commands:
        if cmd == -1:
            d = (d + 1) % 4
        elif cmd == -2:
            d = (d + 3) % 4
        else:
            dx, dy = DIRS[d]
            limit = cmd
            for ox, oy in obstacles:
                # obstacle at step t along the ray: (x + t dx, y + t dy)
                if dx == 0 and ox == x and (oy - y) * dy > 0:
                    t = (oy - y) * dy
                elif dy == 0 and oy == y and (ox - x) * dx > 0:
                    t = (ox - x) * dx
                else:
                    continue
                limit = min(limit, t - 1)
            x, y = x + dx * limit, y + dy * limit
            best = max(best, x * x + y * y)
    return best


def test_robot_sim_matches_ray_scan():
    rng = random.Random(71)
    assert robot_sim([4, -1, 4, -2, 4], [[2, 4]]) == 65
    for _ in range(400):
        obstacles = [[rng.randint(-6, 6), rng.randint(-6, 6)] for _ in range(rng.randint(0, 12))]
        obstacles = [o for o in obstacles if o != [0, 0]]
        commands = [rng.choice([-2, -1, rng.randint(1, 9)]) for _ in range(rng.randint(1, 12))]
        assert robot_sim(commands, obstacles) == robot_sim_ray(commands, obstacles)


class SnakeGameList:
    """Reference: body as a plain list, collision by linear scan."""

    def __init__(self, width, height, food):
        self.W, self.H, self.food, self.body, self.score = width, height, list(map(tuple, food)), [(0, 0)], 0

    def move(self, direction):
        dr, dc = SnakeGame.MOVES[direction]
        r, c = self.body[0][0] + dr, self.body[0][1] + dc
        if not (0 <= r < self.H and 0 <= c < self.W):
            return -1
        eats = self.food and self.food[0] == (r, c)
        rest = self.body if eats else self.body[:-1]
        if (r, c) in rest:
            return -1
        if eats:
            self.food.pop(0)
            self.score += 1
        self.body = [(r, c)] + rest
        return self.score


def test_snake_matches_list_reference():
    rng = random.Random(72)
    for _ in range(300):
        W, H = rng.randint(1, 5), rng.randint(1, 5)
        food = [[rng.randrange(H), rng.randrange(W)] for _ in range(10)]
        a, b = SnakeGame(W, H, food), SnakeGameList(W, H, food)
        for _ in range(30):
            mv = rng.choice("UDLR")
            ra, rb = a.move(mv), b.move(mv)
            assert ra == rb
            if ra == -1:
                break


def test_snake_may_chase_its_tail():
    g = SnakeGame(2, 2, [[0, 1], [1, 1], [1, 0]])
    assert [g.move(m) for m in "RDL"] == [1, 2, 3]  # length 4 fills the 2 x 2 board
    assert g.move("U") == 3   # head enters (0, 0) as the tail leaves it
    assert g.move("D") == -1  # (1, 0) is still body


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
