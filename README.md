# DSA Grand Slam

One folder per theme, one file per technique: implementation + tests checked against brute force. Each theme has a Field Guide explaining every technique.

```
python3 graphs/dijkstra.py                                              # one file
for f in */*.py; do python3 "$f" >/dev/null || echo "FAIL $f"; done   # everything
```

| Theme | Techniques | Tests | Field Guide |
|---|---|---|---|
| [Hashing & Strings](hashing_strings/) | 7 | 36 | [Guide](https://claude.ai/code/artifact/124c1e02-f09b-486f-be10-642bb2d8b633) |
| [Sliding Window & Two Pointers](sliding_window/) | 8 | 39 | [Guide](https://claude.ai/code/artifact/b846811e-9a34-44cd-aa71-c52c9165fbd5) |
| [Prefix Sums](prefix_sums/) | 7 | 45 | [Guide](https://claude.ai/code/artifact/211b38e1-3bc5-408e-9cf4-d0b8f81df2b9) |
| [Sorting](sorting/) | 7 | 43 | [Guide](https://claude.ai/code/artifact/2e0eac46-fb1c-4e75-9131-77608d979ab9) |
| [Intervals](intervals/) | 6 | 22 | [Guide](https://claude.ai/code/artifact/ab0092c5-d68f-448a-bb91-35f81464dee2) |
| [Binary Search](binary_search/) | 9 | 44 | [Guide](https://claude.ai/code/artifact/1430adbb-6aca-4d1a-a6bc-df3d8e1a21b8) |
| [Linked Lists](linked_lists/) | 7 | 36 | [Guide](https://claude.ai/code/artifact/69ae0481-8f31-4207-b10e-69079321c7c9) |
| [Stacks, Queues & Heaps](stacks_heaps/) | 16 | 83 | [Guide](https://claude.ai/code/artifact/0bf44f3c-1be4-40ac-89ea-cb4aadf55644) |
| [Matrix & Simulation](matrix_simulation/) | 8 | 49 | [Guide](https://claude.ai/code/artifact/2fd43d5f-022c-42de-82bd-7011f5480229) |
| [Binary Trees](binary_trees/) | 16 | 118 | [Guide](https://claude.ai/code/artifact/e12df7b3-b5ea-4c4b-9b6f-df52cda45a62) |
| [Binary Search Trees](binary_search_trees/) | 11 | 42 | [Guide](https://claude.ai/code/artifact/ebf92a33-880b-482a-81fa-8ef77e334da4) |
| [Tries](tries/) | 7 | 34 | [Guide](https://claude.ai/code/artifact/b43a5a21-403d-4104-8ee9-c6eec0e3e3b0) |
| [Backtracking](backtracking/) | 11 | 53 | [Guide](https://claude.ai/code/artifact/deaf2307-8090-42dc-978f-c09d79524758) |
| [Greedy](greedy/) | 8 | 47 | [Guide](https://claude.ai/code/artifact/0274a374-e893-43e9-b66a-6e5b667cd5f7) |
| [Graphs](graphs/) | 22 | 218 | [Guide](https://claude.ai/code/artifact/ed02e36a-59a5-4346-8146-d43924037c92) |
| [Dynamic Programming](dynamic_programming/) | 17 | 103 | [Guide](https://claude.ai/code/artifact/c974221c-6651-4d95-a222-42471f92137e) |
| [Bit Manipulation](bit_manipulation/) | 6 | 40 | [Guide](https://claude.ai/code/artifact/bb26549a-f8af-477a-a29f-2073e4ead5c5) |
| [Math](math_algorithms/) | 14 | 113 | [Guide](https://claude.ai/code/artifact/4b1830c1-4c61-4508-8f97-25f8c017b5a5) |
| [Data Structure Design](design/) | 7 | 57 | [Guide](https://claude.ai/code/artifact/6529e231-921f-4ba9-a43d-5b226effeb91) |
| **Total** | **194** | **1222** | |

## By situation

<details><summary><b>Hashing & Strings</b></summary>

| Situation | File |
|---|---|
| Two sum (unsorted), pair counts, duplicates within k, first unique, isomorphic, word pattern | [hash_lookup.py](hashing_strings/hash_lookup.py) |
| Anagram, ransom note, group anagrams/shifts, duplicates in 1..n by marking | [frequency_signatures.py](hashing_strings/frequency_signatures.py) |
| Longest consecutive in O(n), first missing positive, valid sudoku, seen-set cycles | [set_sequences.py](hashing_strings/set_sequences.py) |
| Majority > n/2 or > n/3 in O(1) space (Boyer–Moore) | [majority_vote.py](hashing_strings/majority_vote.py) |
| Reverse words, compression, encode/decode list, longest common prefix, zigzag | [string_building.py](hashing_strings/string_building.py) |
| Longest palindromic substring, count palindromic substrings | [expand_centre.py](hashing_strings/expand_centre.py) |
| strStr, repeated DNA, longest duplicate substring, repeated block, shortest palindrome | [string_matching.py](hashing_strings/string_matching.py) |

</details>

<details><summary><b>Sliding Window & Two Pointers</b></summary>

| Situation | File |
|---|---|
| Sorted pair/triplet sums, 3sum/4sum, container, palindrome, sorted squares | [opposite_ends.py](sliding_window/opposite_ends.py) |
| In place: remove, dedupe, move zeroes, Dutch flag | [read_write.py](sliding_window/read_write.py) |
| Linked-list cycle + entry, middle, n-th from end, happy number, duplicate | [fast_slow.py](sliding_window/fast_slow.py) |
| Two sorted sequences: merge, intersect, subsequence, interval overlap | [merge_two.py](sliding_window/merge_two.py) |
| Every window of length k: average, vowels, anagrams | [fixed_window.py](sliding_window/fixed_window.py) |
| Longest valid: no repeats, ≤ k distinct, replacements, flips | [longest_window.py](sliding_window/longest_window.py) |
| Shortest valid: min subarray sum, minimum window substring | [shortest_window.py](sliding_window/shortest_window.py) |
| Count subarrays: product < k, exactly k = atMost(k) − atMost(k−1), negatives → prefix sums | [counting.py](sliding_window/counting.py) |

</details>

<details><summary><b>Prefix Sums</b></summary>

| Situation | File |
|---|---|
| Static range sums, pivot index, split counts, window averages | [range_sum.py](prefix_sums/range_sum.py) |
| Range XOR, counts in a range, product except self | [prefix_ops.py](prefix_sums/prefix_ops.py) |
| Subarray sum = k (count/longest), 0/1 balance, divisible by k | [prefix_hashmap.py](prefix_sums/prefix_hashmap.py) |
| Rectangle sums, submatrix sum = target, max rectangle ≤ k | [prefix_2d.py](prefix_sums/prefix_2d.py) |
| Many range adds then read: car pooling, bookings, stamps | [difference_array.py](prefix_sums/difference_array.py) |
| Best i < j, partition point, trapped water, two windows | [prefix_extremes.py](prefix_sums/prefix_extremes.py) |
| Updates and range sums interleaved, count smaller after self | [fenwick.py](prefix_sums/fenwick.py) |

</details>

<details><summary><b>Sorting</b></summary>

| Situation | File |
|---|---|
| Write a sort: insertion, merge (top-down/bottom-up), quick (Lomuto/Hoare/3-way) | [comparison_sorts.py](sorting/comparison_sorts.py) |
| Small int range, fixed-width keys, uniform floats: counting, radix, bucket | [linear_sorts.py](sorting/linear_sorts.py) |
| K-th element / median in O(n), k smallest, wiggle sort II | [selection.py](sorting/selection.py) |
| Count pairs i < j: inversions, smaller after self, reverse pairs, range sums | [merge_count.py](sorting/merge_count.py) |
| Multi-key, comparator, given order: largest number, logs, frequency | [custom_comparators.py](sorting/custom_comparators.py) |
| Sort then sweep: intervals, min difference, H-index, max gap, cookies | [sort_first.py](sorting/sort_first.py) |
| Values in 1..n, O(1) space: missing/duplicate, couples, min swaps | [cyclic_sort.py](sorting/cyclic_sort.py) |

</details>

<details><summary><b>Intervals</b></summary>

| Situation | File |
|---|---|
| Merge overlapping, insert into sorted, summary/missing ranges, partition labels | [merging.py](intervals/merging.py) |
| Can attend all, max meetings, min removals, min arrows | [overlap_greedy.py](intervals/overlap_greedy.py) |
| Min rooms (two sorted arrays), busiest time, employee free time, skyline | [sweep_line.py](intervals/sweep_line.py) |
| Online bookings: My Calendar I / II / III | [booking.py](intervals/booking.py) |
| Add/remove/query ranges, stream as disjoint intervals | [interval_set.py](intervals/interval_set.py) |
| Covered intervals, count intervals per point, smallest interval per query | [relations.py](intervals/relations.py) |

</details>

<details><summary><b>Binary Search</b></summary>

| Situation | File |
|---|---|
| First true of a monotone predicate, lower/upper bound | [templates.py](binary_search/templates.py) |
| First/last position, count, insert position, floor/ceil, k closest | [occurrences.py](binary_search/occurrences.py) |
| Rotated sorted array: min, search, duplicates | [rotated_array.py](binary_search/rotated_array.py) |
| Peak element, mountain / bitonic array, 2D peak | [peak_finding.py](binary_search/peak_finding.py) |
| Min-max / max-min: Koko, ship capacity, split array, bouquets | [answer_search.py](binary_search/answer_search.py) |
| sqrt, roots to a precision, max average, fractional answers | [real_valued.py](binary_search/real_valued.py) |
| 2D matrix: row-major flatten vs staircase | [matrix_search.py](binary_search/matrix_search.py) |
| Median / k-th of two sorted arrays | [two_arrays.py](binary_search/two_arrays.py) |
| K-th smallest in matrix, multiplication table, pair distance | [kth_by_value.py](binary_search/kth_by_value.py) |

</details>

<details><summary><b>Linked Lists</b></summary>

| Situation | File |
|---|---|
| Head might be deleted: remove value, sorted dedupe I/II, partition, delete given node | [dummy_head.py](linked_lists/dummy_head.py) |
| Reverse all / m..n / k-groups, swap pairs, palindrome in O(1) space | [reversal.py](linked_lists/reversal.py) |
| Reorder L0→Ln→L1, odd-even, rotate, split into k parts | [reordering.py](linked_lists/reordering.py) |
| Merge two / k sorted, sort list O(n log n), insertion sort | [merge_sort.py](linked_lists/merge_sort.py) |
| Digit lists: add I/II, plus one, double | [arithmetic.py](linked_lists/arithmetic.py) |
| Copy list with random pointer, flatten multilevel list | [extra_pointers.py](linked_lists/extra_pointers.py) |
| Y-shaped lists: first shared node | [intersection.py](linked_lists/intersection.py) |
| Shared `ListNode`, `from_list` / `to_list`, generators | [ll.py](linked_lists/ll.py) |

</details>

<details><summary><b>Stacks, Queues & Heaps</b></summary>

| Situation | File |
|---|---|
| Valid brackets, min fixes, longest valid | [bracket_matching.py](stacks_heaps/bracket_matching.py) |
| RPN, calculator with precedence and parens | [expression_eval.py](stacks_heaps/expression_eval.py) |
| Next greater/smaller, warmer day, span, sum of mins | [monotonic_stack.py](stacks_heaps/monotonic_stack.py) |
| Largest rectangle, maximal rectangle, rain water | [histogram.py](stacks_heaps/histogram.py) |
| Smallest number/subsequence after removals | [monotonic_greedy.py](stacks_heaps/monotonic_greedy.py) |
| Asteroids, decode `3[a]`, simplify path, call logs | [stack_simulation.py](stacks_heaps/stack_simulation.py) |
| Min stack, queue via stacks, freq stack | [stack_design.py](stacks_heaps/stack_design.py) |
| Circular queue/deque, last-N-ms counter, moving average | [queue_design.py](stacks_heaps/queue_design.py) |
| Window max, max − min ≤ limit, shortest sum ≥ k | [monotonic_deque.py](stacks_heaps/monotonic_deque.py) |
| Ticket line, senate rounds, reveal cards, Josephus | [queue_simulation.py](stacks_heaps/queue_simulation.py) |
| heapq idioms, max-heap, tiebreakers, own heap | [heap_basics.py](stacks_heaps/heap_basics.py) |
| k largest, kth largest, k frequent, k closest | [top_k.py](stacks_heaps/top_k.py) |
| k sorted lists, sorted matrix, smallest range | [k_way_merge.py](stacks_heaps/k_way_merge.py) |
| Running median, IPO | [two_heaps.py](stacks_heaps/two_heaps.py) |
| Delete from a heap, sliding median | [lazy_deletion.py](stacks_heaps/lazy_deletion.py) |
| Meeting rooms, task cooldown, reorganise, CPU | [heap_scheduling.py](stacks_heaps/heap_scheduling.py) |

</details>

<details><summary><b>Matrix & Simulation</b></summary>

| Situation | File |
|---|---|
| Direction arrays, turning, flatten `r*C+c`, reshape, shift, padding | [grid_idioms.py](matrix_simulation/grid_idioms.py) |
| Spiral order, fill a spiral, walk outward from a cell | [spiral.py](matrix_simulation/spiral.py) |
| Group by `r+c` / `r-c`, zigzag, sort diagonals, Toeplitz, diagonal sum | [diagonals.py](matrix_simulation/diagonals.py) |
| Rotate 90° in place, flip, transpose, k quarter turns | [rotate_flip.py](matrix_simulation/rotate_flip.py) |
| O(1)-space set zeroes, Game of Life in place | [in_place_marking.py](matrix_simulation/in_place_marking.py) |
| Stones fall, Candy Crush, 2048 moves | [gravity.py](matrix_simulation/gravity.py) |
| Valid Sudoku, tic-tac-toe winner / O(1) moves, lucky numbers | [validation.py](matrix_simulation/validation.py) |
| Robot instructions, obstacles, bounded-in-circle, snake | [robot_simulation.py](matrix_simulation/robot_simulation.py) |

</details>

<details><summary><b>Binary Trees</b></summary>

| Situation | File |
|---|---|
| Depth, root-path state, subtree sums | [top_down_bottom_up.py](binary_trees/top_down_bottom_up.py) |
| Diameter, max path sum (path bends at a node) | [global_best.py](binary_trees/global_best.py) |
| Balanced check: value + verdict in one return | [sentinel_returns.py](binary_trees/sentinel_returns.py) |
| Pre/in/postorder without recursion, Morris | [iterative_traversals.py](binary_trees/iterative_traversals.py) |
| Rows, side views, zigzag, min depth | [level_order.py](binary_trees/level_order.py) |
| Vertical order, top/bottom view, max width | [coordinate_tagging.py](binary_trees/coordinate_tagging.py) |
| Same, symmetric, invert, subtree | [structural_comparison.py](binary_trees/structural_comparison.py) |
| Lowest common ancestor, node distance | [lca.py](binary_trees/lca.py) |
| Distance k from a node, burn/infect time | [tree_as_graph.py](binary_trees/tree_as_graph.py) |
| Build from pre/post + inorder | [construct_from_traversals.py](binary_trees/construct_from_traversals.py) |
| Tree to string and back | [serialize_deserialize.py](binary_trees/serialize_deserialize.py) |
| Count downward paths summing to k | [path_prefix_sum.py](binary_trees/path_prefix_sum.py) |
| House robber, vertex cover, cameras | [tree_dp.py](binary_trees/tree_dp.py) |
| Answer for every node as root | [rerooting.py](binary_trees/rerooting.py) |
| Count a complete tree in O(log² n) | [count_complete.py](binary_trees/count_complete.py) |
| Many LCA / k-th ancestor queries | [binary_lifting.py](binary_trees/binary_lifting.py) |

</details>

<details><summary><b>Binary Search Trees</b></summary>

| Situation | File |
|---|---|
| Search, insert, delete | [search_insert_delete.py](binary_search_trees/search_insert_delete.py) |
| Is it a BST, largest BST subtree | [validate_bst.py](binary_search_trees/validate_bst.py) |
| K-th smallest, iterator, successor | [kth_and_iterator.py](binary_search_trees/kth_and_iterator.py) |
| Pair summing to k (one or two BSTs) | [two_sum_bst.py](binary_search_trees/two_sum_bst.py) |
| Two nodes swapped | [recover_bst.py](binary_search_trees/recover_bst.py) |
| Floor, ceil, closest, k closest | [floor_ceil.py](binary_search_trees/floor_ceil.py) |
| LCA, distance in a BST | [bst_lca.py](binary_search_trees/bst_lca.py) |
| Range sum, values in range, trim | [range_queries.py](binary_search_trees/range_queries.py) |
| Build from sorted array/list or preorder | [construct_bst.py](binary_search_trees/construct_bst.py) |
| To sorted DLL, increasing tree, greater-sum | [convert_bst.py](binary_search_trees/convert_bst.py) |
| Rebalance, count/generate BSTs, rotations | [balance_and_count.py](binary_search_trees/balance_and_count.py) |

</details>

<details><summary><b>Tries</b></summary>

| Situation | File |
|---|---|
| Insert / search / startsWith, counts, delete | [basic_trie.py](tries/basic_trie.py) |
| Search with `.` wildcards | [wildcard_search.py](tries/wildcard_search.py) |
| LCP, replace words, top-3 suggestions, map sum, prefix + suffix | [prefix_queries.py](tries/prefix_queries.py) |
| Longest word one char at a time, concatenated words, word break | [word_building.py](tries/word_building.py) |
| Does a word end at the latest stream char | [stream_matching.py](tries/stream_matching.py) |
| Max XOR pair, max XOR under a limit | [bitwise_trie.py](tries/bitwise_trie.py) |
| Concatenation is a palindrome | [palindrome_pairs.py](tries/palindrome_pairs.py) |

</details>

<details><summary><b>Backtracking</b></summary>

| Situation | File |
|---|---|
| Subsets, with dups, non-decreasing subsequences, subset sums (78, 1863, 90, 491, 416, 2035) | [subsets.py](backtracking/subsets.py) |
| Choose k, combination sum I/II/III/IV, missing binary string (77, 39, 40, 216, 377, 1980) | [combinations.py](backtracking/combinations.py) |
| Permutations, with dups, tiles, palindromes, beautiful, squareful (46, 47, 1079, 267, 526, 996) | [permutations.py](backtracking/permutations.py) |
| Next / prev / k-th permutation, rank (31, 556, 1053, 60) | [permutation_order.py](backtracking/permutation_order.py) |
| k equal subsets, matchsticks, cookies, jobs, marbles (698, 473, 2305, 1723, 2551) | [bucket_filling.py](backtracking/bucket_filling.py) |
| Palindrome partition, IP addresses, word break II (131, 93, 140) | [partitioning.py](backtracking/partitioning.py) |
| Word search I/II, N-Queens, Sudoku, maze paths, paths III, DAG paths, flood fill, islands, gold (79, 212, 51, 52, 37, 63, 980, 797, 733, 200, 1219) | [grid_search.py](backtracking/grid_search.py) |
| Parentheses, phone letters, add operators, target sum (22, 17, 282, 494) | [string_construction.py](backtracking/string_construction.py) |
| Factor combinations, dice rolls (254, 1155) | [target_enumeration.py](backtracking/target_enumeration.py) |
| Word pattern II, word pattern (291, 290) | [bijection.py](backtracking/bijection.py) |
| Remove invalid parentheses (301) | [removal.py](backtracking/removal.py) |

</details>

<details><summary><b>Greedy</b></summary>

| Situation | File |
|---|---|
| Prove it (exchange, stays ahead); coins where greedy fails | [proofs.py](greedy/proofs.py) |
| Reach the end, fewest jumps, cover [0, T] | [reachability.py](greedy/reachability.py) |
| Gas station, running sum ≥ 1, stock II | [running_balance.py](greedy/running_balance.py) |
| Cookies, boats, two cities, tokens, perimeter | [sort_assign.py](greedy/sort_assign.py) |
| Most parts, balanced split, hand of straights | [partitioning.py](greedy/partitioning.py) |
| Candy, unique frequencies, queue by height | [two_pass.py](greedy/two_pass.py) |
| Largest number, `*` brackets, min additions | [string_greedy.py](greedy/string_greedy.py) |
| Deadlines, refuelling, bricks/ladders (heap regret) | [heap_regret.py](greedy/heap_regret.py) |

</details>

<details><summary><b>Graphs</b></summary>

| Situation | File |
|---|---|
| Unweighted shortest path | [bfs.py](graphs/bfs.py) |
| Reachability, components | [dfs.py](graphs/dfs.py) |
| Nearest of many sources | [multi_source_bfs.py](graphs/multi_source_bfs.py) |
| Extra state (keys, fuel, breaks) | [state_space_bfs.py](graphs/state_space_bfs.py) |
| Nodes are strings/boards | [implicit_neighbors.py](graphs/implicit_neighbors.py) |
| Both ends known, big branching | [bidirectional_bfs.py](graphs/bidirectional_bfs.py) |
| 0/1 weights | [zero_one_bfs.py](graphs/zero_one_bfs.py) |
| Non-negative weights, minimax, max product | [dijkstra.py](graphs/dijkstra.py) |
| Negative weights, ≤ K edges | [bellman_ford.py](graphs/bellman_ford.py) |
| All pairs, small V | [floyd_warshall.py](graphs/floyd_warshall.py) |
| DAG, any weights | [dag_longest_path.py](graphs/dag_longest_path.py) |
| Dynamic connectivity, ratio relations | [union_find.py](graphs/union_find.py) |
| Prerequisite ordering | [topological_sort.py](graphs/topological_sort.py) |
| Cycles, is-it-a-tree | [cycle_detection.py](graphs/cycle_detection.py) |
| Tree centres, diameter | [leaf_peeling.py](graphs/leaf_peeling.py) |
| Two conflict-free groups | [bipartite.py](graphs/bipartite.py) |
| Cheapest spanning network | [mst.py](graphs/mst.py) |
| Single points of failure | [bridges_articulation.py](graphs/bridges_articulation.py) |
| Mutually reachable groups | [scc_kosaraju.py](graphs/scc_kosaraju.py) |
| Every edge once | [euler_path.py](graphs/euler_path.py) |
| Deep-copy a cyclic graph | [clone_graph.py](graphs/clone_graph.py) |
| Representations, grid neighbours | [modeling.py](graphs/modeling.py) |

</details>

<details><summary><b>Dynamic Programming</b></summary>

| Situation | File |
|---|---|
| No two adjacent, stairs, delete-and-earn | [linear_dp.py](dynamic_programming/linear_dp.py) |
| Decode ways, word break | [string_segmentation.py](dynamic_programming/string_segmentation.py) |
| Budget, subset sum, ±target, coin change | [knapsack.py](dynamic_programming/knapsack.py) |
| Longest increasing chain, envelopes | [lis.py](dynamic_programming/lis.py) |
| Two strings: LCS, edit distance, interleave | [two_sequence.py](dynamic_programming/two_sequence.py) |
| Wildcard `?*`, regex `.*` | [pattern_matching.py](dynamic_programming/pattern_matching.py) |
| Right/down grid paths, squares, dungeon | [grid_dp.py](dynamic_programming/grid_dp.py) |
| Any-direction moves with a strict order | [memo_dfs.py](dynamic_programming/memo_dfs.py) |
| Palindromic subsequence, min cuts | [palindrome_dp.py](dynamic_programming/palindrome_dp.py) |
| Split a segment: balloons, sticks, stones | [interval_dp.py](dynamic_programming/interval_dp.py) |
| Two players, optimal play | [game_dp.py](dynamic_programming/game_dp.py) |
| Modes over time: stocks, paint house | [state_machine.py](dynamic_programming/state_machine.py) |
| n ≤ 20, subsets: TSP, team, assignment | [bitmask_dp.py](dynamic_programming/bitmask_dp.py) |
| Choices on a tree, answer for every root | [tree_dp_problems.py](dynamic_programming/tree_dp_problems.py) |
| Count numbers ≤ N with a digit property | [digit_dp.py](dynamic_programming/digit_dp.py) |
| Count mod 10⁹+7, Catalan shapes | [counting_dp.py](dynamic_programming/counting_dp.py) |
| `dp[i] = a[i] + max(dp[i-k..i-1])` | [deque_optimization.py](dynamic_programming/deque_optimization.py) |

</details>

<details><summary><b>Bit Manipulation</b></summary>

| Situation | File |
|---|---|
| Get / set / clear / flip a bit, lowest set bit, power of two / four, 32-bit emulation | [bit_basics.py](bit_manipulation/bit_basics.py) |
| One element unpaired (twice / thrice), missing number, XOR of 0..n | [xor_tricks.py](bit_manipulation/xor_tricks.py) |
| Popcount for 0..n, number of 1 bits, Hamming distance (pairs, total) | [counting_bits.py](bit_manipulation/counting_bits.py) |
| Add / multiply without operators, reverse bits, AND of a range | [bit_arithmetic.py](bit_manipulation/bit_arithmetic.py) |
| Subsets, submasks, k-subsets (Gosper), letter masks, Gray code | [bitmask_sets.py](bit_manipulation/bitmask_sets.py) |
| XOR-equal triplets, distinct subarray ORs, decode adjacent XORs | [subarray_bitwise.py](bit_manipulation/subarray_bitwise.py) |

</details>

<details><summary><b>Math</b></summary>

| Situation | File |
|---|---|
| Huge exponent, `x^n mod m`, n-th term of a recurrence | [fast_power.py](math_algorithms/fast_power.py) |
| Simplify fractions, common periods, Bezout, water jugs | [gcd_lcm.py](math_algorithms/gcd_lcm.py) |
| All primes up to N, factorise many numbers | [sieve.py](math_algorithms/sieve.py) |
| Is n prime, factorise one n, divisors | [primes.py](math_algorithms/primes.py) |
| n-th ugly / super-ugly number | [smooth_numbers.py](math_algorithms/smooth_numbers.py) |
| "Answer mod 10^9 + 7", modular inverse | [modular.py](math_algorithms/modular.py) |
| C(n, k), Pascal's triangle | [binomial.py](math_algorithms/binomial.py) |
| Grid paths, stars and bars, Catalan, inclusion-exclusion, pigeonhole | [counting.py](math_algorithms/counting.py) |
| Floor / ceil / truncate on negatives, divide without `/` | [integer_division.py](math_algorithms/integer_division.py) |
| Base k, base -2, Excel columns, Roman numerals, English words | [base_conversion.py](math_algorithms/base_conversion.py) |
| Add / subtract / multiply numbers given as strings | [big_number_strings.py](math_algorithms/big_number_strings.py) |
| Turns, collinearity, slopes, rectangles, squares, convex hull | [geometry.py](math_algorithms/geometry.py) |
| Shuffle, reservoir sampling, weighted pick, rand10 from rand7 | [randomized.py](math_algorithms/randomized.py) |
| Reverse digits, palindrome number, 32-bit overflow, atoi | [digits.py](math_algorithms/digits.py) |

</details>

<details><summary><b>Data Structure Design</b></summary>

| Situation | File |
|---|---|
| LRU / LFU cache, O(1) get/put | [caches.py](design/caches.py) |
| Insert/delete/getRandom O(1), with duplicates | [randomized_set.py](design/randomized_set.py) |
| HashMap/HashSet from scratch, load factor | [hash_table.py](design/hash_table.py) |
| Value at time t, snapshots, corrected prices, rate limiter | [time_based.py](design/time_based.py) |
| Peeking, nested list, zigzag, 2D iterators | [iterators.py](design/iterators.py) |
| Max/min-count key O(1), leaderboard, average trip time | [rankings.py](design/rankings.py) |
| Twitter feed, browser history, file system, tic-tac-toe | [mini_systems.py](design/mini_systems.py) |

</details>

Generated by `python3 build_readme.py` from the section READMEs — edit those, not this.
