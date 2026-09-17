"""Graph cloning — deep copy a graph that contains cycles.

Signs: "return a deep copy", the nodes are objects holding neighbour references,
       and the graph may loop back on itself.
Approach: keep a map original -> copy. Create a node's copy the *first* time you
          see it, and always wire neighbours through the map. That map is
          simultaneously the visited set and the result, which is what stops the
          cycles from recursing forever.
Complexity: O(V + E).
Gotchas:
  - Create the copy on first sight, before walking its neighbours. Creating it
    after would recurse into a cycle and never come back.
  - Append neighbours exactly once per original edge. Popping a node twice
    duplicates its neighbour list — harmless-looking, structurally wrong.
  - The same pattern copies any object graph (linked list with random pointers,
    nested config). Nothing here is specific to graphs.

Run the tests at the bottom with:  python3 graphs/clone_graph.py
"""


# ---------------------------------------------------------------- implementation


class GraphNode:
    def __init__(self, val, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

    def __repr__(self):
        return f"GraphNode({self.val})"


def clone_graph(node):
    """Deep copy, iteratively. Returns the copy of `node`, or None."""
    if node is None:
        return None
    copies = {node: GraphNode(node.val)}
    stack = [node]
    while stack:
        u = stack.pop()
        for v in u.neighbors:
            if v not in copies:
                copies[v] = GraphNode(v.val)
                stack.append(v)  # push only on first sight -> popped exactly once
            copies[u].neighbors.append(copies[v])
    return copies[node]


def clone_graph_recursive(node, copies=None):
    """Deep copy, recursively. The `copies` memo is what breaks the cycles."""
    if node is None:
        return None
    if copies is None:
        copies = {}
    if node in copies:
        return copies[node]

    copy = GraphNode(node.val)
    copies[node] = copy  # register BEFORE recursing, or a cycle never terminates
    for v in node.neighbors:
        copy.neighbors.append(clone_graph_recursive(v, copies))
    return copy


def build_from_adjacency(adj):
    """Helper: {val: [neighbour vals]} -> the node holding the smallest val."""
    nodes = {val: GraphNode(val) for val in adj}
    for val, nbrs in adj.items():
        nodes[val].neighbors = [nodes[v] for v in nbrs]
    return nodes[min(nodes)] if nodes else None


def to_adjacency(node):
    """Helper: walk a node graph back into {val: [neighbour vals]}."""
    if node is None:
        return {}
    adj, stack, seen = {}, [node], {node}
    while stack:
        u = stack.pop()
        adj[u.val] = [v.val for v in u.neighbors]
        for v in u.neighbors:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return adj


# ------------------------------------------------------------------------ tests


def all_nodes(node):
    if node is None:
        return set()
    out, stack = set(), [node]
    while stack:
        u = stack.pop()
        if id(u) in {id(x) for x in out}:
            continue
        out.add(u)
        for v in u.neighbors:
            if v not in out:
                stack.append(v)
    return out


SQUARE = {1: [2, 4], 2: [1, 3], 3: [2, 4], 4: [1, 3]}


def test_structure_is_preserved():
    for clone in (clone_graph, clone_graph_recursive):
        original = build_from_adjacency(SQUARE)
        copy = clone(original)
        assert to_adjacency(copy) == SQUARE


def test_copy_shares_no_objects_with_the_original():
    for clone in (clone_graph, clone_graph_recursive):
        original = build_from_adjacency(SQUARE)
        copy = clone(original)
        originals = {id(x) for x in all_nodes(original)}
        clones = {id(x) for x in all_nodes(copy)}
        assert originals & clones == set()
        assert len(clones) == 4


def test_mutating_the_copy_leaves_the_original_alone():
    original = build_from_adjacency(SQUARE)
    copy = clone_graph(original)
    copy.val = 999
    copy.neighbors.clear()
    assert original.val == 1
    assert to_adjacency(original) == SQUARE


def test_cycles_terminate():
    # A 2-cycle, the smallest thing that traps a naive recursive copy.
    adj = {1: [2], 2: [1]}
    for clone in (clone_graph, clone_graph_recursive):
        assert to_adjacency(clone(build_from_adjacency(adj))) == adj


def test_self_loop():
    a = GraphNode(1)
    a.neighbors = [a]
    for clone in (clone_graph, clone_graph_recursive):
        copy = clone(a)
        assert copy is not a
        assert copy.neighbors[0] is copy  # the loop points at the copy, not the original


def test_single_node_and_none():
    for clone in (clone_graph, clone_graph_recursive):
        assert clone(None) is None
        lone = GraphNode(7)
        copy = clone(lone)
        assert copy is not lone and copy.val == 7 and copy.neighbors == []


def test_duplicate_neighbour_entries_are_preserved():
    # Parallel edges are part of the structure, not noise to deduplicate.
    a, b = GraphNode(1), GraphNode(2)
    a.neighbors = [b, b]
    b.neighbors = [a]
    for clone in (clone_graph, clone_graph_recursive):
        copy = clone(a)
        assert [x.val for x in copy.neighbors] == [2, 2]
        assert copy.neighbors[0] is copy.neighbors[1]  # same node, listed twice


def test_both_implementations_agree_on_random_graphs():
    import random

    random.seed(83)
    for _ in range(30):
        n = random.randint(1, 8)
        adj = {
            i: sorted(random.sample(range(n), random.randint(0, n)))
            for i in range(n)
        }
        for u, nbrs in adj.items():  # make it undirected-consistent
            for v in nbrs:
                if u not in adj[v]:
                    adj[v].append(u)
        for v in adj:
            adj[v].sort()

        want = to_adjacency(build_from_adjacency(adj))
        assert to_adjacency(clone_graph(build_from_adjacency(adj))) == want
        assert to_adjacency(clone_graph_recursive(build_from_adjacency(adj))) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
