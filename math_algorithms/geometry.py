"""Geometry primitives — cross product, exact slopes, overlaps, convex hull.

Signs: collinear points, left/right turn, "max points on a line", rectangle
       overlap or union area, "is this a valid square", polygon area, fence
       around trees (convex hull).
Approach: stay in integers.
  - cross(o, a, b) = (a - o) x (b - o) is twice the signed triangle area:
    > 0 counter-clockwise (left turn), < 0 clockwise, 0 collinear.
  - A slope is the reduced pair (dy, dx) with a fixed sign convention — never
    a float, which confuses 1/3 with 0.333... and has two zeros.
  - Compare squared distances; sqrt only adds rounding error.
  - Axis-aligned rectangles overlap iff their x-intervals and y-intervals
    both overlap.
  - Monotone chain hull: sort points, build the lower and upper chains,
    popping whenever the last turn is not counter-clockwise.
Complexity: O(1) per primitive; max points on a line O(n^2); hull O(n log n).
Gotchas:
  - Duplicate points lie on every line through them: count them separately.
  - Normalise the slope sign: (1, -2) and (-1, 2) are the same line.
  - Rectangles that only touch share no area: use strict >.
  - Hull: pop on cross <= 0 for vertices only; pop on cross < 0 to keep
    collinear boundary points ("erect the fence"), and then de-duplicate,
    because an all-collinear input comes back from both chains.

Run the tests at the bottom with:  python3 math_algorithms/geometry.py
"""

from collections import Counter

from gcd_lcm import gcd


# ---------------------------------------------------------------- implementation


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def dist2(p, q):
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def orientation(o, a, b):
    """1 counter-clockwise, -1 clockwise, 0 collinear."""
    c = cross(o, a, b)
    return (c > 0) - (c < 0)


def slope_key(dx, dy):
    """Canonical direction of a line: reduced, with dx > 0 or (dx == 0 and dy > 0)."""
    g = gcd(dx, dy)
    dx, dy = dx // g, dy // g
    if dx < 0 or (dx == 0 and dy < 0):
        dx, dy = -dx, -dy
    return dx, dy


def max_points_on_line(pts):
    """Most points of `pts` that lie on one straight line (duplicates allowed)."""
    best = 0
    for i, p in enumerate(pts):
        same, slopes = 1, Counter()
        for q in pts[i + 1 :]:
            dx, dy = q[0] - p[0], q[1] - p[1]
            if dx == 0 and dy == 0:
                same += 1  # a copy of p is on every line through p
            else:
                slopes[slope_key(dx, dy)] += 1
        best = max(best, same + max(slopes.values(), default=0))
    return best


def rect_overlap(r1, r2):
    """Positive-area overlap of axis-aligned rectangles (x1, y1, x2, y2)."""
    return min(r1[2], r2[2]) > max(r1[0], r2[0]) and min(r1[3], r2[3]) > max(r1[1], r2[1])


def rect_intersection_area(r1, r2):
    w = min(r1[2], r2[2]) - max(r1[0], r2[0])
    h = min(r1[3], r2[3]) - max(r1[1], r2[1])
    return max(w, 0) * max(h, 0)


def valid_square(p1, p2, p3, p4):
    """Four points form a square with positive area, in any order.

    Of the six pairwise squared distances, a square has four equal sides and
    two equal diagonals, with diagonal == 2 * side. The ratio check rules out
    the rhombus, which also has only two distinct lengths.
    """
    pts = [p1, p2, p3, p4]
    d = sorted(dist2(pts[i], pts[j]) for i in range(4) for j in range(i + 1, 4))
    return d[0] > 0 and d[0] == d[3] and d[4] == d[5] and d[4] == 2 * d[0]


def polygon_area2(poly):
    """Twice the signed area (shoelace); positive for counter-clockwise order."""
    n = len(poly)
    return sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1]
               for i in range(n))


