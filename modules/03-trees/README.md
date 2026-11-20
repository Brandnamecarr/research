# Module 3: Hierarchical structures (trees)

> The cost of every tree operation is the tree's height. Each kind of tree is a different strategy for keeping that height small.

Previous: [Module 2, linear structures](../02-linear-structures/README.md) · [Back to the curriculum](../README.md) · Next: [Module 4, graphs](../04-graphs/README.md)

## 1. Core conceptual model

### Why trees exist

Module 2 left a gap. Each linear structure is good at one thing and poor at another:

| Structure | Find a key | Insert | Keeps keys in order? |
|---|---|---|---|
| Sorted array | O(log n) binary search | O(n) shift | Yes |
| Linked list | O(n) | O(1) | Only if you pay O(n) to find the spot |
| Hash table | O(1) | O(1) | No |
| **Balanced tree** | **O(log n)** | **O(log n)** | **Yes** |

A tree gives you the halving of binary search and the cheap pointer updates of a linked list together. You reach for one when you need ordered data that also changes.

### Binary search trees

One rule holds at every node:

```
everything in the left subtree  <  node  <  everything in the right subtree
```

A search compares against a node and discards one entire subtree per step. An in-order traversal (left, node, right) visits the keys in sorted order, which gives you range queries.

Every operation walks one path from the root, so every operation costs the height. And a plain BST has no control over its height, because insertion order decides the shape:

```
insert 4, 2, 6, 1, 3, 5, 7          insert 1, 2, 3, 4, 5, 6, 7

          4                          1
        /   \                         \
       2     6                         2
      / \   / \                         \
     1   3 5   7                         3
                                          \
   height 3: O(log n)                      ...   height 7: O(n)
```

Sorted input turns the tree into a linked list. Sorted input is also the common case in practice: timestamps, auto-incrementing IDs, alphabetised imports.

### Balanced trees

A balanced tree repairs its shape after every insert and delete using **rotations**. A rotation is a local rewiring of three pointers that moves one subtree up and another down while preserving the left-to-right order:

```
        y                x
       / \              / \
      x   C    ->      A   y
     / \                  / \
    A   B                B   C
```

The order A, x, B, y, C is the same on both sides. Only the height changed. Schemes differ in how strictly they enforce balance:

- **AVL trees** keep the two sides of every node within one level of each other. Lookups are the fastest; writes do more rotations.
- **Red-black trees** allow the longest path to be up to twice the shortest. They rotate less on writes, which makes them the usual choice for general-purpose ordered maps such as Java's `TreeMap`, C++'s `std::map`, and the Linux kernel's `rbtree`.

Both guarantee O(log n) in the worst case, not only on average.

### B-trees

A binary tree has a fan-out of 2, so a million keys need about 20 levels. A B-tree makes each node wide: hundreds of sorted keys per node, and one more child than keys.

```
                  [ 30 | 60 ]
                 /     |     \
     [ 10 | 20 ]  [ 40 | 50 ]  [ 70 | 80 | 90 ]
```

Height becomes `log_fanout(n)` instead of `log₂(n)`. With a fan-out of 500, four levels cover more than 60 billion keys.

A B-tree stays balanced in a different way from a binary tree. It grows at the **root**. When a node overflows it splits in two and pushes its middle key up to the parent. If that overflows the parent, the parent splits as well. Only when the root splits does the tree gain a level, and then every leaf becomes one level deeper at once. All leaves are always at the same depth.

Databases use the **B+ tree** variant. Values live only in the leaves, so internal nodes hold only keys and fit more of them. The leaves are linked to each other, so a range scan walks sideways without climbing back up.

### Heaps

A heap keeps a much weaker rule than a search tree:

```
every parent  <=  both of its children        (a min-heap)
```

Siblings are not ordered relative to each other. That is enough to guarantee the minimum is at the root, and it is cheap to maintain. Reading the minimum is O(1). Push and pop are O(log n), because an item moves up or down one level at a time.

A heap is always a complete tree, filled level by level with no gaps, so it needs no nodes or pointers. It is stored in a flat array and the links are arithmetic: `parent(i) = (i - 1) // 2` and `children(i) = 2i + 1, 2i + 2`. It is a tree in concept and an array in memory, so it gets the cache behaviour of Module 2's contiguous layout.

The trade-off is that a heap cannot search. Finding an arbitrary item is O(n). It answers "what is the smallest?" and nothing else.

### Tries

In a search tree, a node holds a whole key. In a trie, the key is spelled out by the **path** from the root, one symbol per edge. Keys with a common prefix share nodes.

```
"car", "card", "care", "cat"            (root)
                                          c
                                          a
                                        /   \
                                       r*    t*        * = a key ends here
                                      / \
                                     d*  e*
```

