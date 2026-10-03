"""Greedy monotonic stack — the lexicographically smallest subsequence.

Signs: "remove k digits to make the smallest number", "smallest subsequence
       containing each distinct letter once", "most competitive subsequence of
       length k".
Approach: build the answer left to right on a stack. While the top is larger
          than the incoming item *and you can still afford to drop it*, pop
          it: a smaller value earlier always beats anything that follows.
          "Afford" is the problem-specific part — removals left, enough items
          remaining, or the letter appears again later.
Complexity: O(n) time and space; each item is pushed and popped once.
Gotchas:
  - Remove k digits: if k removals are left at the end, cut from the tail
    (the stack is non-decreasing, so the tail is largest). Strip leading
    zeros; an empty result is "0".
  - Distinct letters: skip a letter already on the stack, and only pop a top
    that occurs again later.
  - Length k: pop only while len(stack) - 1 + remaining >= k.

Run the tests at the bottom with:  python3 stacks_heaps/monotonic_greedy.py
"""


# ---------------------------------------------------------------- implementation


def remove_k_digits(num, k):
    """Smallest number (as a string) after deleting k digits from num."""
    stack = []
    for d in num:
        while k and stack and stack[-1] > d:
            stack.pop()
            k -= 1
        stack.append(d)
    if k:
        stack = stack[:-k]
    return "".join(stack).lstrip("0") or "0"


def smallest_distinct_subsequence(s):
    """Smallest subsequence containing every distinct letter of s exactly once.

    (LeetCode 316 / 1081 — "remove duplicate letters".)
    """
    last = {ch: i for i, ch in enumerate(s)}
    stack, on_stack = [], set()
    for i, ch in enumerate(s):
        if ch in on_stack:
            continue
        while stack and stack[-1] > ch and last[stack[-1]] > i:
            on_stack.discard(stack.pop())  # it comes back later, so drop it now
        stack.append(ch)
        on_stack.add(ch)
    return "".join(stack)


def most_competitive(nums, k):
    """Lexicographically smallest subsequence of length k."""
    stack = []
    n = len(nums)
    for i, x in enumerate(nums):
        while stack and stack[-1] > x and len(stack) - 1 + (n - i) >= k:
            stack.pop()
        if len(stack) < k:
            stack.append(x)
    return stack


# ------------------------------------------------------------------------ tests


def test_remove_k_digits_examples():
    assert remove_k_digits("1432219", 3) == "1219"
    assert remove_k_digits("10200", 1) == "200"
    assert remove_k_digits("10", 2) == "0"
    assert remove_k_digits("12345", 2) == "123"  # nothing popped: cut the tail


def test_remove_k_digits_matches_brute_force():
    import random
    from itertools import combinations

    rng = random.Random(1)
    for _ in range(600):
        num = "".join(rng.choice("0123") for _ in range(rng.randint(1, 8)))
        k = rng.randint(0, len(num))
        brute = min(
            (int("".join(num[i] for i in keep) or "0") for keep in combinations(range(len(num)), len(num) - k)),
        )
        assert remove_k_digits(num, k) == str(brute), (num, k)


def test_smallest_distinct_subsequence():
    import random
    from itertools import combinations

    assert smallest_distinct_subsequence("bcabc") == "abc"
    assert smallest_distinct_subsequence("cbacdcbc") == "acdb"
    rng = random.Random(2)
    for _ in range(500):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(1, 9)))
        d = len(set(s))
        brute = min(
            t
            for t in ("".join(s[i] for i in idx) for idx in combinations(range(len(s)), d))
            if len(set(t)) == d
        )
        assert smallest_distinct_subsequence(s) == brute, s


def test_most_competitive():
    import random
    from itertools import combinations

    assert most_competitive([3, 5, 2, 6], 2) == [2, 6]
    assert most_competitive([2, 4, 3, 3, 5, 4, 9, 6], 4) == [2, 3, 3, 4]
    rng = random.Random(3)
    for _ in range(500):
        nums = [rng.randint(0, 4) for _ in range(rng.randint(1, 9))]
        k = rng.randint(1, len(nums))
        assert most_competitive(nums, k) == min(list(c) for c in combinations(nums, k)), (nums, k)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
