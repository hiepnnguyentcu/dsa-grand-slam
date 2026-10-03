"""Expression evaluation — RPN, and infix with precedence and parentheses.

Signs: "evaluate reverse Polish notation", "basic calculator", a string of
       numbers, + - * / and brackets, operator precedence, unary minus.
Approach:
  - RPN: push numbers; an operator pops two, applies, pushes the result.
  - Infix (shunting-yard): an operand stack and an operator stack. Before
    pushing an operator, apply every stacked operator that binds at least as
    tightly. '(' is a wall; ')' applies down to the wall. Emit instead of apply
    and you get RPN.
  - Only + - and brackets: keep a running sum and a stack of signs, one per
    open bracket. No operator stack needed.
Complexity: O(n) time and space — each token is pushed and popped once.
Gotchas:
  - Pop order: the *second* pop is the left operand (`b = pop(); a = pop()`).
  - Integer division truncates toward zero here (C/Java/LeetCode). Python's
    // floors, so -7 // 2 == -4, not -3.
  - Unary minus: a '-' where an operand is expected. Treat it as "0 - x" with
    the highest precedence, so -3*4 and 2*-3 both work.
  - Multi-digit numbers: keep reading digits before emitting a token.

Run the tests at the bottom with:  python3 stacks_heaps/expression_eval.py
"""

PREC = {"+": 1, "-": 1, "*": 2, "/": 2, "u": 3}  # "u" = unary minus


# ---------------------------------------------------------------- implementation


