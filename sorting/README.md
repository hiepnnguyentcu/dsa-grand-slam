# Sorting

One file per technique family: implementation + tests, checked against `sorted()` / brute force. Explanations: [Sorting — Field Guide](URL).

```
python3 sorting/comparison_sorts.py                                   # one file
for f in sorting/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Write a sort: insertion, merge (top-down/bottom-up), quick (Lomuto/Hoare/3-way) | [comparison_sorts.py](comparison_sorts.py) |
| Small int range, fixed-width keys, uniform floats: counting, radix, bucket | [linear_sorts.py](linear_sorts.py) |
| K-th element / median in O(n), k smallest, wiggle sort II | [selection.py](selection.py) |
| Count pairs i < j: inversions, smaller after self, reverse pairs, range sums | [merge_count.py](merge_count.py) |
| Multi-key, comparator, given order: largest number, logs, frequency | [custom_comparators.py](custom_comparators.py) |
| Sort then sweep: intervals, min difference, H-index, max gap, cookies | [sort_first.py](sort_first.py) |
| Values in 1..n, O(1) space: missing/duplicate, couples, min swaps | [cyclic_sort.py](cyclic_sort.py) |

**Conventions:** ascending; `key=` like `sorted()`; in-place functions also return the list; `k` is 1-based for "k-th largest", 0-based index for `quickselect`. Related: heap sort in [heap_basics.py](../stacks_heaps/heap_basics.py), top-k in [top_k.py](../stacks_heaps/top_k.py), BIT counting in [fenwick.py](../prefix_sums/fenwick.py), Dutch flag in [read_write.py](../sliding_window/read_write.py).
