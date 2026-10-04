"""Removal / deletion — remove the fewest chars to make a string valid.

Signs: "remove the minimum number of ... return all results".
Approach: count first how many '(' and ')' must go (left_rem, right_rem).
          Then start is a slot (char index): keep it, or remove it if that
          kind still has removals left. Track open_count so a prefix with
          more ')' than '(' dies early. Record at the end when
          left_rem == right_rem == 0 and open_count == 0.
          Dedup: collect into a set.
Complexity: O(2^n * n) worst case.
Gotchas:
  - Without the min-removal counts you enumerate every subsequence.
  - Letters are always kept.
  - 402 (remove k digits for the smallest number) is greedy with a monotonic
    stack, not backtracking: stacks_heaps/monotonic_greedy.py.

Run the tests at the bottom with:  python3 backtracking/removal.py
"""

import random
from itertools import combinations


# ---------------------------------------------------------------- implementation


def remove_invalid_parentheses(s):
    """LC 301."""
    left_rem = right_rem = 0
    for char in s:
        if char == "(":
            left_rem += 1
        elif char == ")":
            if left_rem:
                left_rem -= 1
            else:
                right_rem += 1

    n = len(s)
    res = set()

    def dfs(start, temp, open_count, left_rem, right_rem):
        if start == n:
            if left_rem == right_rem == 0 and open_count == 0:
                res.add("".join(temp))
            return
        char = s[start]

        # Remove
        if char == "(" and left_rem:
            dfs(start + 1, temp, open_count, left_rem - 1, right_rem)
        if char == ")" and right_rem:
            dfs(start + 1, temp, open_count, left_rem, right_rem - 1)

        # Keep
        if char == ")" and open_count == 0:
            return
        temp.append(char)
        delta = 1 if char == "(" else -1 if char == ")" else 0
        dfs(start + 1, temp, open_count + delta, left_rem, right_rem)
        temp.pop()

    dfs(0, [], 0, left_rem, right_rem)
    return list(res)


# ------------------------------------------------------------------------ tests


def is_valid(s):
    bal = 0
    for char in s:
        bal += 1 if char == "(" else -1 if char == ")" else 0
        if bal < 0:
            return False
    return bal == 0


def brute_remove(s):
    for k in range(len(s) + 1):
        found = {"".join(s[i] for i in range(len(s)) if i not in drop)
                 for drop in map(set, combinations(range(len(s)), k))}
        found = {x for x in found if is_valid(x)}
        if found:
            return found


def test_remove_invalid_parentheses_examples():
    assert sorted(remove_invalid_parentheses("()())()")) == ["(())()", "()()()"]
    assert sorted(remove_invalid_parentheses("(a)())()")) == ["(a())()", "(a)()()"]
    assert remove_invalid_parentheses(")(") == [""]


def test_remove_invalid_parentheses_vs_brute_force():
    random.seed(1)
    for _ in range(150):
        s = "".join(random.choice("(()a") for _ in range(random.randint(0, 10)))
        assert set(remove_invalid_parentheses(s)) == brute_remove(s)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