def trunc_div(a, b):
    """Integer division truncating toward zero, exactly, without floats."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q


def apply(op, a, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    return trunc_div(a, b)


def eval_rpn(tokens):
    """Value of a postfix token list, e.g. ["2", "1", "+", "3", "*"] -> 9."""
    stack = []
    for t in tokens:
        if t in "+-*/":
            b = stack.pop()  # right operand comes off first
            a = stack.pop()
            stack.append(apply(t, a, b))
        else:
            stack.append(int(t))
    return stack[0]


def tokenize(s):
    """Numbers as ints, operators and brackets as strings; unary '-' -> 'u'."""
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch.isdigit():
            j = i
            while j < len(s) and s[j].isdigit():
                j += 1
            out.append(int(s[i:j]))
            i = j
            continue
        if ch == "-" and (not out or out[-1] in ("(", "+", "-", "*", "/", "u")):
            out.append("u")  # no operand before it: this minus is unary
        elif ch in "+-*/()":
            out.append(ch)
        i += 1
    return out


def _shunting_yard(s, on_number, on_operator):
    """The shared driver: `on_operator(op)` is called in evaluation order."""
    ops = []

    def flush_while(cond):
        while ops and ops[-1] != "(" and cond(ops[-1]):
            on_operator(ops.pop())

    for t in tokenize(s):
        if isinstance(t, int):
            on_number(t)
        elif t == "(":
            ops.append(t)
        elif t == ")":
            flush_while(lambda top: True)
            ops.pop()  # the "("
        elif t == "u":
            on_number(0)  # unary minus is "0 - x"; prefix, so pop nothing
            ops.append(t)
        else:  # binary: left-associative, so pop ties too
            flush_while(lambda top: PREC[top] >= PREC[t])
            ops.append(t)
    flush_while(lambda top: True)


def calculate(s):
    """Evaluate infix with + - * /, brackets, unary minus, spaces."""
    vals = []

    def on_operator(op):
        b = vals.pop()
        a = vals.pop()
        vals.append(apply("-" if op == "u" else op, a, b))

    _shunting_yard(s, vals.append, on_operator)
    return vals[0]


def to_rpn(s):
    """Infix -> postfix tokens (strings). Unary minus becomes '0 x -'."""
    out = []
    _shunting_yard(s, lambda n: out.append(str(n)), lambda op: out.append("-" if op == "u" else op))
    return out


def calculate_add_sub(s):
    """Only + - and brackets: a running sum and a stack of bracket signs.

    `signs[-1]` is the sign the current bracket level contributes overall, so
    each number is added as  sign_of_level * its_own_sign * value.
    """
    total, num, sign = 0, 0, 1
    signs = [1]
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
            continue
        if ch in "+-()":
            total += signs[-1] * sign * num
            num = 0
        if ch == "+":
            sign = 1
        elif ch == "-":
            sign = -1
        elif ch == "(":
            signs.append(signs[-1] * sign)
            sign = 1
        elif ch == ")":
            signs.pop()
    return total + signs[-1] * sign * num


# ------------------------------------------------------------------------ tests


def random_expr(rng, depth, ops):
    """(string, value) of a random expression tree, valued independently.

    The value is computed straight from the tree, so it shares no code with
    the parser under test. Brackets are added only where precedence needs
    them, plus some redundant ones, so precedence is actually exercised.
    """
    if depth == 0 or rng.random() < 0.3:
        n = rng.randint(0, 30)
        return str(n), n, 9
    if "u" in ops and rng.random() < 0.15:
        s, v, p = random_expr(rng, depth - 1, ops)
        return "-" + (s if p == 9 else f"({s})"), -v, 3
    op = rng.choice([o for o in ops if o != "u"])
    ls, lv, lp = random_expr(rng, depth - 1, ops)
    rs, rv, rp = random_expr(rng, depth - 1, ops)
    if op == "/" and rv == 0:
        op = "+"
    p = PREC[op]
    if lp < p or rng.random() < 0.1:
        ls = f"({ls})"
    if rp < p or (rp == p and op != "+") or rs[0] == "-" or rng.random() < 0.1:
        rs = f"({rs})"
    sep = rng.choice(["", " "])
    return f"{ls}{sep}{op}{sep}{rs}", apply(op, lv, rv), p


def test_trunc_div():
    assert trunc_div(7, 2) == 3
    assert trunc_div(-7, 2) == -3
    assert trunc_div(7, -2) == -3
    assert trunc_div(-7, -2) == 3
    assert -7 // 2 == -4  # the trap trunc_div avoids


def test_eval_rpn_examples():
    assert eval_rpn(["2", "1", "+", "3", "*"]) == 9
    assert eval_rpn(["4", "13", "5", "/", "+"]) == 6
    assert eval_rpn(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]) == 22


def test_calculate_examples():
    assert calculate("3+2*2") == 7
    assert calculate(" 3/2 ") == 1
    assert calculate("(1+(4+5+2)-3)+(6+8)") == 23
    assert calculate("(5-8)/2") == -1        # -3/2 truncates to -1
    assert calculate("2*(5-8)/4") == -1      # left to right: -6/4
    assert calculate("-3*4") == -12
    assert calculate("2*-3") == -6
    assert calculate("-(2+3)") == -5
    assert calculate("14-3/2") == 13


def test_calculate_matches_expression_trees():
    import random

    rng = random.Random(11)
    for _ in range(3000):
        s, v, _ = random_expr(rng, 4, ["+", "-", "*", "/", "u"])
        assert calculate(s) == v, s


def test_to_rpn_round_trips_through_eval_rpn():
    import random

    rng = random.Random(12)
    assert to_rpn("3+4*2") == ["3", "4", "2", "*", "+"]
    assert to_rpn("8-3-2") == ["8", "3", "-", "2", "-"]  # left-associative
    for _ in range(2000):
        s, v, _ = random_expr(rng, 4, ["+", "-", "*", "/", "u"])
        assert eval_rpn(to_rpn(s)) == v, s


def test_add_sub_calculator():
    import random

    assert calculate_add_sub("1 + 1") == 2
    assert calculate_add_sub(" 2-1 + 2 ") == 3
    assert calculate_add_sub("(1+(4+5+2)-3)+(6+8)") == 23
    assert calculate_add_sub("-(2+3)") == -5
    assert calculate_add_sub("1-(-2)") == 3
    rng = random.Random(13)
    for _ in range(2000):
        s, v, _ = random_expr(rng, 5, ["+", "-", "u"])
        assert calculate_add_sub(s) == v == calculate(s), s


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
