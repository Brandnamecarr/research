# Module 4: Graphs and network topologies (BFS and DFS)

> BFS and DFS are the same algorithm with one container swapped. A queue explores by distance. A stack explores by depth. Everything each is good at follows from that.

Previous: [Module 3, trees](../03-trees/README.md) · [Back to the curriculum](../README.md) · Next: [Module 5, algorithmic paradigms](../05-algorithmic-paradigms/README.md)

## 1. Core conceptual model

### What a graph is

A graph is a set of **nodes** and a set of **edges** connecting them. It is the general case of every structure so far. A linked list is a graph where each node has one outgoing edge. A tree is a graph with no cycles and exactly one path between any two nodes.

Three properties decide which algorithms apply:

| Property | Options | Example |
|---|---|---|
| Direction | Undirected (links go both ways) or directed | Network cable vs "A depends on B" |
| Weight | Unweighted, or each edge has a cost | Hop count vs latency per link |
| Cycles | Cyclic, or acyclic (a directed acyclic graph is a "DAG") | Road network vs build dependencies |

### Representing a graph: the adjacency list

```python
graph = {
    "api":    ["auth", "orders"],
    "auth":   ["users-db"],
    "orders": ["users-db", "payments"],
}
```

Each node maps to the list of its neighbours. Memory is O(V + E), where V is the number of nodes (vertices) and E the number of edges. "Who is next to X?" is one dictionary lookup.

The alternative is an **adjacency matrix**, a V × V grid with a mark wherever an edge exists. It answers "is there an edge from A to B?" in O(1) but always costs O(V²) memory. Real graphs are sparse. A graph of a million nodes with 10 edges each needs about 10 million list entries, or a trillion matrix cells. The adjacency list is the default for that reason.

### One traversal skeleton, two containers

Every traversal has the same parts: a **frontier** of nodes discovered but not yet explored, and a **visited set** so no node is processed twice.

```
put the start node in the frontier
while the frontier is not empty:
    take a node out
    for each neighbour not yet visited:
        mark it visited and put it in the frontier
```

The visited set is what separates graph traversal from tree traversal. A tree has one path to each node. A graph can have many, and can loop, so without the set the search either repeats work exponentially or never ends.

The only remaining choice is which node comes out of the frontier next.

### Breadth-first search: a queue

Take the **oldest** node (first in, first out). Nodes discovered earlier are closer to the start, so the search expands in rings: everything 1 hop away, then everything 2 hops away, and so on.

```
ring 0:  A
ring 1:  B  C          (neighbours of A)
ring 2:  D  E  F       (their unvisited neighbours)
```

This ordering gives BFS its guarantee: **the first time BFS reaches a node, it got there by a path with the fewest possible edges.** Any shorter path would have been found in an earlier ring. Recording which node discovered each node lets you rebuild that path by walking backwards.

### Depth-first search: a stack

Take the **newest** node (last in, first out). The search follows one path as far as it goes, then backs up to the most recent branch point and tries the next option. Recursion does this naturally, because the call stack is the stack.

The useful moment in DFS is when it **backs out** of a node. By then, everything reachable from that node has been fully explored. Two applications come directly from this:

**Topological ordering.** In a dependency graph, record each node as you back out of it. Every node is then recorded after all of its dependencies, which is a valid build order.

**Cycle detection.** Track three states per node:

| State | Meaning |
|---|---|
| Unvisited | Not reached yet |
| In progress | Entered but not yet backed out of; it is on the path currently being walked |
| Done | It and everything below it are fully explored |

Following an edge to an **in progress** node means you have found a route from that node back to itself, which is a cycle. Following an edge to a **done** node is harmless; you reached a finished region by a second route. Two states are not enough for directed graphs because they cannot tell these cases apart, and a diamond-shaped dependency (A needs B and C, and both need D) would be reported as a cycle.

### BFS vs DFS

| | BFS | DFS |
|---|---|---|
| Frontier | Queue (FIFO) | Stack (LIFO) or recursion |
| Explores | Level by level, nearest first | One branch to the end, then back up |
| Time | O(V + E) | O(V + E) |
| Memory | The widest ring, which can be most of the graph | The longest path |
| Guarantee | Shortest path by edge count | None about path length |
| Natural uses | Shortest paths, "within k hops", level-by-level processing | Dependency ordering, cycle detection, reachability |

BFS counts hops, so its shortest paths are only shortest when every edge costs the same. With weighted edges, replace the queue with a min-heap keyed by total cost so far. That is Dijkstra's algorithm, and it uses the heap from Module 3.

## 2. Systems lens

**Backend systems are full of graphs.** Service call graphs, package dependencies, task DAGs in CI pipelines and schedulers such as Airflow, foreign-key relationships, network topology, the object reference graph that a garbage collector walks, and the wait-for graph between transactions holding locks. Recognising that a problem is a graph traversal is usually the hard part.

### Where BFS shows up

- **Fewest-hop routing** and "degrees of separation" queries.
- **Blast radius.** "If this service fails, what is affected within two hops?" is BFS with a depth limit.
- **Crawling by depth**, and anything else that should process near things before far things.
- **Flooding and gossip** in networks, where a hop limit (TTL) bounds the rings.

