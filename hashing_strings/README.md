# Hashing & Strings

One file per technique family: implementation + tests, checked against brute force.

```
python3 hashing_strings/hash_lookup.py                                   # one file
for f in hashing_strings/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Two sum (unsorted), pair counts, duplicates within k, first unique, isomorphic, word pattern | [hash_lookup.py](hash_lookup.py) |
| Anagram, ransom note, group anagrams/shifts, duplicates in 1..n by marking | [frequency_signatures.py](frequency_signatures.py) |
| Longest consecutive in O(n), first missing positive, valid sudoku, seen-set cycles | [set_sequences.py](set_sequences.py) |
| Majority > n/2 or > n/3 in O(1) space (Boyer–Moore) | [majority_vote.py](majority_vote.py) |
| Reverse words, compression, encode/decode list, longest common prefix, zigzag | [string_building.py](string_building.py) |
| Longest palindromic substring, count palindromic substrings | [expand_centre.py](expand_centre.py) |
| strStr, repeated DNA, longest duplicate substring, repeated block, shortest palindrome | [string_matching.py](string_matching.py) |

Substring windows: [sliding_window/](../sliding_window/README.md). Subarray sum = k: [prefix_hashmap.py](../prefix_sums/prefix_hashmap.py). Roman, atoi: [math_algorithms/](../math_algorithms/README.md). Top-k frequent: [top_k.py](../stacks_heaps/top_k.py). Palindrome subsequences: [palindrome_dp.py](../dynamic_programming/palindrome_dp.py).

**Conventions:** "not found" is `-1`, `None` or `[]`; grouping returns lists in any order; lowercase `a`–`z` unless noted.
