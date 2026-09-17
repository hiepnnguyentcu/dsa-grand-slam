"""Big-number string arithmetic — add, subtract, multiply digit strings.

Signs: "numbers are given as strings", "do not convert to int / use BigInteger",
       values beyond 64 bits in languages without big ints, add binary strings.
Approach: grade-school arithmetic on digit arrays, least significant first.
  - Add: walk both from the right with a carry; stop when both are exhausted
    *and* the carry is 0.
  - Subtract: compare magnitudes, subtract the smaller from the larger with a
    borrow, and put the sign in front.
  - Multiply: digit i of a (from the left) times digit j of b lands in slot
    i + j + 1 of an array of len(a) + len(b) slots; its carry goes to i + j.
Complexity: add/subtract O(m + n); multiply O(m * n).
Gotchas:
  - Strip leading zeros from the result, but keep a single "0".
  - Do not forget the final carry ("999" + "1").
  - "Compare magnitudes" means length first, then lexicographic — only valid
    once leading zeros are gone.
  - In multiply, a slot can briefly exceed 9; it is normalised when its own
    column is processed, and the top slot can never overflow because the
    product has at most m + n digits.

Run the tests at the bottom with:  python3 math_algorithms/big_number_strings.py
"""


# ---------------------------------------------------------------- implementation


def _strip(s):
    return s.lstrip("0") or "0"


def add_strings(a, b, base=10):
    """Sum of two non-negative numbers given as digit strings (base <= 10)."""
    i, j, carry, out = len(a) - 1, len(b) - 1, 0, []
    while i >= 0 or j >= 0 or carry:
        s = carry
        if i >= 0:
            s += ord(a[i]) - 48
            i -= 1
        if j >= 0:
            s += ord(b[j]) - 48
            j -= 1
        carry, d = divmod(s, base)
        out.append(chr(48 + d))
    return _strip("".join(reversed(out)))


def add_binary(a, b):
    return add_strings(a, b, base=2)


def compare_magnitude(a, b):
    """-1, 0 or 1 comparing two non-negative digit strings."""
    a, b = _strip(a), _strip(b)
    if len(a) != len(b):
        return -1 if len(a) < len(b) else 1
    return (a > b) - (a < b)  # same length: lexicographic == numeric


def subtract_strings(a, b):
    """a - b for non-negative digit strings; result may start with '-'."""
    a, b = _strip(a), _strip(b)
    cmp = compare_magnitude(a, b)
    if cmp == 0:
        return "0"
    if cmp < 0:
        return "-" + subtract_strings(b, a)
    i, j, borrow, out = len(a) - 1, len(b) - 1, 0, []
    while i >= 0:
        d = (ord(a[i]) - 48) - borrow - (ord(b[j]) - 48 if j >= 0 else 0)
        borrow = 1 if d < 0 else 0
        out.append(chr(48 + d + 10 * borrow))
        i, j = i - 1, j - 1
    return _strip("".join(reversed(out)))


def multiply_strings(a, b):
    """Product of two integers given as strings; each may have a leading '-'."""
    neg = (a[:1] == "-") != (b[:1] == "-")
    a, b = a.lstrip("+-"), b.lstrip("+-")
    res = [0] * (len(a) + len(b))
    for i in range(len(a) - 1, -1, -1):
        da = ord(a[i]) - 48
        for j in range(len(b) - 1, -1, -1):
            p = da * (ord(b[j]) - 48) + res[i + j + 1]
            res[i + j + 1] = p % 10
            res[i + j] += p // 10
    s = _strip("".join(map(str, res)))
    return "-" + s if neg and s != "0" else s


# ------------------------------------------------------------------------ tests


def _rand_num(rng, max_digits=60):
    return rng.randint(0, 10 ** rng.randint(0, max_digits))


def test_add_against_python_ints():
    import random

    rng = random.Random(29)
    for _ in range(3000):
        x, y = _rand_num(rng), _rand_num(rng)
        assert add_strings(str(x), str(y)) == str(x + y)
    assert add_strings("999", "1") == "1000"  # final carry
    assert add_strings("0", "0") == "0"
    assert add_strings("11", "123") == "134"
    assert add_strings("007", "0003") == "10"  # leading zeros stripped


def test_add_binary():
    import random

    rng = random.Random(30)
    for _ in range(2000):
        x, y = rng.getrandbits(rng.randint(1, 200)), rng.getrandbits(rng.randint(1, 200))
        assert add_binary(bin(x)[2:], bin(y)[2:]) == bin(x + y)[2:]
    assert add_binary("1010", "1011") == "10101"
    assert add_binary("0", "0") == "0"


def test_other_small_bases():
    import random

    rng = random.Random(31)
    for _ in range(500):
        base = rng.randint(2, 10)
        x, y = rng.getrandbits(100), rng.getrandbits(100)

        def enc(n):
            s = ""
            while n:
                n, d = divmod(n, base)
                s = str(d) + s
            return s or "0"

        assert int(add_strings(enc(x), enc(y), base), base) == x + y


def test_compare_magnitude():
    import random

    rng = random.Random(32)
    for _ in range(3000):
        x, y = _rand_num(rng, 5), _rand_num(rng, 5)
        pad_x = "0" * rng.randint(0, 3) + str(x)
        assert compare_magnitude(pad_x, str(y)) == (x > y) - (x < y)
    assert compare_magnitude("9", "10") == -1  # plain string compare says "9" > "10"


def test_subtract_against_python_ints():
    import random

    rng = random.Random(33)
    for _ in range(3000):
        x, y = _rand_num(rng), _rand_num(rng)
        assert subtract_strings(str(x), str(y)) == str(x - y)
    assert subtract_strings("1000", "1") == "999"
    assert subtract_strings("1", "1000") == "-999"
    assert subtract_strings("5", "5") == "0"
    assert subtract_strings("100000000000000000000", "99999999999999999999") == "1"


def test_multiply_against_python_ints():
    import random

    rng = random.Random(34)
    for _ in range(1500):
        x, y = _rand_num(rng, 80), _rand_num(rng, 80)
        if rng.random() < 0.3:
            x = -x
        if rng.random() < 0.3:
            y = -y
        assert multiply_strings(str(x), str(y)) == str(x * y)
    assert multiply_strings("123", "456") == "56088"
    assert multiply_strings("0", "987654321") == "0"
    assert multiply_strings("-0", "5") == "0"  # no "-0"
    assert multiply_strings("9" * 50, "9" * 50) == str((10**50 - 1) ** 2)


def test_multiply_many_digits():
    x, y = 7**400, 3**500  # hundreds of digits each
    assert multiply_strings(str(x), str(y)) == str(x * y)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