Lookup cost is the length of the key, independent of how many keys are stored. Every key with a given prefix sits in one subtree. Walking a key passes every stored prefix of it on the way down.

The cost is memory, since a naive trie spends a node per character. Production tries are **radix trees**, which collapse chains of single-child nodes into one edge labelled with a whole substring.

### Summary

| Tree | Rule it maintains | Height | Answers quickly | Cannot do |
|---|---|---|---|---|
| BST | left < node < right | log n to n | Search, range, sorted order | Guarantee its own height |
| AVL / red-black | BST rule + balance | log₂ n | The same, in the worst case | Be disk-friendly: one node per key |
| B-tree | Sorted wide nodes, leaves at equal depth | log_fanout n | Search and range with few page reads | Cheap random-order writes |
| Heap | parent ≤ children | log₂ n | Minimum, push, pop | Search or iterate in order |
| Trie | Key = path from root | key length | Prefix and longest-prefix queries | Use memory economically |

## 2. Systems lens

### Database indexes are B+ trees

A node is sized to fill one disk page (8 KB in PostgreSQL, 16 KB in InnoDB), so fan-out is in the hundreds and a billion-row index is 3 or 4 levels deep. The upper levels are small and stay cached in memory, so a point lookup often costs a single disk read. Much of what people learn as SQL performance rules follows from this structure:

- **Composite indexes follow a leftmost-prefix rule.** An index on `(a, b)` is sorted by `a`, then by `b` within each `a`. It serves `WHERE a = ?` and `WHERE a = ? AND b > ?`. It cannot serve `WHERE b = ?` alone, because the `b` values are scattered across the whole tree.
- **Range queries and `ORDER BY` on the indexed column are cheap.** Descend once, then walk the linked leaves.
- **`LIKE 'abc%'` can use an index and `LIKE '%abc'` cannot.** A prefix defines one contiguous range of sorted keys. A suffix defines none.
- **Every index is another tree to update on every write.** Indexes speed reads and slow writes.
- **Key order affects write cost.** Sequential keys always insert at the right-hand edge, which touches one hot page. Random keys such as UUIDv4 land on random leaf pages, so pages across the whole index are dirtied and split. The code sample shows a second effect: a textbook split leaves sequentially loaded pages half empty. Real engines detect append-heavy patterns and split unevenly to keep pages full.
- **In InnoDB the table itself is a B+ tree** keyed by the primary key. Secondary indexes store the primary key, so a lookup through one walks two trees.

### B-trees vs LSM trees

A B-tree updates pages in place, which means random writes. Write-heavy stores such as RocksDB and Cassandra use a log-structured merge tree instead. Writes go into a sorted in-memory structure that is flushed to immutable sorted files, and those files are merged in the background. Writes become sequential. In exchange, a read may have to check several files. The background merge is the k-way merge implemented in `heap.py`.

### Balanced trees in memory

Use an ordered map when you need "the next key after X", a range, or a min and max that keep changing. The Linux scheduler keeps runnable tasks in a red-black tree, and `epoll` tracks its file descriptors in one. Python has no built-in ordered map. `bisect` on a list gives O(log n) search with O(n) insertion. The third-party `sortedcontainers` library uses a list of sorted lists, which is the B-tree idea again: wide contiguous chunks beat one pointer per key.

### Heaps

- **Priority queues and timers.** `asyncio` keeps its scheduled callbacks in a `heapq`. Dijkstra's shortest-path algorithm is the BFS from Module 4 with its queue replaced by a heap.
- **Top-K over a stream.** "The 10 slowest queries today" needs a heap of 10 items, however many queries go by.
- **K-way merge.** External sorting, LSM compaction, and scatter-gather queries all use it. When a query fans out to many shards and each returns sorted results, the coordinator merges them with a heap.

### Tries

IP routers pick a route by longest-prefix match over the bits of the address, using compressed tries. Many HTTP routers match URL paths with a radix tree. Autocomplete is a prefix query. Redis uses a radix tree internally for stream IDs.

### A practical warning about recursion

Tree code is naturally recursive, and recursion depth equals tree height. That is safe for balanced trees, where the height is about 20 to 40. It is a crash waiting to happen for anything that can degenerate, because Python's default call stack limit is about 1,000 frames. `bst.py` uses loops for the unbalanced tree for that reason.

## 3. Code

Five samples, each runnable on its own.

### [tree.py](tree.py): a basic tree, DFS vs BFS

```bash
python3 tree.py
```

```
DFS: [1, 2, 5, 6, 3, 4, 7]
BFS: [1, 2, 3, 4, 5, 6, 7]
find(6): True
find(9): False
```

