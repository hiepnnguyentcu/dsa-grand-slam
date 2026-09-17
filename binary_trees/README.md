# Binary Trees

One file per technique: implementation + tests. Shared node, codec and random-tree helpers live in [tree.py](tree.py). Explanations: [Binary Trees — Field Guide](https://claude.ai/code/artifact/e12df7b3-b5ea-4c4b-9b6f-df52cda45a62).

```
python3 binary_trees/lca.py                                        # one file
for f in binary_trees/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Depth, root-path state, subtree sums | [top_down_bottom_up.py](top_down_bottom_up.py) |
| Diameter, max path sum (path bends at a node) | [global_best.py](global_best.py) |
| Balanced check: value + verdict in one return | [sentinel_returns.py](sentinel_returns.py) |
| Pre/in/postorder without recursion, Morris | [iterative_traversals.py](iterative_traversals.py) |
| Rows, side views, zigzag, min depth | [level_order.py](level_order.py) |
| Vertical order, top/bottom view, max width | [coordinate_tagging.py](coordinate_tagging.py) |
| Same, symmetric, invert, subtree | [structural_comparison.py](structural_comparison.py) |
| Lowest common ancestor, node distance | [lca.py](lca.py) |
| Distance k from a node, burn/infect time | [tree_as_graph.py](tree_as_graph.py) |
| Build from pre/post + inorder | [construct_from_traversals.py](construct_from_traversals.py) |
| Tree to string and back | [serialize_deserialize.py](serialize_deserialize.py) |
| Count downward paths summing to k | [path_prefix_sum.py](path_prefix_sum.py) |
| House robber, vertex cover, cameras | [tree_dp.py](tree_dp.py) |
| Answer for every node as root | [rerooting.py](rerooting.py) |
| Count a complete tree in O(log² n) | [count_complete.py](count_complete.py) |
| Many LCA / k-th ancestor queries | [binary_lifting.py](binary_lifting.py) |

**Conventions:** trees are LeetCode level-order lists, `[1, None, 2]` = 1 with right child 2 (`build` / `to_list` in tree.py); edge-list trees use nodes `0..n-1`.
