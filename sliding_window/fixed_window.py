"""Fixed-size sliding window — every window of length k in one pass.

Signs: "subarray / substring of length k", "every window of size k",
       "max average of k consecutive", "is some permutation of p a substring
       of s", "all anagram start indices".
Approach: build the first window, then slide: add a[i], remove a[i - k].
          Keep only what the question needs — a running sum, a count of
          matching chars, a frequency map — so each slide is O(1).
          Anagram check: keep `matched` = number of letters whose window count
          equals the target count; a window is an anagram when matched hits
          the alphabet size, no map comparison needed.
Complexity: O(n) time; O(1) or O(alphabet) space.
Gotchas:
  - Record the answer only once the window is full (i >= k - 1).
  - Remove the outgoing element BEFORE or AFTER adding — pick one and be
    consistent; off-by-one here is the usual bug.
  - Max/min of each window isn't a running sum: use a monotonic deque,
    stacks_heaps/monotonic_deque.py (max_sliding_window).
  - k > len(a): no window exists; decide what to return up front.

Run the tests at the bottom with:  python3 sliding_window/fixed_window.py
"""

from collections import Counter


# ---------------------------------------------------------------- implementation


def max_average(a, k):
    """LC 643. Max average of a length-k subarray (1 <= k <= len(a))."""
    s = sum(a[:k])
    best = s
    for i in range(k, len(a)):
        s += a[i] - a[i - k]
        best = max(best, s)
    return best / k


def max_vowels(s, k):
    """LC 1456. Most vowels in any length-k substring."""
    vowels = set("aeiou")
    cur = best = 0
    for i, c in enumerate(s):
        cur += c in vowels
        if i >= k:
            cur -= s[i - k] in vowels
        best = max(best, cur)
    return best


def find_anagrams(s, p):
    """LC 438. Start indices of every anagram of p in s."""
    k, need = len(p), Counter(p)
    window = Counter()
    matched = 0           # letters c with window[c] == need[c]
    out = []
    for i, c in enumerate(s):
        window[c] += 1
        if window[c] == need[c]:
            matched += 1
        elif window[c] == need[c] + 1:
            matched -= 1  # was exactly right, now one too many
        if i >= k:
            d = s[i - k]
            if window[d] == need[d]:
                matched -= 1
            elif window[d] == need[d] + 1:
                matched += 1
            window[d] -= 1
        if matched == len(need):
            out.append(i - k + 1)
    return out


def check_inclusion(p, s):
    """LC 567. Does s contain a permutation of p?"""
    return bool(find_anagrams(s, p))


def count_good_substrings(s, k=3):
    """LC 1876 (generalised): windows of length k with all-distinct chars."""
    window = Counter()
    count = 0
    for i, c in enumerate(s):
        window[c] += 1
        if i >= k:
            window[s[i - k]] -= 1
            if window[s[i - k]] == 0:
                del window[s[i - k]]
        if i >= k - 1 and len(window) == k:
            count += 1
    return count


# ------------------------------------------------------------------------ tests


def test_examples():
    assert max_average([1, 12, -5, -6, 50, 3], 4) == 12.75
    assert max_vowels("abciiidef", 3) == 3
    assert find_anagrams("cbaebabacd", "abc") == [0, 6]
    assert check_inclusion("ab", "eidbaooo") and not check_inclusion("ab", "eidboaoo")
    assert count_good_substrings("xyzzaz") == 1


def test_sum_windows_match_slicing():
    import random

    rng = random.Random(1)
    for _ in range(500):
        n = rng.randint(1, 15)
        a = [rng.randint(-10, 10) for _ in range(n)]
        k = rng.randint(1, n)
        assert max_average(a, k) == max(sum(a[i:i + k]) for i in range(n - k + 1)) / k
        s = "".join(rng.choice("abeiz") for _ in range(n))
        assert max_vowels(s, k) == max(sum(c in "aeiou" for c in s[i:i + k]) for i in range(n - k + 1))


def test_anagrams_match_sorted_slices():
    import random

    rng = random.Random(2)
    for _ in range(500):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 14)))
        p = "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
        k = len(p)
        brute = [i for i in range(len(s) - k + 1) if sorted(s[i:i + k]) == sorted(p)]
        assert find_anagrams(s, p) == brute
        assert check_inclusion(p, s) == bool(brute)


def test_distinct_windows_match_slicing():
    import random

    rng = random.Random(3)
    for _ in range(500):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 14)))
        k = rng.randint(1, 4)
        brute = sum(len(set(s[i:i + k])) == k for i in range(len(s) - k + 1))
        assert count_good_substrings(s, k) == brute


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
