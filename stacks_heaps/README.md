# Stacks, Queues & Heaps

One file per technique family: implementation + tests, checked against brute force. Explanations: [Stacks, Queues & Heaps — Field Guide](https://claude.ai/code/artifact/0bf44f3c-1be4-40ac-89ea-cb4aadf55644).

```
python3 stacks_heaps/monotonic_stack.py                                   # one file
for f in stacks_heaps/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Valid brackets, min fixes, longest valid | [bracket_matching.py](bracket_matching.py) |
| RPN, calculator with precedence and parens | [expression_eval.py](expression_eval.py) |
| Next greater/smaller, warmer day, span, sum of mins | [monotonic_stack.py](monotonic_stack.py) |
| Largest rectangle, maximal rectangle, rain water | [histogram.py](histogram.py) |
| Smallest number/subsequence after removals | [monotonic_greedy.py](monotonic_greedy.py) |
| Asteroids, decode `3[a]`, simplify path, call logs | [stack_simulation.py](stack_simulation.py) |
| Min stack, queue via stacks, freq stack | [stack_design.py](stack_design.py) |
| Circular queue/deque, last-N-ms counter, moving average | [queue_design.py](queue_design.py) |
| Window max, max − min ≤ limit, shortest sum ≥ k | [monotonic_deque.py](monotonic_deque.py) |
| Ticket line, senate rounds, reveal cards, Josephus | [queue_simulation.py](queue_simulation.py) |
| heapq idioms, max-heap, tiebreakers, own heap | [heap_basics.py](heap_basics.py) |
| k largest, kth largest, k frequent, k closest | [top_k.py](top_k.py) |
| k sorted lists, sorted matrix, smallest range | [k_way_merge.py](k_way_merge.py) |
| Running median, IPO | [two_heaps.py](two_heaps.py) |
| Delete from a heap, sliding median | [lazy_deletion.py](lazy_deletion.py) |
| Meeting rooms, task cooldown, reorganise, CPU | [heap_scheduling.py](heap_scheduling.py) |

**Conventions:** queues are `collections.deque`; stacks hold indices, not values; heaps are `heapq` min-heaps (negate for max); ints divide toward zero.