What to notice: with no ordering rule, `insert` needs a parent to attach to and `find` has to search the whole tree, which is O(n) (a BST does this in O(height)). `dfs` and `bfs` are the same loop. One pops the newest node (a stack) and the other pops the oldest (a queue). DFS finishes one branch before starting the next. BFS goes level by level.

### [bst.py](bst.py): a plain BST against an AVL tree

```bash
python3 bst.py
```

```
1. Same 1,023 keys, three trees
  tree                                height   avg nodes visited per lookup
  plain BST, random insert order          20                           12.0
  plain BST, sorted insert order       1,023                          512.0
  AVL tree,  sorted insert order          10                            9.0

2. Range scan on the AVL tree: keys between 500 and 510
  [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510]
```

What to notice: the three trees hold identical keys. Fed sorted input, the plain BST reaches height 1,023 and a lookup averages 512 steps, the same as scanning a list. The AVL tree given the same sorted input reaches height 10, the minimum possible for 1,023 keys. Random insertion order gives a usable but unguaranteed height of 20. The `_rotate_right` function is the entire repair mechanism, and it is six lines.

### [btree.py](btree.py): wide nodes and shallow trees

```bash
python3 btree.py
```

```
1. 200,000 keys, up to 127 keys per node
  insert order    height   nodes  avg fill
  random               3   2,296       69%
  sequential           3   3,174       50%

2. Point lookup of 123,456: found=True, pages read=3
   (a balanced binary tree would visit up to 18 nodes)

3. Range scan 1,000..1,010
  [1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010]

4. Levels needed as the table grows
                rows   binary tree    B-tree, fanout 500
           1,000,000            20                     3
       1,000,000,000            30                     4
   1,000,000,000,000            40                     5
```

What to notice:

- **Demo 2.** Three page reads instead of 18. If each read is a disk access, that is the whole argument for B-trees.
- **Demo 4.** Going from a million rows to a trillion adds two levels. This is why index lookups stay fast as tables grow.
- **Demo 1.** Sequential inserts leave nearly every node half full, because each split divides a node evenly and the left half never receives another key. Random inserts fill to about 69%. Same data, 38% more pages.

### [heap.py](heap.py): a heap in a flat array, top-K, and k-way merge

```bash
python3 heap.py
```

```
1. The heap as a flat array
  push 50 -> [50]
  push 30 -> [30, 50]
  push 40 -> [30, 50, 40]
  push 10 -> [10, 30, 40, 50]
  push 20 -> [10, 20, 40, 50, 30]
  push  5 -> [5, 20, 10, 50, 30, 40]
  pops come out sorted: [5, 10, 20, 30, 40, 50]

2. Top 3 slowest requests from a latency stream (ms)
  [1250, 902, 480]

3. Merging three sorted log shards by timestamp
  t=1  a: boot
  t=2  b: boot
  t=3  b: ready
  ...
```

What to notice:

- **Demo 1.** The array is never sorted (`[5, 20, 10, 50, 30, 40]`), yet index 0 is always the minimum. Check the rule by hand: the item at index `i` is never larger than the items at `2i + 1` and `2i + 2`.
- **Demo 2.** `top_k` keeps a *min*-heap to find the *largest* items. The root is the weakest member of the current top K, which is exactly the one a newcomer has to beat.
- **Demo 3.** The merge holds one item per shard in memory, no matter how long the shards are.

### [trie.py](trie.py): autocomplete and longest-prefix routing

```bash
python3 trie.py
```

```
1. Autocomplete
  'con'  -> ['config', 'connect', 'connection', 'container', 'context']
  'co'   -> ['config', 'connect', 'connection', 'container', 'context', 'copy', 'count']
  'cr'   -> ['create', 'cron']
  'x'    -> []
  -> 62 characters stored in 37 nodes (shared prefixes are stored once)

2. Longest-prefix match in a routing table
  10.1.2.7     -> db-subnet          (matched 10.1.2.0/24)
  10.1.9.9     -> app-subnet         (matched 10.1.0.0/16)
  10.200.0.1   -> vpc                (matched 10.0.0.0/8)
  8.8.8.8      -> internet-gateway   (matched 0.0.0.0/0)
```

What to notice: in demo 2 a CIDR block is a bit-string prefix, so a routing table is a trie over the alphabet `{0, 1}`. `10.1.2.7` matches all four routes, and the deepest one wins. The lookup walks at most 32 bits whether the table holds four routes or a million.

### Experiments to try

- In `bst.py`, insert the keys in the order `[511, 255, 767, ...]` (the middle first, then the middle of each half). The plain BST comes out perfectly balanced with no rotations at all.
- In `btree.py`, set `min_degree=2`. Each node holds at most 3 keys, the fan-out collapses, and you can watch the height climb.
- In `heap.py`, make `top_k` return the K *smallest* items. Work out which way the heap needs to be ordered before you change anything.
