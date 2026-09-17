# Graphs

Running code for every technique in §18 of the DSA reference. Each file is
self-contained: module docstring (**Signs → Approach → Complexity → Gotchas**),
implementation, then its tests at the bottom.

```
python3 graphs/dijkstra.py          # run one file's tests
for f in graphs/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done
```

They are also plain `test_*` functions, so `pytest graphs/` collects them if you
install pytest.

## Picking a technique

| Situation | Use | File |
|---|---|---|
| Unweighted shortest path | BFS | [bfs.py](bfs.py) |
| Reachability, components, path existence | DFS | [dfs.py](dfs.py) |
| Nearest of many sources, simultaneous spread | Multi-source BFS | [multi_source_bfs.py](multi_source_bfs.py) |
| Position isn't the whole story (keys, fuel, breaks) | State-space BFS | [state_space_bfs.py](state_space_bfs.py) |
| Nodes are strings/boards, edges implied | Implicit neighbours | [implicit_neighbors.py](implicit_neighbors.py) |
| Both ends known, high branching factor | Bidirectional BFS | [bidirectional_bfs.py](bidirectional_bfs.py) |
| Weights are only 0 or 1 | 0-1 BFS (deque) | [zero_one_bfs.py](zero_one_bfs.py) |
| Non-negative weights | Dijkstra | [dijkstra.py](dijkstra.py) |
| Minimise the worst edge, maximise a product | Modified Dijkstra | [dijkstra.py](dijkstra.py) |
| Negative weights, or "at most K edges" | Bellman-Ford | [bellman_ford.py](bellman_ford.py) |
| All pairs, V ≲ 400 | Floyd-Warshall | [floyd_warshall.py](floyd_warshall.py) |
| Acyclic graph, any weights | Topological order + DP | [dag_longest_path.py](dag_longest_path.py) |
| Connectivity as edges arrive | Union-Find | [union_find.py](union_find.py) |
| Ratios, offsets, parity between elements | Weighted Union-Find | [union_find.py](union_find.py) |
| Ordering under prerequisites | Topological sort | [topological_sort.py](topological_sort.py) |
| Are the prerequisites even satisfiable | Cycle detection | [cycle_detection.py](cycle_detection.py) |
| Tree centres, peel from the outside | Leaf peeling | [leaf_peeling.py](leaf_peeling.py) |
| Split into two conflict-free groups | Bipartite 2-colouring | [bipartite.py](bipartite.py) |
| Connect everything as cheaply as possible | MST (Kruskal / Prim) | [mst.py](mst.py) |
| Single points of failure | Bridges, articulation points | [bridges_articulation.py](bridges_articulation.py) |
| Mutually reachable groups in a digraph | SCC (Kosaraju) | [scc_kosaraju.py](scc_kosaraju.py) |
| Use every **edge** exactly once | Eulerian path (Hierholzer) | [euler_path.py](euler_path.py) |
| Deep-copy a graph with cycles | original → copy map | [clone_graph.py](clone_graph.py) |
| Deciding what a node and an edge even are | Representations | [modeling.py](modeling.py) |

Use every **node** exactly once is a Hamiltonian path — NP-hard, and not on this
list. The edge version is linear; the node version is not.

## Conventions

```
unweighted adjacency   {u: [v, ...]}
weighted adjacency     {u: [(v, w), ...]}
edge list              [(u, v)] or [(u, v, w)]     # weight always last
```

Nodes are `0..n-1` unless the problem is naturally keyed by strings. Neighbours
are read with `g.get(u, ())` so a sink node needs no entry of its own.
Unreachable is `-1` for hop counts and `float('inf')` for weighted distances.

## Things that bite

- **Recursion limit.** CPython allows ~1000 frames. Recursive DFS, Tarjan and
  Kosaraju all inherit that; anything with a deep path needs the iterative form.
- **Mark on enqueue in BFS**, not on dequeue, or the queue fills with duplicates.
- **`k` outermost in Floyd-Warshall.** Any other order is silently wrong —
  [floyd_warshall.py](floyd_warshall.py) has a test that demonstrates it.
- **Dijkstra and negative edges** produce wrong answers, not errors.
- **Bellman-Ford's K-stops variant** must relax from a snapshot of the previous
  round, or one round chains several edges together.
- **Directed vs undirected** decides half of these algorithms. Settle it first.
