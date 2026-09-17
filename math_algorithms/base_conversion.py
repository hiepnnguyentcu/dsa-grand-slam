"""Base conversion — base k, negative base, Excel columns, Roman numerals, words.

Signs: "convert to base 7 / hex / base -2", spreadsheet column titles,
       Roman numerals, "integer to English words".
Approach: repeated divmod peels the lowest digit each step; reverse at the end.
  - Bijective alphabets (A = 1 ... Z = 26, no zero digit): subtract 1 before
    each divmod so the digits run 0..25.
  - Negative base: divmod still works, but a negative remainder must be
    lifted into [0, |k|) by borrowing one from the quotient.
  - Roman numerals and English words: greedy over a descending value table.
    Adding the subtractive pairs (900 CM, 40 XL, ...) is what makes greedy
    correct.
Complexity: O(log_k n) digits.
Gotchas:
  - n == 0 is "0", not the empty string (but Excel and Roman have no zero).
  - Handle the sign separately for positive bases; do not divmod a negative n.
  - "Excel = base 26" is wrong: Z is 26 and AA is 27; there is no zero digit.
  - Words: groups of three, and skip empty groups ("One Million" not
    "One Million Zero Thousand").

Run the tests at the bottom with:  python3 math_algorithms/base_conversion.py
"""

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ---------------------------------------------------------------- implementation


def to_base(n, k):
    """n in base 2 <= k <= 36, with a leading '-' for negatives."""
    if not 2 <= k <= 36:
        raise ValueError("base must be in 2..36")
    if n == 0:
        return "0"
    neg, n, digits = n < 0, abs(n), []
    while n:
        n, d = divmod(n, k)
        digits.append(DIGITS[d])
    return ("-" if neg else "") + "".join(reversed(digits))


def from_base(s, k):
    """Inverse of to_base. Horner's rule: value = value * k + digit."""
    s = s.strip()
    neg = s.startswith("-")
    if neg or s.startswith("+"):
        s = s[1:]
    if not s:
        raise ValueError("empty number")
    value = 0
    for ch in s.upper():
        d = DIGITS.find(ch)
        if not 0 <= d < k:
            raise ValueError(f"invalid digit {ch!r} for base {k}")
        value = value * k + d
    return -value if neg else value


def to_negative_base(n, k=-2):
    """n in base k <= -2. Every integer has a sign-free representation."""
    if n == 0:
        return "0"
    digits = []
    while n:
        n, d = divmod(n, k)  # Python: d is in (k, 0], i.e. <= 0
        if d < 0:
            d -= k  # d + |k| is in [0, |k|)
            n += 1  # and the quotient absorbs the borrow
        digits.append(DIGITS[d])
    return "".join(reversed(digits))


def excel_title(n):
    """1 -> A, 26 -> Z, 27 -> AA."""
    if n < 1:
        raise ValueError("columns start at 1")
    out = []
    while n:
        n, r = divmod(n - 1, 26)
        out.append(chr(65 + r))
    return "".join(reversed(out))


def excel_number(title):
    n = 0
    for ch in title:
        n = n * 26 + (ord(ch) - 64)  # A = 1, no zero digit
    return n


ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
         (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def to_roman(num):
    if not 1 <= num <= 3999:
        raise ValueError("Roman numerals cover 1..3999")
    out = []
    for v, s in ROMAN:
        q, num = divmod(num, v)
        out.append(s * q)
    return "".join(out)


def from_roman(s):
    """A symbol smaller than its right neighbour is subtracted (IV, XC)."""
    val = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        v = val[ch]
        if i + 1 < len(s) and v < val[s[i + 1]]:
            total -= v
        else:
            total += v
    return total


_ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
         "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
         "Seventeen", "Eighteen", "Nineteen"]
_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
_SCALES = ["", "Thousand", "Million", "Billion", "Trillion"]


