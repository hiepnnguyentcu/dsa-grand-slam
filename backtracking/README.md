# Backtracking

One file per technique family: implementation + tests, checked against brute force or itertools. Explanations: [Backtracking — Field Guide](https://claude.ai/code/artifact/deaf2307-8090-42dc-978f-c09d79524758).

```
python3 backtracking/subsets.py                                   # one file
for f in backtracking/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Choose / explore / unchoose, all paths | [template.py](template.py) |
| All subsets, with duplicates | [subsets.py](subsets.py) |
| All orderings, with duplicates | [permutations.py](permutations.py) |
| Choose k, combination sum I/II/III | [combinations.py](combinations.py) |
| Palindrome cuts, IP addresses, unique split | [partitioning.py](partitioning.py) |
| Parentheses, phone letters, add operators | [string_generation.py](string_generation.py) |
| N-Queens, Sudoku | [constraint_placement.py](constraint_placement.py) |
| Word search, word search II (trie) | [grid_search.py](grid_search.py) |
| Too slow: k equal subsets, matchsticks | [pruning.py](pruning.py) |

**Conventions:** results are lists of lists (or strings); one shared `path`, copied on record; only a count or optimum needed → [dynamic_programming/](../dynamic_programming/).
