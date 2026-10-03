# Intervals

One file per technique family: implementation + tests, checked against brute force. Explanations: [Intervals — Field Guide](https://claude.ai/code/artifact/ab0092c5-d68f-448a-bb91-35f81464dee2).

```
python3 intervals/merging.py                                   # one file
for f in intervals/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Merge overlapping, insert into sorted, summary/missing ranges, partition labels | [merging.py](merging.py) |
| Can attend all, max meetings, min removals, min arrows | [overlap_greedy.py](overlap_greedy.py) |
| Min rooms (two sorted arrays), busiest time, employee free time, skyline | [sweep_line.py](sweep_line.py) |
| Online bookings: My Calendar I / II / III | [booking.py](booking.py) |
| Add/remove/query ranges, stream as disjoint intervals | [interval_set.py](interval_set.py) |
| Covered intervals, count intervals per point, smallest interval per query | [relations.py](relations.py) |

Rooms with a heap: [stacks_heaps/heap_scheduling.py](../stacks_heaps/heap_scheduling.py). Interval list intersections: [sliding_window/merge_two.py](../sliding_window/merge_two.py). Car pooling, overlap via difference array: [prefix_sums/difference_array.py](../prefix_sums/difference_array.py).

**Conventions:** intervals are `[s, e]` lists; closed `[s, e]` for merging, arrows and point queries (touching merges); half-open `[s, e)` for meetings, bookings and Range Module (touching is fine).