def number_to_words(num):
    """0 <= num < 10^15 in English (LeetCode 273 style)."""
    if num == 0:
        return "Zero"

    def below_1000(n):
        words = []
        if n >= 100:
            words += [_ONES[n // 100], "Hundred"]
            n %= 100
        if n >= 20:
            words.append(_TENS[n // 10])
            n %= 10
        if n:
            words.append(_ONES[n])
        return words

    words, scale = [], 0
    while num:
        num, group = divmod(num, 1000)
        if group:  # skip empty groups: no "Zero Thousand"
            words = below_1000(group) + ([_SCALES[scale]] if scale else []) + words
        scale += 1
    return " ".join(words)


# ------------------------------------------------------------------------ tests


def test_to_base_matches_int_parsing():
    import random

    rng = random.Random(26)
    values = [0, 1, -1, 35, 36, -36] + [rng.randint(-(10**50), 10**50) for _ in range(500)]
    for n in values:
        for k in range(2, 37):
            s = to_base(n, k)
            assert int(s, k) == n
            assert from_base(s, k) == n
    assert to_base(255, 16) == "FF"
    assert to_base(100, 7) == "202"
    assert to_base(-7, 7) == "-10"
    assert to_base(0, 2) == "0"


def test_to_base_matches_builtin_formatters():
    import random

    rng = random.Random(27)
    for n in [0, 1, -1] + [rng.randint(-(10**30), 10**30) for _ in range(500)]:
        assert to_base(n, 2) == format(n, "b")
        assert to_base(n, 8) == format(n, "o")
        assert to_base(n, 16) == format(n, "X")


def test_from_base_rejects_bad_digits():
    for s, k in [("2", 2), ("G", 16), ("", 10), ("-", 10), ("1.5", 10)]:
        try:
            from_base(s, k)
        except ValueError:
            pass
        else:
            raise AssertionError((s, k))
    assert from_base("ff", 16) == 255


def test_negative_base():
    for k in (-2, -3, -10, -16):
        for n in range(-2000, 2001):
            s = to_negative_base(n, k)
            assert "-" not in s
            assert s == "0" or s[0] != "0"
            value = sum(DIGITS.index(ch) * k**i for i, ch in enumerate(reversed(s)))
            assert value == n, (n, k, s)
    assert to_negative_base(2) == "110"  # 4 - 2 + 0
    assert to_negative_base(3) == "111"  # 4 - 2 + 1


def test_excel_titles():
    assert [excel_title(n) for n in (1, 26, 27, 28, 52, 53, 701, 702, 703, 16384)] == \
        ["A", "Z", "AA", "AB", "AZ", "BA", "ZY", "ZZ", "AAA", "XFD"]
    # every title of length 1..3, in order, is the next column number
    from itertools import product
    from string import ascii_uppercase

    n = 0
    for length in (1, 2, 3):
        for letters in product(ascii_uppercase, repeat=length):
            n += 1
            assert excel_title(n) == "".join(letters)
            assert excel_number("".join(letters)) == n
    for n in (1, 10**6, 2**31 - 1, 10**20):
        assert excel_number(excel_title(n)) == n


def test_roman_round_trip_and_independent_table():
    th = ["", "M", "MM", "MMM"]
    hu = ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"]
    te = ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"]
    on = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
    for n in range(1, 4000):
        expected = th[n // 1000] + hu[n // 100 % 10] + te[n // 10 % 10] + on[n % 10]
        assert to_roman(n) == expected
        assert from_roman(expected) == n
    assert to_roman(1994) == "MCMXCIV"
    assert to_roman(3999) == "MMMCMXCIX"
    for bad in (0, 4000, -1):
        try:
            to_roman(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(bad)


def test_number_to_words_examples():
    assert number_to_words(0) == "Zero"
    assert number_to_words(5) == "Five"
    assert number_to_words(13) == "Thirteen"
    assert number_to_words(20) == "Twenty"
    assert number_to_words(100) == "One Hundred"
    assert number_to_words(123) == "One Hundred Twenty Three"
    assert number_to_words(12345) == "Twelve Thousand Three Hundred Forty Five"
    assert number_to_words(1_000_000) == "One Million"
    assert number_to_words(1_000_010) == "One Million Ten"
    assert number_to_words(1_234_567) == \
        "One Million Two Hundred Thirty Four Thousand Five Hundred Sixty Seven"
    assert number_to_words(2**31 - 1) == ("Two Billion One Hundred Forty Seven Million "
                                          "Four Hundred Eighty Three Thousand "
                                          "Six Hundred Forty Seven")


def test_number_to_words_parses_back():
    # An independent parser: accumulate within a group, flush on a scale word.
    import random

    small = {w: i for i, w in enumerate(_ONES) if w}
    small.update({w: 10 * i for i, w in enumerate(_TENS) if w})
    scales = {"Thousand": 10**3, "Million": 10**6, "Billion": 10**9, "Trillion": 10**12}

    def parse(text):
        total = group = 0
        for w in text.split(" "):
            if w in small:
                group += small[w]
            elif w == "Hundred":
                group *= 100
            else:
                total += group * scales[w]
                group = 0
        return total + group

    rng = random.Random(28)
    values = list(range(1, 2100)) + [rng.randint(1, 10**15 - 1) for _ in range(3000)]
    values += [10**k for k in range(15)] + [10**k + 1 for k in range(15)]
    for n in values:
        text = number_to_words(n)
        assert "  " not in text and text == text.strip()
        assert parse(text) == n, (n, text)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
