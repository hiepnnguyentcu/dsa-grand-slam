"""String / expression construction — parentheses, phone letters, operators.

Signs: "generate all strings / expressions", each position picks from a small
       alphabet, maybe under a running rule (balance, value).
Approach: start is a slot (position being written) -> start + 1; no loop over
          an index range, just over the choices for this slot.
          Prune with counters you carry: open_count / close_count (22),
          curr_val / last operand (282).
Complexity: 22 is Catalan(n) * n; 17 is 4^n * n; 282 is 4^n * n.
Gotchas:
  - 22 brute force (2^(2n) then validate) works but the counted version
    never builds an invalid prefix: `(` while open < n, `)` while close < open.
  - 282 multiplication: curr - last + last * val (undo the last term, redo it
    multiplied). Leading zero: "05" is not an operand -> break.
  - 282 first operand gets no operator in front.
  - Only a count (494)? That's knapsack DP:
    dynamic_programming/knapsack.py count_target_signs.

Run the tests at the bottom with:  python3 backtracking/string_construction.py
"""

import random
from itertools import product


# ---------------------------------------------------------------- implementation


def generate_parenthesis_brute(n):
    """LC 22, brute: every ( / ) string of length 2n, keep the valid ones."""
    res = []

    def is_valid(temp):
        stack = []
        for item in temp:
            if item == "(":
                stack.append(item)
            elif item == ")":
                if stack and stack[-1] == "(":
                    stack.pop()
                else:
                    return False
        return True if not stack else False

    def dfs(start, res, temp):
        if start == 2 * n:
            if is_valid(temp):
                res.append("".join(temp))
            return

        for parenthesis in ["(", ")"]:
            temp.append(parenthesis)
            dfs(start + 1, res, temp)
            temp.pop()

    dfs(0, res, [])
    return res


def generate_parenthesis(n):
    """LC 22, counted: only valid prefixes are ever built."""
    res = []

    def dfs(res, temp, open_count, close_count):
        if open_count == close_count == n:
            res.append("".join(temp))
            return
        if open_count < n:
            temp.append("(")
            dfs(res, temp, 1 + open_count, close_count)
            temp.pop()
        if close_count < open_count:
            temp.append(")")
            dfs(res, temp, open_count, 1 + close_count)
            temp.pop()

    dfs(res, [], 0, 0)
    return res


def letter_combinations(digits):
    """LC 17."""
    if not digits:
        return []
    digit_char_m = {
        "2": ["a", "b", "c"],
        "3": ["d", "e", "f"],
        "4": ["g", "h", "i"],
        "5": ["j", "k", "l"],
        "6": ["m", "n", "o"],
        "7": ["p", "q", "r", "s"],
        "8": ["t", "u", "v"],
        "9": ["w", "x", "y", "z"],
    }

    res = []
    n = len(digits)

    def dfs(start, res, temp):
        if start == n:
            res.append("".join(temp))
            return

        digit = digits[start]
        valid_chars = digit_char_m[digit]

        for char in valid_chars:
            temp.append(char)
            dfs(start + 1, res, temp)
            temp.pop()

    dfs(0, res, [])
    return res


def add_operators(num, target):
    """LC 282. Insert + - * between digits to reach target."""
    n = len(num)
    res = []

    def dfs(start, res, temp, curr_val, last):
        if start == n:
            if curr_val == target:
                res.append("".join(temp))
            return
        for i in range(start, n):
            piece = num[start:i + 1]
            if len(piece) > 1 and piece[0] == "0":
                break
            val = int(piece)
            if start == 0:
                temp.append(piece)
                dfs(i + 1, res, temp, val, val)
                temp.pop()
                continue
            for op, next_val, next_last in (
                ("+", curr_val + val, val),
                ("-", curr_val - val, -val),
                ("*", curr_val - last + last * val, last * val),
            ):
                temp.append(op + piece)
                dfs(i + 1, res, temp, next_val, next_last)
                temp.pop()

    dfs(0, res, [], 0, 0)
    return res


def find_target_sum_ways(nums, target):
    """LC 494. +/- in front of each number; count ways to hit target."""
    n = len(nums)

    def dfs(start, curr_sum):
        if start == n:
            return 1 if curr_sum == target else 0
        return dfs(start + 1, curr_sum + nums[start]) + dfs(start + 1, curr_sum - nums[start])
    return dfs(0, 0)


# ------------------------------------------------------------------------ tests


def test_parentheses_two_ways_agree():
    catalan = [1, 1, 2, 5, 14, 42, 132, 429]
    for n in range(1, 8):
        a, b = generate_parenthesis(n), generate_parenthesis_brute(n)
        assert sorted(a) == sorted(b) and len(a) == catalan[n]


def test_letter_combinations_vs_product():
    assert letter_combinations("") == []
    assert sorted(letter_combinations("23")) == sorted(a + b for a in "abc" for b in "def")
    random.seed(1)
    keys = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    for _ in range(20):
        digits = "".join(random.choice("23456789") for _ in range(random.randint(1, 4)))
        want = sorted("".join(p) for p in product(*(keys[d] for d in digits)))
        assert sorted(letter_combinations(digits)) == want


def test_add_operators_vs_eval():
    assert sorted(add_operators("123", 6)) == ["1*2*3", "1+2+3"]
    assert sorted(add_operators("105", 5)) == ["1*0+5", "10-5"]
    assert add_operators("3456237490", 9191) == []
    random.seed(2)
    for _ in range(40):
        num = "".join(random.choice("0123") for _ in range(random.randint(1, 5)))
        target = random.randint(-10, 30)
        want = set()
        for gaps in product(["", "+", "-", "*"], repeat=len(num) - 1):
            expr = num[0] + "".join(g + d for g, d in zip(gaps, num[1:]))
            operands = expr.replace("+", " ").replace("-", " ").replace("*", " ").split()
            if any(len(x) > 1 and x[0] == "0" for x in operands):
                continue
            if eval(expr) == target:
                want.add(expr)
        got = add_operators(num, target)
        assert len(got) == len(want) and set(got) == want


def test_find_target_sum_ways_vs_product():
    assert find_target_sum_ways([1, 1, 1, 1, 1], 3) == 5
    random.seed(3)
    for _ in range(40):
        nums = [random.randint(0, 5) for _ in range(random.randint(1, 8))]
        target = random.randint(-6, 6)
        want = sum(sum(s * x for s, x in zip(signs, nums)) == target
                   for signs in product([1, -1], repeat=len(nums)))
        assert find_target_sum_ways(nums, target) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
