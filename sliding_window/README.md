# Sliding Window & Two Pointers

One file per technique family: implementation + tests, checked against brute force.

```
python3 sliding_window/longest_window.py                                 # one file
for f in sliding_window/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Sorted pair/triplet sums, 3sum/4sum, container, palindrome, sorted squares | [opposite_ends.py](opposite_ends.py) |
| In place: remove, dedupe, move zeroes, Dutch flag | [read_write.py](read_write.py) |
| Linked-list cycle + entry, middle, n-th from end, happy number, duplicate | [fast_slow.py](fast_slow.py) |
| Two sorted sequences: merge, intersect, subsequence, interval overlap | [merge_two.py](merge_two.py) |
| Every window of length k: average, vowels, anagrams | [fixed_window.py](fixed_window.py) |
| Longest valid: no repeats, ≤ k distinct, replacements, flips | [longest_window.py](longest_window.py) |
| Shortest valid: min subarray sum, minimum window substring | [shortest_window.py](shortest_window.py) |
| Count subarrays: product < k, exactly k = atMost(k) − atMost(k−1), negatives → prefix sums | [counting.py](counting.py) |

Window max/min, sum ≥ k with negatives: [stacks_heaps/monotonic_deque.py](../stacks_heaps/monotonic_deque.py). Trapping rain water: [stacks_heaps/histogram.py](../stacks_heaps/histogram.py).

**Conventions:** `left`/`right` inclusive, length `right - left + 1`; "none" is `0`, `""` or `[]`; windows need non-negative values unless noted.
