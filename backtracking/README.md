# Backtracking

One file per worksheet category: implementation + tests, checked against brute force or itertools. Explanations: [Backtracking — Field Guide](https://claude.ai/code/artifact/deaf2307-8090-42dc-978f-c09d79524758).

```
python3 backtracking/subsets.py                                   # one file
for f in backtracking/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

**The rule:** loop from start → start is a choice → `i+1` (or `i` for reuse); dedup `i > start`; no visited. Loop from 0 / no loop → start is a slot → `start+1`; dedup `visited[i-1]`; needs visited. Both: sort before dedup. State is a dict → undo with `del`.

| Situation | File |
|---|---|
| Subsets, with dups, non-decreasing subsequences, subset sums (78, 1863, 90, 491, 416, 2035) | [subsets.py](subsets.py) |
| Choose k, combination sum I/II/III/IV, missing binary string (77, 39, 40, 216, 377, 1980) | [combinations.py](combinations.py) |
| Permutations, with dups, tiles, palindromes, beautiful, squareful (46, 47, 1079, 267, 526, 996) | [permutations.py](permutations.py) |
| Next / prev / k-th permutation, rank (31, 556, 1053, 60) | [permutation_order.py](permutation_order.py) |
| k equal subsets, matchsticks, cookies, jobs, marbles (698, 473, 2305, 1723, 2551) | [bucket_filling.py](bucket_filling.py) |
| Palindrome partition, IP addresses, word break II (131, 93, 140) | [partitioning.py](partitioning.py) |
| Word search I/II, N-Queens, Sudoku, maze paths, paths III, DAG paths, flood fill, islands, gold (79, 212, 51, 52, 37, 63, 980, 797, 733, 200, 1219) | [grid_search.py](grid_search.py) |
| Parentheses, phone letters, add operators, target sum (22, 17, 282, 494) | [string_construction.py](string_construction.py) |
| Factor combinations, dice rolls (254, 1155) | [target_enumeration.py](target_enumeration.py) |
| Word pattern II, word pattern (291, 290) | [bijection.py](bijection.py) |
| Remove invalid parentheses (301) | [removal.py](removal.py) |

**Elsewhere:** 567/438 → [sliding_window/fixed_window.py](../sliding_window/fixed_window.py) · 765 → [sorting/cyclic_sort.py](../sorting/cyclic_sort.py) · 332 → [graphs/euler_path.py](../graphs/euler_path.py) · 402 → [stacks_heaps/monotonic_greedy.py](../stacks_heaps/monotonic_greedy.py) · 132 → [dynamic_programming/palindrome_dp.py](../dynamic_programming/palindrome_dp.py).

**Conventions:** `res = []`, `dfs(start, res, temp)`, `temp.append` / `dfs` / `temp.pop`, record `temp.copy()`; only a count or optimum needed → [dynamic_programming/](../dynamic_programming/).
