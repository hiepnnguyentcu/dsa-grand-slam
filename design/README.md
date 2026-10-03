# Data Structure Design

One file per technique family: implementation + tests, checked against naive references.

```
python3 design/caches.py                                            # one file
for f in design/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| LRU / LFU cache, O(1) get/put | [caches.py](caches.py) |
| Insert/delete/getRandom O(1), with duplicates | [randomized_set.py](randomized_set.py) |
| HashMap/HashSet from scratch, load factor | [hash_table.py](hash_table.py) |
| Value at time t, snapshots, corrected prices, rate limiter | [time_based.py](time_based.py) |
| Peeking, nested list, zigzag, 2D iterators | [iterators.py](iterators.py) |
| Max/min-count key O(1), leaderboard, average trip time | [rankings.py](rankings.py) |
| Twitter feed, browser history, file system, tic-tac-toe | [mini_systems.py](mini_systems.py) |

Elsewhere: min/freq stack [stack_design.py](../stacks_heaps/stack_design.py), circular queue + hit counter [queue_design.py](../stacks_heaps/queue_design.py), median finder [two_heaps.py](../stacks_heaps/two_heaps.py), BST iterator [kth_and_iterator.py](../binary_search_trees/kth_and_iterator.py), trie [tries/](../tries/).

**Conventions:** LeetCode APIs in snake_case; missing is `-1` (ints) or `""` (strings); random tests use fixed seeds.