def convex_hull(points, keep_collinear=False):
    """Hull in counter-clockwise order, starting from the lowest-x (then lowest-y) point.

    keep_collinear=False returns only the corners; True also keeps points
    lying on the hull's edges.
    """
    pts = sorted(set(map(tuple, points)))
    if len(pts) <= 2:
        return pts

    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (cross(h[-2], h[-1], p) < 0 if keep_collinear
                                   else cross(h[-2], h[-1], p) <= 0):
                h.pop()
            h.append(p)
        return h

    lower, upper = half(pts), half(reversed(pts))
    return list(dict.fromkeys(lower[:-1] + upper[:-1]))


# ------------------------------------------------------------------------ tests


def _on_hull_boundary(p, pts):
    """Brute force: some line through p and another point has every point on one side."""
    return any(q != p and (all(cross(p, q, r) >= 0 for r in pts) or
                           all(cross(p, q, r) <= 0 for r in pts))
               for q in pts)


def _is_hull_vertex(p, pts):
    """Brute force: a supporting line through p whose other collinear points
    all lie on the same side of p (so p is an end, not the middle, of an edge)."""
    for q in pts:
        if q == p:
            continue
        for sign in (1, -1):
            if all(sign * cross(p, q, r) >= 0 for r in pts):
                on_line = [r for r in pts if r != p and cross(p, q, r) == 0]
                dot = [(r[0] - p[0]) * (q[0] - p[0]) + (r[1] - p[1]) * (q[1] - p[1])
                       for r in on_line]
                if all(v > 0 for v in dot):
                    return True
    return False


def test_cross_and_orientation():
    o = (0, 0)
    assert cross(o, (1, 0), (0, 1)) == 1 and orientation(o, (1, 0), (0, 1)) == 1
    assert orientation(o, (0, 1), (1, 0)) == -1
    assert orientation(o, (2, 2), (5, 5)) == 0
    assert orientation((1, 1), (2, 2), (-7, -7)) == 0  # collinear, behind o
    # huge integer coordinates stay exact where floats would not
    big = 10**18
    # big * (big + 2) - (big + 1) ** 2 == -1: a clockwise turn
    assert cross((0, 0), (big, big + 1), (big + 1, big + 2)) == -1
    fb = float(big)
    assert fb * (fb + 2) - (fb + 1) * (fb + 1) == 0  # floats call it collinear
    assert orientation((0, 0), (big, big), (big + 1, big + 1)) == 0


def test_float_slopes_collide_but_keys_do_not():
    a, b = 10**17, 10**17 + 1  # two different slopes
    assert a / b == 1.0  # float cannot tell them apart
    assert slope_key(b, a) != slope_key(1, 1)


def test_slope_key_normalises():
    assert slope_key(2, 4) == slope_key(-1, -2) == (1, 2)
    assert slope_key(-3, 6) == slope_key(1, -2) == (1, -2)
    assert slope_key(0, 5) == slope_key(0, -3) == (0, 1)
    assert slope_key(-4, 0) == slope_key(7, 0) == (1, 0)


def test_max_points_on_line_against_brute_force():
    import random
    from itertools import combinations

    def brute(pts):
        if len(pts) <= 2:
            return len(pts)
        best = 1
        for p, q in combinations(pts, 2):
            if p == q:
                count = sum(r == p for r in pts)
            else:
                count = sum(cross(p, q, r) == 0 for r in pts)
            best = max(best, count)
        return best

    rng = random.Random(35)
    for _ in range(400):
        n = rng.randint(0, 12)
        pts = [(rng.randint(-4, 4), rng.randint(-4, 4)) for _ in range(n)]
        assert max_points_on_line(pts) == brute(pts), pts
    assert max_points_on_line([(1, 1), (3, 2), (5, 3), (4, 1), (2, 3), (1, 4)]) == 4
    assert max_points_on_line([(0, 0), (0, 0), (0, 0)]) == 3
    assert max_points_on_line([(0, 0), (0, 0), (1, 1), (5, 0)]) == 3


