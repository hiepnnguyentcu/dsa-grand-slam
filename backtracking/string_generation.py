"""String generation — build every valid string one character at a time.

Signs: "generate all valid parentheses", "letter combinations of a phone
       number", "all expressions that evaluate to target", output is a list
       of strings.
Approach: each level appends one character. Keep just enough state to know
          which characters are legal next, so invalid prefixes are never
          built.
            - Parentheses: track open and close counts. Add "(" while
              open < n; add ")" while close < open. Every leaf is valid; no
              check at the end.
            - Phone letters: level i loops over the letters of digit i.
            - Add operators: between each pair of digits choose "+", "-",
              "*" or nothing. Carry the running value and the last operand so
              "*" can undo the last addition: val - last + last * cur.
Complexity: parentheses produce Catalan(n) ~ 4^n / n^1.5 strings; phone is
            O(4^n * n); add operators O(4^n * n).
Gotchas:
  - Guarding ")" with close < open (not close < n) is what keeps prefixes
    valid. Without it you generate and filter 2^(2n) strings.
  - Empty digit string -> [], not [""].
  - Add operators: a multi-digit operand may not start with "0" ("05").
  - Only the count of valid parentheses? Catalan number, no search
    (dynamic_programming/counting_dp.py).

Run the tests at the bottom with:  python3 backtracking/string_generation.py
"""

import random
from itertools import product


PHONE = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
         "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


# ---------------------------------------------------------------- implementation


def generate_parentheses(n):
    """All balanced strings of n pairs, in lexicographic order."""
    out, path = [], []

    def go(opened, closed):
        if closed == n:
            out.append("".join(path))
            return
        if opened < n:
            path.append("("); go(opened + 1, closed); path.pop()
        if closed < opened:
            path.append(")"); go(opened, closed + 1); path.pop()
    go(0, 0)
    return out


def letter_combinations(digits):
    """All strings the digits can spell on a phone keypad."""
    if not digits:
        return []
    out, path = [], []

    def go(i):
        if i == len(digits):
            out.append("".join(path))
            return
        for ch in PHONE[digits[i]]:
            path.append(ch); go(i + 1); path.pop()
    go(0)
    return out


def add_operators(num, target):
    """Insert + - * between digits so the expression equals target."""
    out = []

    def go(i, expr, val, last):
        if i == len(num):
            if val == target:
                out.append(expr)
            return
        for j in range(i + 1, len(num) + 1):
            s = num[i:j]
            if len(s) > 1 and s[0] == "0":
                break                         # no leading zeros
            cur = int(s)
            if i == 0:
                go(j, s, cur, cur)
            else:
                go(j, expr + "+" + s, val + cur, cur)
                go(j, expr + "-" + s, val - cur, -cur)
                go(j, expr + "*" + s, val - last + last * cur, last * cur)
    if num:
        go(0, "", 0, 0)
    return out


# ------------------------------------------------------------------------ tests


def balanced(s):
    depth = 0
    for c in s:
        depth += 1 if c == "(" else -1
        if depth < 0:
            return False
    return depth == 0


def test_parentheses_classic():
    assert generate_parentheses(3) == ["((()))", "(()())", "(())()", "()(())", "()()()"]
    assert generate_parentheses(0) == [""]


def test_parentheses_vs_filter_all_strings():
    catalan = [1, 1, 2, 5, 14, 42, 132, 429]
    for n in range(0, 8):
        want = sorted("".join(t) for t in product("()", repeat=2 * n) if balanced("".join(t)))
        got = generate_parentheses(n)
        assert got == want and len(got) == catalan[n]


def test_letter_combinations():
    assert letter_combinations("23") == ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]
    assert letter_combinations("") == []
    random.seed(9)
    for _ in range(20):
        d = "".join(random.choice("23456789") for _ in range(random.randint(1, 4)))
        assert letter_combinations(d) == ["".join(t) for t in product(*(PHONE[c] for c in d))]


def test_add_operators_classic():
    assert sorted(add_operators("123", 6)) == ["1*2*3", "1+2+3"]
    assert sorted(add_operators("232", 8)) == ["2*3+2", "2+3*2"]
    assert sorted(add_operators("105", 5)) == ["1*0+5", "10-5"]
    assert add_operators("3456237490", 9191) == []


def test_add_operators_vs_eval():
    random.seed(10)
    for _ in range(25):
        num = "".join(random.choice("0123") for _ in range(random.randint(1, 5)))
        target = random.randint(-5, 15)
        want = set()
        for ops in product(["+", "-", "*", ""], repeat=len(num) - 1):
            expr = num[0] + "".join(o + d for o, d in zip(ops, num[1:]))
            operands = expr.replace("+", " ").replace("-", " ").replace("*", " ").split()
            if any(len(x) > 1 and x[0] == "0" for x in operands):
                continue
            if eval(expr) == target:
                want.add(expr)
        assert sorted(add_operators(num, target)) == sorted(want)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
