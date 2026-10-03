# Binary Search Trees

One file per technique: implementation + tests. Shared node, codec and random-BST helpers live in [bst.py](bst.py). Generic traversal, LCA and tree DP are in [binary_trees/](../binary_trees/).

```
python3 binary_search_trees/floor_ceil.py                                 # one file
for f in binary_search_trees/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Search, insert, delete | [search_insert_delete.py](search_insert_delete.py) |
| Is it a BST, largest BST subtree | [validate_bst.py](validate_bst.py) |
| K-th smallest, iterator, successor | [kth_and_iterator.py](kth_and_iterator.py) |
| Pair summing to k (one or two BSTs) | [two_sum_bst.py](two_sum_bst.py) |
| Two nodes swapped | [recover_bst.py](recover_bst.py) |
| Floor, ceil, closest, k closest | [floor_ceil.py](floor_ceil.py) |
| LCA, distance in a BST | [bst_lca.py](bst_lca.py) |
| Range sum, values in range, trim | [range_queries.py](range_queries.py) |
| Build from sorted array/list or preorder | [construct_bst.py](construct_bst.py) |
| To sorted DLL, increasing tree, greater-sum | [convert_bst.py](convert_bst.py) |
| Rebalance, count/generate BSTs, rotations | [balance_and_count.py](balance_and_count.py) |

**Conventions:** trees are LeetCode level-order lists (`build` / `to_list` in bst.py); values distinct; ranges inclusive.