The hazard is memory. The frontier grows roughly as `degree^depth`, and real graphs have hubs: one account with a million followers puts a million nodes in the next ring. Bound the depth. For point-to-point searches, bidirectional BFS helps a great deal. Searching from both ends and meeting in the middle explores about `2 × b^(d/2)` nodes instead of `b^d`.

### Where DFS shows up

- **Dependency resolution.** Build systems such as `make` and Bazel, package installers, database migration ordering, service start-up order, and spreadsheet recalculation are all topological sorts.
- **Cycle detection.** Circular imports and circular dependencies are the obvious cases. Databases also detect deadlocks this way: they look for a cycle in the wait-for graph and abort one transaction to break it.
- **Reachability.** A garbage collector's mark phase finds everything reachable from the roots; whatever is left is garbage. This is also why reference counting alone leaks cycles, and why CPython has a separate cycle collector. Tree shaking and dead-code elimination are the same question asked of a module graph.
- **Incremental builds.** "What must be rebuilt if X changes?" is reachability with the edges reversed.

### Implementation realities

- **Recursion depth.** Recursive DFS on a long chain exceeds Python's default limit of about 1,000 frames. Use an explicit stack for graphs you do not control.
- **The visited set costs O(V) memory.** For very large graphs such as a web crawl, it moves to disk or becomes a probabilistic structure like a Bloom filter.
- **Use the standard library for real dependency ordering.** `graphlib.TopologicalSorter` detects cycles, and its `get_ready()` method hands back every node whose dependencies are complete, so independent tasks can run in parallel.
- **Graphs in SQL.** A relational database stores a graph as an edge table. `WITH RECURSIVE` traverses it one level per iteration, and each iteration is a join. Deep traversals get expensive, which is the niche graph databases fill by storing direct references between neighbours.
- **Across a network, every hop can be a round trip.** That is the N+1 problem from Module 1 again. BFS has an advantage here because it batches naturally: one query can fetch the neighbours of the whole current ring. DFS issues one request at a time.

## 3. Code

Two samples, each runnable on its own.

### [bfs_shortest_path.py](bfs_shortest_path.py): shortest paths and blast radius

```bash
python3 bfs_shortest_path.py
```

```
1. The adjacency list
  edge-proxy  -> ['auth', 'api']
  auth        -> ['edge-proxy', 'sessions']
  api         -> ['edge-proxy', 'users-db', 'orders']
  sessions    -> ['auth', 'users-db']
  users-db    -> ['sessions', 'api']
  ...

2. Path from edge-proxy to users-db
  BFS (2 hops): edge-proxy -> api -> users-db
  DFS (3 hops): edge-proxy -> auth -> sessions -> users-db

3. Blast radius: everything grouped by hops from users-db
  0 hops: ['users-db']
  1 hops: ['api', 'sessions']
  2 hops: ['auth', 'edge-proxy', 'orders']
  3 hops: ['inventory', 'payments']
  4 hops: ['ledger-db', 'warehouse']
```

What to notice:

- **Demo 2.** Both searches are correct, and only BFS is shortest. DFS tried `auth` first, kept going down that branch, and reached the goal before it ever looked at `api`.
- **Demo 3.** The rings are the order in which BFS discovers nodes. `hops_from` contains no logic for computing distances beyond "one more than whoever found me".
- **In the code.** Compare the main loops of `shortest_path` and `any_path_dfs`. The difference in search order comes down to `popleft()` versus `pop()`. Also note that BFS marks a node visited when it is *discovered*, not when it is removed from the queue. Marking late lets the same node be queued once per neighbour.

### [dfs_dependencies.py](dfs_dependencies.py): build order, impact analysis, and cycles

```bash
python3 dfs_dependencies.py
```

```
1. Build order (each package appears after everything it needs)
  1. sockets        needs: nothing
  2. http           needs: sockets
  3. crypto         needs: nothing
  4. auth           needs: http, crypto
  5. api-client     needs: http, auth
  6. design-tokens  needs: nothing
  7. ui-kit         needs: design-tokens
  8. web-app        needs: api-client, ui-kit

2. What must be rebuilt if `http` changes?
  ['api-client', 'auth', 'web-app']

3. Add a bad edge: crypto now depends on api-client
  cycle detected: api-client -> auth -> crypto -> api-client
```

What to notice:

- **Demo 1.** The search started at `web-app`, yet `web-app` is listed last. Nodes are recorded as the search backs out of them, so the deepest dependency (`sockets`) is recorded first.
- **Demo 1, the diamond.** `http` is needed by both `api-client` and `auth` and appears once. The second time the search reaches it, it is already done and is skipped. That check is what keeps the traversal linear.
- **Demo 3.** The error reports the actual loop. It is read straight off the list of in-progress nodes.

### Experiments to try

- In `bfs_shortest_path.py`, add a direct link `("edge-proxy", "users-db")` to the end of the list and rerun. BFS drops to 1 hop. DFS still reports the 3-hop route, even though the goal is now a direct neighbour of the start, because it commits to `auth` first.
- In `dfs_dependencies.py`, remove the `IN_PROGRESS` state so that nodes are only unvisited or done, then run demo 3. The cycle goes undetected and the "build order" returned is silently wrong.
- Build a 5,000-node chain (`{"n0": ["n1"], "n1": ["n2"], ...}`) and pass it to `build_order`. It raises `RecursionError`. Then try `dependents_of` on the same graph, which uses an explicit stack.
