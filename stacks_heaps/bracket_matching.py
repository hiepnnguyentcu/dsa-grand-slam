"""Bracket matching — the stack as a record of what is still open.

Signs: "valid parentheses", nested structure, "minimum insertions/removals to
       make it valid", "longest valid substring", anything where the most
       recent opener must close first.
Approach: push each opener; on a closer, the top of the stack must be its
          partner. With one bracket type, a counter replaces the stack. Push
          *indices* instead of characters when the answer is a length or a set
          of positions to delete.
Complexity: O(n) time, O(n) space (O(1) with a counter for one bracket type).
Gotchas:
  - Check the stack is non-empty before peeking on a closer.
  - "Valid" also needs an empty stack at the end — leftover openers fail.
  - For longest-valid, seed the stack with -1: a sentinel "last unmatched"
    index, so lengths come out as i - stack[-1].

Run the tests at the bottom with:  python3 stacks_heaps/bracket_matching.py
"""

PAIRS = {")": "(", "]": "[", "}": "{"}


# ---------------------------------------------------------------- implementation


def is_valid(s):
    """True if every bracket in s closes the most recent unclosed opener."""
    stack = []
    for ch in s:
        if ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
        else:
            stack.append(ch)
    return not stack


def min_add_to_make_valid(s):
    """Fewest '(' or ')' insertions to balance s (one bracket type).

    `open_` counts unmatched '(' so far; a ')' with nothing to match costs one
    insertion. Whatever is still open at the end needs a ')' each.
    """
    open_ = added = 0
    for ch in s:
        if ch == "(":
            open_ += 1
        elif open_:
            open_ -= 1
        else:
            added += 1
    return added + open_


def longest_valid_parentheses(s):
    """Length of the longest balanced substring of '(' and ')'.

    The stack holds indices of characters not yet matched; its bottom is the
    last unmatched ')' (or -1). After a match, the valid run ends at i and
    starts just after whatever is now on top.
    """
    stack = [-1]
    best = 0
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        else:
            stack.pop()
            if stack:
                best = max(best, i - stack[-1])
            else:
                stack.append(i)  # new barrier: this ')' can never be matched
    return best


def min_remove_to_make_valid(s):
    """Delete the fewest parentheses so s is balanced; letters stay.

    Unmatched ')' are known the moment they appear; unmatched '(' are the
    indices left on the stack at the end.
    """
    drop = set()
    stack = []
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        elif ch == ")":
            if stack:
                stack.pop()
            else:
                drop.add(i)
    drop.update(stack)
    return "".join(ch for i, ch in enumerate(s) if i not in drop)


# ------------------------------------------------------------------------ tests


def brute_is_valid(s):
    """Reference: repeatedly delete adjacent matched pairs until none remain."""
    prev = None
    while prev != s:
        prev = s
        s = s.replace("()", "").replace("[]", "").replace("{}", "")
    return s == ""


def brute_longest_valid(s):
    return max(
        (j - i for i in range(len(s)) for j in range(i, len(s) + 1) if brute_is_valid(s[i:j])),
        default=0,
    )


def brute_min_remove_count(s):
    """Fewest deletions, by trying every subset of parenthesis positions."""
    from itertools import combinations

    paren = [i for i, ch in enumerate(s) if ch in "()"]
    for k in range(len(paren) + 1):
        for drop in combinations(paren, k):
            t = "".join(ch for i, ch in enumerate(s) if i not in drop)
            if brute_is_valid("".join(c for c in t if c in "()")):
                return k
    return len(paren)


def random_strings(alphabet, count, max_len, seed):
    import random

    rng = random.Random(seed)
    for _ in range(count):
        yield "".join(rng.choice(alphabet) for _ in range(rng.randint(0, max_len)))


def test_is_valid_examples():
    assert is_valid("()[]{}")
    assert is_valid("{[()]}")
    assert not is_valid("(]")
    assert not is_valid("([)]")
    assert not is_valid("((")      # leftover openers
    assert not is_valid(")")       # closer on an empty stack
    assert is_valid("")


def test_is_valid_matches_brute_force():
    for s in random_strings("()[]{}", 2000, 10, seed=1):
        assert is_valid(s) == brute_is_valid(s), s


def test_min_add():
    assert min_add_to_make_valid("())") == 1
    assert min_add_to_make_valid("(((") == 3
    assert min_add_to_make_valid("()))((") == 4
    for s in random_strings("()", 500, 10, seed=2):
        assert is_valid(s) == (min_add_to_make_valid(s) == 0)
        # insertions needed == deletions needed for a single bracket type
        assert min_add_to_make_valid(s) == brute_min_remove_count(s)


def test_longest_valid():
    assert longest_valid_parentheses("(()") == 2
    assert longest_valid_parentheses(")()())") == 4
    assert longest_valid_parentheses("()(())") == 6
    assert longest_valid_parentheses("") == 0
    for s in random_strings("()", 500, 12, seed=3):
        assert longest_valid_parentheses(s) == brute_longest_valid(s), s


def test_min_remove():
    assert min_remove_to_make_valid("lee(t(c)o)de)") == "lee(t(c)o)de"
    assert min_remove_to_make_valid("))((") == ""
    for s in random_strings("()ab", 400, 9, seed=4):
        out = min_remove_to_make_valid(s)
        assert brute_is_valid("".join(c for c in out if c in "()"))
        assert len(s) - len(out) == brute_min_remove_count(s), s
        assert [c for c in out if c not in "()"] == [c for c in s if c not in "()"]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
