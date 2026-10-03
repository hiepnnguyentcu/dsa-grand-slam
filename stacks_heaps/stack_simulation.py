"""Stack simulation — the process itself is last-in, first-out.

Signs: things collide with their nearest neighbour ("asteroid collision"),
       nested repetition ("3[a2[c]]"), path components where ".." undoes the
       last one, function call logs with start/end times.
Approach: the stack holds the part of the input that is settled *so far*. A
          new item interacts only with the top: it may destroy it, merge into
          it, or be pushed on top. For nesting, push the outer context on '['
          and pop it back on ']'.
Complexity: O(n) amortised — every item is pushed and popped at most once
            (decode string is O(output length)).
Gotchas:
  - Asteroids: only a right-mover on the stack meeting a left-mover collides.
    A left-mover with nothing (or only left-movers) before it survives.
  - Decode string: repeat counts can have several digits.
  - Simplify path: ".." at the root stays at the root; "..." is a name.
  - Exclusive time: an "end" timestamp is inclusive, so the next start is
    end + 1.

Run the tests at the bottom with:  python3 stacks_heaps/stack_simulation.py
"""


# ---------------------------------------------------------------- implementation


def asteroid_collision(asteroids):
    """Survivors after all collisions; sign is direction, abs is size."""
    stack = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:
            if stack[-1] < -a:
                stack.pop()          # top explodes, keep checking
            elif stack[-1] == -a:
                stack.pop()          # both explode
                alive = False
            else:
                alive = False        # incoming explodes
        if alive:
            stack.append(a)
    return stack


def decode_string(s):
    """'3[a2[c]]' -> 'accaccacc'. Push (prefix, count) on '[', pop on ']'."""
    stack = []
    cur, num = [], 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == "[":
            stack.append((cur, num))
            cur, num = [], 0
        elif ch == "]":
            prev, k = stack.pop()
            prev.append("".join(cur) * k)
            cur = prev
        else:
            cur.append(ch)
    return "".join(cur)


def simplify_path(path):
    """Canonical absolute Unix path."""
    stack = []
    for part in path.split("/"):
        if part == "..":
            if stack:
                stack.pop()
        elif part and part != ".":
            stack.append(part)
    return "/" + "/".join(stack)


def exclusive_time(n, logs):
    """Time each function spent running itself (not its callees).

    logs: "id:start:t" / "id:end:t", t inclusive for both. The stack is the
    call stack; `prev` is when the current top last started being billed.
    """
    res = [0] * n
    stack = []
    prev = 0
    for log in logs:
        fid, kind, t = log.split(":")
        fid, t = int(fid), int(t)
        if kind == "start":
            if stack:
                res[stack[-1]] += t - prev
            stack.append(fid)
            prev = t
        else:
            res[stack.pop()] += t - prev + 1
            prev = t + 1
    return res


# ------------------------------------------------------------------------ tests


def brute_asteroids(a):
    """Collide the first adjacent (right, left) pair until none is left."""
    a = list(a)
    changed = True
    while changed:
        changed = False
        for i in range(len(a) - 1):
            if a[i] > 0 > a[i + 1]:
                x, y = a[i], -a[i + 1]
                a[i : i + 2] = [a[i]] if x > y else ([a[i + 1]] if y > x else [])
                changed = True
                break
    return a


def test_asteroids():
    import random

    assert asteroid_collision([5, 10, -5]) == [5, 10]
    assert asteroid_collision([8, -8]) == []
    assert asteroid_collision([10, 2, -5]) == [10]
    assert asteroid_collision([-2, -1, 1, 2]) == [-2, -1, 1, 2]
    rng = random.Random(1)
    for _ in range(1500):
        a = [rng.choice([-1, 1]) * rng.randint(1, 4) for _ in range(rng.randint(0, 10))]
        assert asteroid_collision(a) == brute_asteroids(a), a


def random_encoding(rng, depth):
    """(encoded, decoded) built together, so the expectation is independent."""
    enc, dec = [], []
    for _ in range(rng.randint(1, 3)):
        if depth and rng.random() < 0.4:
            k = rng.randint(1, 12)  # 10-12 exercises multi-digit counts
            e, d = random_encoding(rng, depth - 1)
            enc.append(f"{k}[{e}]")
            dec.append(d * k)
        else:
            w = "".join(rng.choice("abc") for _ in range(rng.randint(1, 2)))
            enc.append(w)
            dec.append(w)
    return "".join(enc), "".join(dec)


def brute_decode(s):
    """Expand the innermost k[...] with a regex until none remain."""
    import re

    pat = re.compile(r"(\d+)\[([a-z]*)\]")
    while "[" in s:
        s = pat.sub(lambda m: m.group(2) * int(m.group(1)), s)
    return s


def test_decode_string():
    import random

    assert decode_string("3[a]2[bc]") == "aaabcbc"
    assert decode_string("3[a2[c]]") == "accaccacc"
    assert decode_string("2[abc]3[cd]ef") == "abcabccdcdcdef"
    assert decode_string("10[a]") == "a" * 10
    rng = random.Random(2)
    for _ in range(500):
        enc, dec = random_encoding(rng, 3)
        assert decode_string(enc) == dec == brute_decode(enc), enc


def test_simplify_path():
    import posixpath
    import random

    assert simplify_path("/home/") == "/home"
    assert simplify_path("/../") == "/"
    assert simplify_path("/home//foo/") == "/home/foo"
    assert simplify_path("/a/./b/../../c/") == "/c"
    assert simplify_path("/.../a/../b") == "/.../b"
    rng = random.Random(3)
    for _ in range(2000):
        parts = [rng.choice(["", ".", "..", "...", "a", "b", "cd"]) for _ in range(rng.randint(0, 8))]
        p = "/" + "/".join(parts)
        assert simplify_path(p) == posixpath.normpath("/" + p.lstrip("/")), p


def brute_exclusive_time(n, logs):
    """Replay second by second: whoever is on top of the call stack is billed."""
    events = [(int(t), k, int(f)) for f, k, t in (log.split(":") for log in logs)]
    res = [0] * n
    stack = []
    i = 0
    for t in range(events[-1][0] + 1):
        while i < len(events) and events[i][0] == t and events[i][1] == "start":
            stack.append(events[i][2])
            i += 1
        if stack:
            res[stack[-1]] += 1
        while i < len(events) and events[i][0] == t and events[i][1] == "end":
            stack.pop()
            i += 1
    return res


def random_logs(rng, n):
    """A well-nested call log on a strictly increasing integer clock."""
    logs, stack, t = [], [], 0
    for _ in range(rng.randint(1, 6)):
        f = rng.randrange(n)
        logs.append(f"{f}:start:{t}")
        stack.append(f)
        t += rng.randint(1, 3)
        while stack and rng.random() < 0.5:
            logs.append(f"{stack.pop()}:end:{t}")
            t += rng.randint(1, 3)
    while stack:
        logs.append(f"{stack.pop()}:end:{t}")
        t += rng.randint(1, 3)
    return logs


def test_exclusive_time():
    import random

    assert exclusive_time(2, ["0:start:0", "1:start:2", "1:end:5", "0:end:6"]) == [3, 4]
    assert exclusive_time(1, ["0:start:0", "0:start:2", "0:end:5", "0:end:6"]) == [7]
    rng = random.Random(4)
    for _ in range(500):
        n = rng.randint(1, 3)
        logs = random_logs(rng, n)
        assert exclusive_time(n, logs) == brute_exclusive_time(n, logs), logs


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
