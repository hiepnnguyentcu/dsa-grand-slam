"""Histogram problems — largest rectangle, maximal rectangle, trapped water.

Signs: bars of heights, "largest rectangle", a 0/1 matrix and "largest
       rectangle of 1s", "how much water is trapped".
Approach:
  - Largest rectangle: each bar, as the *shortest* bar of a rectangle, extends
    left and right until a strictly lower bar. An increasing stack finds both
    walls: when bar j is popped by i, the right wall is i and the left wall
    is the new stack top.
  - Maximal rectangle: treat each matrix row as the floor of a histogram
    (height = consecutive 1s above) and run the histogram routine per row.
  - Trapping water, stack version: a decreasing stack; popping a bar means it
    is a basin bottom bounded by the new top (left) and the current bar
    (right). Fill it layer by layer. The two-pointer version is O(1) space:
    always advance the side with the lower max, because that max is its
    binding wall.
Complexity: largest rectangle and water O(n); maximal rectangle O(R x C).
Gotchas:
  - Append a 0-height sentinel (or loop to n inclusive) so the stack empties.
  - Width is i - stack[-1] - 1 after the pop, or i if the stack is empty.
  - Water: a basin with no left wall (empty stack after pop) holds nothing.

Run the tests at the bottom with:  python3 stacks_heaps/histogram.py
"""


# ---------------------------------------------------------------- implementation


def largest_rectangle(heights):
    """Area of the largest axis-aligned rectangle under the histogram."""
    stack = []  # indices of increasing heights
    best = 0
    for i in range(len(heights) + 1):
        h = heights[i] if i < len(heights) else 0  # sentinel flushes the stack
        while stack and heights[stack[-1]] > h:
            top = heights[stack.pop()]
            left = stack[-1] if stack else -1
            best = max(best, top * (i - left - 1))
        stack.append(i)
    return best


def maximal_rectangle(matrix):
    """Largest all-1 rectangle in a 0/1 matrix (ints or '0'/'1' chars)."""
    if not matrix:
        return 0
    heights = [0] * len(matrix[0])
    best = 0
    for row in matrix:
        for c, v in enumerate(row):
            heights[c] = heights[c] + 1 if int(v) else 0
        best = max(best, largest_rectangle(heights))
    return best


def trap_stack(height):
    """Trapped rain water, filling basins horizontally with a stack."""
    stack = []  # decreasing heights
    water = 0
    for i, h in enumerate(height):
        while stack and height[stack[-1]] < h:
            bottom = height[stack.pop()]
            if not stack:
                break  # no left wall: water would run off
            left = stack[-1]
            water += (min(height[left], h) - bottom) * (i - left - 1)
        stack.append(i)
    return water


def trap_two_pointers(height):
    """Trapped rain water in O(1) space, filling each column vertically."""
    lo, hi = 0, len(height) - 1
    left_max = right_max = water = 0
    while lo < hi:
        if height[lo] < height[hi]:
            left_max = max(left_max, height[lo])
            water += left_max - height[lo]  # right side is at least as tall
            lo += 1
        else:
            right_max = max(right_max, height[hi])
            water += right_max - height[hi]
            hi -= 1
    return water


# ------------------------------------------------------------------------ tests


def brute_largest_rectangle(h):
    return max(
        (min(h[i:j]) * (j - i) for i in range(len(h)) for j in range(i + 1, len(h) + 1)),
        default=0,
    )


def brute_maximal_rectangle(m):
    R, C = len(m), len(m[0]) if m else 0
    best = 0
    for r1 in range(R):
        for r2 in range(r1, R):
            for c1 in range(C):
                for c2 in range(c1, C):
                    if all(m[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)):
                        best = max(best, (r2 - r1 + 1) * (c2 - c1 + 1))
    return best


def brute_trap(h):
    """Each column holds min(tallest to its left, tallest to its right) - h."""
    return sum(max(0, min(max(h[: i + 1]), max(h[i:])) - h[i]) for i in range(len(h)))


def test_largest_rectangle():
    import random

    assert largest_rectangle([2, 1, 5, 6, 2, 3]) == 10
    assert largest_rectangle([2, 4]) == 4
    assert largest_rectangle([]) == 0
    assert largest_rectangle([3, 3, 3]) == 9  # equal heights
    rng = random.Random(1)
    for _ in range(800):
        h = [rng.randint(0, 6) for _ in range(rng.randint(0, 12))]
        assert largest_rectangle(h) == brute_largest_rectangle(h), h


def test_maximal_rectangle():
    import random

    m = [list("10100"), list("10111"), list("11111"), list("10010")]
    assert maximal_rectangle(m) == 6
    assert maximal_rectangle([["0"]]) == 0
    assert maximal_rectangle([]) == 0
    rng = random.Random(2)
    for _ in range(300):
        R, C = rng.randint(1, 5), rng.randint(1, 5)
        m = [[int(rng.random() < 0.7) for _ in range(C)] for _ in range(R)]
        assert maximal_rectangle(m) == brute_maximal_rectangle(m), m


def test_trap():
    import random

    assert trap_stack([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert trap_two_pointers([4, 2, 0, 3, 2, 5]) == 9
    assert trap_stack([]) == trap_two_pointers([]) == 0
    rng = random.Random(3)
    for _ in range(1000):
        h = [rng.randint(0, 6) for _ in range(rng.randint(0, 14))]
        assert trap_stack(h) == trap_two_pointers(h) == brute_trap(h), h


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
