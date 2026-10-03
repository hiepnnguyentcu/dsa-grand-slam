# Linked Lists

One file per technique family: implementation + tests, checked against Python lists and node identity.

```
python3 linked_lists/reversal.py                                   # one file
for f in linked_lists/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Head might be deleted: remove value, sorted dedupe I/II, partition, delete given node | [dummy_head.py](dummy_head.py) |
| Reverse all / m..n / k-groups, swap pairs, palindrome in O(1) space | [reversal.py](reversal.py) |
| Reorder L0→Ln→L1, odd-even, rotate, split into k parts | [reordering.py](reordering.py) |
| Merge two / k sorted, sort list O(n log n), insertion sort | [merge_sort.py](merge_sort.py) |
| Digit lists: add I/II, plus one, double | [arithmetic.py](arithmetic.py) |
| Copy list with random pointer, flatten multilevel list | [extra_pointers.py](extra_pointers.py) |
| Y-shaped lists: first shared node | [intersection.py](intersection.py) |
| Shared `ListNode`, `from_list` / `to_list`, generators | [ll.py](ll.py) |

**Conventions:** lists are Python lists in tests (`from_list` / `to_list` in ll.py); cycle, middle, n-th from end → [sliding_window/fast_slow.py](../sliding_window/fast_slow.py); heap merge k → [stacks_heaps/k_way_merge.py](../stacks_heaps/k_way_merge.py); LRU cache → design/.
