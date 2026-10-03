# Prefix Sums

One file per technique family: implementation + tests, checked against brute force. Explanations: [Prefix Sums — Field Guide](https://claude.ai/code/artifact/211b38e1-3bc5-408e-9cf4-d0b8f81df2b9).

```
python3 prefix_sums/prefix_hashmap.py                                   # one file
for f in prefix_sums/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Static range sums, pivot index, split counts, window averages | [range_sum.py](range_sum.py) |
| Range XOR, counts in a range, product except self | [prefix_ops.py](prefix_ops.py) |
| Subarray sum = k (count/longest), 0/1 balance, divisible by k | [prefix_hashmap.py](prefix_hashmap.py) |
| Rectangle sums, submatrix sum = target, max rectangle ≤ k | [prefix_2d.py](prefix_2d.py) |
| Many range adds then read: car pooling, bookings, stamps | [difference_array.py](difference_array.py) |
| Best i < j, partition point, trapped water, two windows | [prefix_extremes.py](prefix_extremes.py) |
| Updates and range sums interleaved, count smaller after self | [fenwick.py](fenwick.py) |

**Conventions:** `p[i] = sum(a[:i])`, `p[0] = 0`, `len(p) = n + 1`; ranges `(l, r)` are 0-based inclusive, so `sum = p[r + 1] - p[l]`. Related: tree paths in [path_prefix_sum.py](../binary_trees/path_prefix_sum.py); shortest sum ≥ k in [monotonic_deque.py](../stacks_heaps/monotonic_deque.py).
