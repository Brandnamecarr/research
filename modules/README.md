# Data Structures and Algorithms: a systems-first curriculum

Five modules that build intuition for how data structures behave under the hood and what that means for backend systems: memory, latency, scaling limits, databases, caches, and pipelines.

Each module has the same three parts:

1. **Core conceptual model**: what the structure is and how it works mechanically.
2. **Systems lens**: where it shows up in real infrastructure and what it costs.
3. **Code**: small, runnable, commented Python that makes the behaviour visible.

## Modules

| # | Module | Central question | Code |
|---|---|---|---|
| 1 | [Big O, complexity, and scaling limits](01-complexity-and-scaling/README.md) | How does cost change as the input grows? | [scaling_limits.py](01-complexity-and-scaling/scaling_limits.py) |
| 2 | [Linear structures](02-linear-structures/README.md) | What does memory layout do to performance? | [memory_layout.py](02-linear-structures/memory_layout.py), [hash_map.py](02-linear-structures/hash_map.py), [lru_cache.py](02-linear-structures/lru_cache.py) |
| 3 | [Trees](03-trees/README.md) | How do you keep data ordered and still update it quickly? | [tree.py](03-trees/tree.py), [bst.py](03-trees/bst.py), [btree.py](03-trees/btree.py), [heap.py](03-trees/heap.py), [trie.py](03-trees/trie.py) |
| 4 | [Graphs: BFS and DFS](04-graphs/README.md) | How do you explore connected things without getting lost? | [bfs_shortest_path.py](04-graphs/bfs_shortest_path.py), [dfs_dependencies.py](04-graphs/dfs_dependencies.py) |
| 5 | [Algorithmic paradigms](05-algorithmic-paradigms/README.md) | How do you avoid doing the same work twice? | [two_pointers.py](05-algorithmic-paradigms/two_pointers.py), [sliding_window.py](05-algorithmic-paradigms/sliding_window.py), [dynamic_programming.py](05-algorithmic-paradigms/dynamic_programming.py) |

## System design

Notes on how the structures above combine into whole systems. These are reading notes and have no code.

| Topic | Central question |
|---|---|
| [Common patterns](system-design/common-patterns/README.md) | Which recurring problem is this, and what is the standard solution? Covers realtime updates, long-running tasks, contention, scaling reads and writes, large blobs, multi-step processes, and proximity search. |

## Running the code

Every sample uses only the standard library (Python 3.9 or newer) and runs on its own:

```bash
python3 modules/03-trees/btree.py
```

Each script prints a few numbered experiments. The module notes show the output and say what to look for in it. The samples that measure time will print different numbers on your machine; the ratios are what matter.

The structures are built by hand so the mechanics are visible. In production code, use the standard library equivalents: `dict`, `collections.deque`, `heapq`, `bisect`, `functools.lru_cache`, `graphlib`.

## How the modules connect

The modules build on each other, and the same few ideas keep returning:

- **Module 1** gives the vocabulary for cost. Every later module is an example of moving an operation from one complexity class to a cheaper one.
- **Module 2** shows the two ways to lay data out in memory, contiguous or linked by pointers. Every later structure is built from those two.
- **Module 3** adds order. A hash map finds one key quickly but cannot answer "what comes next?"; trees can. The heap from this module becomes the priority queue behind weighted shortest paths in Module 4.
- **Module 4** generalises trees to graphs. A tree is a graph with no cycles, so the traversals are the same once you add a visited set.
- **Module 5** covers three patterns for skipping redundant work. Dynamic programming turns out to be the cache from Module 2 applied to the dependency graph from Module 4.

One idea runs through all of it: **a data structure is a bet about which operations will be common.** An array bets on reads by position, a hash map on lookups by exact key, a B-tree on range queries from disk, a heap on "give me the smallest". Choosing well means knowing what your workload does most.
