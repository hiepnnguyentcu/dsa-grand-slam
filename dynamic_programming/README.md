# Dynamic Programming

One file per technique family: implementation + tests, checked against brute force.

```
python3 dynamic_programming/knapsack.py                                   # one file
for f in dynamic_programming/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| No two adjacent, stairs, delete-and-earn | [linear_dp.py](linear_dp.py) |
| Decode ways, word break | [string_segmentation.py](string_segmentation.py) |
| Budget, subset sum, ±target, coin change | [knapsack.py](knapsack.py) |
| Longest increasing chain, envelopes | [lis.py](lis.py) |
| Two strings: LCS, edit distance, interleave | [two_sequence.py](two_sequence.py) |
| Wildcard `?*`, regex `.*` | [pattern_matching.py](pattern_matching.py) |
| Right/down grid paths, squares, dungeon | [grid_dp.py](grid_dp.py) |
| Any-direction moves with a strict order | [memo_dfs.py](memo_dfs.py) |
| Palindromic subsequence, min cuts | [palindrome_dp.py](palindrome_dp.py) |
| Split a segment: balloons, sticks, stones | [interval_dp.py](interval_dp.py) |
| Two players, optimal play | [game_dp.py](game_dp.py) |
| Modes over time: stocks, paint house | [state_machine.py](state_machine.py) |
| n ≤ 20, subsets: TSP, team, assignment | [bitmask_dp.py](bitmask_dp.py) |
| Choices on a tree, answer for every root | [tree_dp.py](tree_dp.py) |
| Count numbers ≤ N with a digit property | [digit_dp.py](digit_dp.py) |
| Count mod 10⁹+7, Catalan shapes | [counting_dp.py](counting_dp.py) |
| `dp[i] = a[i] + max(dp[i-k..i-1])` | [deque_optimization.py](deque_optimization.py) |

## Framework

1. **State** in one sentence: "dp[i] = best answer for the first i items".
2. **Transition**: look at the last decision that reaches the state.
3. **Base cases**: empty prefix, zero capacity, single element.
4. **Order**: dependencies first, or memoise top-down.
5. **Answer**: which state(s) hold it.
6. **Space**: keep only the rows the transition reads.

Cost is states × transitions per state. Start top-down with `@cache` for correctness; convert to bottom-up when recursion depth or speed matters.

## DP, greedy or backtracking?

| Need | Use |
|---|---|
| Every solution listed | Backtracking |
| A count or optimum, subproblems repeat | DP |
| A local choice provably safe (exchange argument) | Greedy |
| n ≤ 20 with subset state | Bitmask DP |
| Few distinct values, many items | Knapsack over values |
