# Graphs

One file per technique: implementation + tests. Explanations: [Graph Algorithms — Field Guide](https://claude.ai/code/artifact/ed02e36a-59a5-4346-8146-d43924037c92).

```
python3 graphs/dijkstra.py                                   # one file
for f in graphs/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Unweighted shortest path | [bfs.py](bfs.py) |
| Reachability, components | [dfs.py](dfs.py) |
| Nearest of many sources | [multi_source_bfs.py](multi_source_bfs.py) |
| Extra state (keys, fuel, breaks) | [state_space_bfs.py](state_space_bfs.py) |
| Nodes are strings/boards | [implicit_neighbors.py](implicit_neighbors.py) |
| Both ends known, big branching | [bidirectional_bfs.py](bidirectional_bfs.py) |
| 0/1 weights | [zero_one_bfs.py](zero_one_bfs.py) |
| Non-negative weights, minimax, max product | [dijkstra.py](dijkstra.py) |
| Negative weights, ≤ K edges | [bellman_ford.py](bellman_ford.py) |
| All pairs, small V | [floyd_warshall.py](floyd_warshall.py) |
| DAG, any weights | [dag_longest_path.py](dag_longest_path.py) |
| Dynamic connectivity, ratio relations | [union_find.py](union_find.py) |
| Prerequisite ordering | [topological_sort.py](topological_sort.py) |
| Cycles, is-it-a-tree | [cycle_detection.py](cycle_detection.py) |
| Tree centres, diameter | [leaf_peeling.py](leaf_peeling.py) |
| Two conflict-free groups | [bipartite.py](bipartite.py) |
| Cheapest spanning network | [mst.py](mst.py) |
| Single points of failure | [bridges_articulation.py](bridges_articulation.py) |
| Mutually reachable groups | [scc_kosaraju.py](scc_kosaraju.py) |
| Every edge once | [euler_path.py](euler_path.py) |
| Deep-copy a cyclic graph | [clone_graph.py](clone_graph.py) |
| Representations, grid neighbours | [modeling.py](modeling.py) |

**Conventions:** `{u: [v]}` or `{u: [(v, w)]}`; edges `(u, v[, w])`; nodes `0..n-1`; unreachable is `-1` (hops) or `inf` (weights).