def test_rect_overlap_and_area():
    import random

    def brute_area(r1, r2):
        return sum(1 for x in range(-6, 6) for y in range(-6, 6)
                   if r1[0] <= x < r1[2] and r1[1] <= y < r1[3]
                   and r2[0] <= x < r2[2] and r2[1] <= y < r2[3])

    rng = random.Random(36)
    for _ in range(1500):
        rs = []
        for _ in range(2):
            x1, x2 = sorted(rng.sample(range(-5, 6), 2))
            y1, y2 = sorted(rng.sample(range(-5, 6), 2))
            rs.append((x1, y1, x2, y2))
        area = brute_area(*rs)  # unit cells counted one by one
        assert rect_intersection_area(*rs) == area
        assert rect_overlap(*rs) == (area > 0)
    assert not rect_overlap((0, 0, 1, 1), (1, 0, 2, 1))  # touching edge
    assert not rect_overlap((0, 0, 1, 1), (1, 1, 2, 2))  # touching corner
    assert rect_overlap((0, 0, 2, 2), (1, 1, 3, 3))


def test_valid_square():
    from itertools import permutations

    square = [(0, 0), (1, 1), (1, 0), (0, 1)]
    tilted = [(0, 0), (2, 1), (1, 3), (-1, 2)]
    for pts in (square, tilted):
        assert all(valid_square(*p) for p in permutations(pts))
    assert not valid_square((0, 0), (0, 0), (0, 0), (0, 0))
    assert not valid_square((0, 0), (2, 1), (3, 3), (1, 2))  # rhombus
    assert not valid_square((0, 0), (2, 0), (2, 1), (0, 1))  # rectangle
    assert not valid_square((0, 0), (1, 1), (1, 0), (0, 0))  # repeated point

    # brute force over a small grid: a square iff some ordering walks
    # four equal sides with right angles
    import random

    def brute(pts):
        if len(set(pts)) < 4:
            return False
        for a, b, c, d in permutations(pts):
            v = (b[0] - a[0], b[1] - a[1])
            if (c == (b[0] - v[1], b[1] + v[0]) and d == (a[0] - v[1], a[1] + v[0])):
                return True
        return False

    rng = random.Random(37)
    for _ in range(3000):
        pts = [(rng.randint(0, 3), rng.randint(0, 3)) for _ in range(4)]
        assert valid_square(*pts) == brute(pts), pts


def test_polygon_area():
    assert polygon_area2([(0, 0), (4, 0), (4, 3), (0, 3)]) == 24
    assert polygon_area2([(0, 0), (0, 3), (4, 3), (4, 0)]) == -24  # clockwise
    assert polygon_area2([(0, 0), (1, 1), (2, 2)]) == 0  # degenerate


def test_convex_hull_against_brute_force():
    import random

    rng = random.Random(38)
    for _ in range(400):
        pts = [(rng.randint(-5, 5), rng.randint(-5, 5)) for _ in range(rng.randint(1, 15))]
        uniq = sorted(set(pts))
        if len(uniq) <= 2:
            assert convex_hull(pts) == uniq
            continue
        corners = convex_hull(pts)
        fence = convex_hull(pts, keep_collinear=True)
        assert sorted(corners) == [p for p in uniq if _is_hull_vertex(p, uniq)], pts
        assert sorted(fence) == [p for p in uniq if _on_hull_boundary(p, uniq)], pts
        if len(corners) >= 3:
            # strictly counter-clockwise, and starts at the smallest point
            n = len(corners)
            assert corners[0] == uniq[0]
            assert all(cross(corners[i], corners[(i + 1) % n], corners[(i + 2) % n]) > 0
                       for i in range(n))
            # every input point is inside or on the hull
            assert all(cross(corners[i], corners[(i + 1) % n], p) >= 0
                       for p in uniq for i in range(n))


def test_convex_hull_degenerate_inputs():
    assert convex_hull([]) == []
    assert convex_hull([(1, 1), (1, 1)]) == [(1, 1)]
    assert convex_hull([[0, 0], [3, 3]]) == [(0, 0), (3, 3)]  # lists accepted
    line = [(0, 0), (1, 1), (2, 2), (3, 3)]
    assert convex_hull(line) == [(0, 0), (3, 3)]
    assert sorted(convex_hull(line, keep_collinear=True)) == line  # no duplicates
    square = [(0, 0), (2, 0), (2, 2), (0, 2), (1, 1), (1, 0)]
    assert convex_hull(square) == [(0, 0), (2, 0), (2, 2), (0, 2)]
    assert convex_hull(square, keep_collinear=True) == [(0, 0), (1, 0), (2, 0), (2, 2), (0, 2)]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
