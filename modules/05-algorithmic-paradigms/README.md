# Module 5: Algorithmic paradigms

> A paradigm is a reusable way of avoiding redundant work. Each of these three removes a different kind of repetition.

Previous: [Module 4, graphs](../04-graphs/README.md) · [Back to the curriculum](../README.md)

| Paradigm | The redundant work it removes | Typical gain |
|---|---|---|
| Two pointers | Comparing pairs that sort order already rules out | O(n²) to O(n) |
| Sliding window | Recomputing the part of a window that did not change | O(n · w) to O(n) |
| Dynamic programming | Re-solving a subproblem that was already solved | Exponential to polynomial |

## 1. Core conceptual model

### Two pointers

The brute-force way to relate items in a sequence is a loop inside a loop, which looks at every pair. Two pointers reaches the same answer in one pass by using structure in the data, almost always **sort order**, to prove that most pairs never need checking.

The pattern has three shapes:

| Shape | Setup | Example |
|---|---|---|
| Converging | One pointer at each end, moving inward | Find two values that sum to a target |
| Parallel | One pointer in each of two sequences | Merge or intersect two sorted lists |
| Reader/writer | Both in one sequence, one ahead of the other | Remove duplicates in place |

What makes it valid is an **elimination argument**. Take the converging case on a sorted list. If the smallest and largest values sum to less than the target, the smallest value cannot be part of any answer, because it was just paired with the largest partner available. It can be discarded permanently. Each step eliminates one value, so there are at most `n` steps.

The property to look for: **each pointer only ever moves forward.** That bounds the total work by the input length, however the loop is written.

### Sliding window

A window is a contiguous slice of a sequence, such as the last 5 values or the last 60 seconds. Recomputing an aggregate from scratch each time the window moves costs O(window) per step. But consecutive windows overlap almost completely:

```
window at t:      [ a  b  c  d ] e
window at t+1:      a [ b  c  d  e ]
                    ^              ^
                  leaves         enters
```

So keep a running result and apply only the difference: add what entered and remove what left. Each item enters once and leaves once, giving O(n) total and O(window) memory regardless of how long the stream runs.

- **Fixed windows** have a constant size, either by count (the last N items) or by time (the last N seconds).
- **Variable windows** grow on the right and shrink on the left to keep some condition true, such as "spans at most 5 seconds". This is two pointers again: `right` extends, `left` catches up, and neither moves backward.

One limit to know about: the "remove what left" step needs an aggregate that can be undone. Sums and counts can. A maximum cannot, because when the maximum leaves the window you do not know the next largest. Windowed min and max need an extra structure, a deque kept in sorted order.

### Dynamic programming

Dynamic programming (DP) applies when a problem has two properties:

1. **Overlapping subproblems.** Solving it recursively reaches the same smaller problem by many different routes.
2. **Optimal substructure.** The answer to a problem can be assembled from the answers to its subproblems, and each subproblem's answer depends only on the subproblem itself, not on how you arrived at it.

The central concept is **state**: the minimum information that identifies a subproblem. For edit distance between strings `a` and `b`, the state is the pair `(i, j)`, meaning "the distance between the rest of `a` from position `i` and the rest of `b` from position `j`". Two 9-character strings have only 10 × 10 = 100 distinct states, while naive recursion makes over two million calls. Nearly all of those calls repeat a state already solved.

DP solves each state once and stores the answer. There are two ways to organise that:

| | Top-down (memoization) | Bottom-up (tabulation) |
|---|---|---|
| Mechanism | Recursion plus a cache keyed by state | Loops that fill a table in dependency order |
| Computes | Only the states actually reached | Every state |
| Risk | Recursion depth | Must work out the fill order yourself |
| Space optimisation | Hard | Natural: drop rows nothing will read again |

Complexity is always **number of states × work per state**.

A working recipe:

1. **Define the state.** What is the least you need to know to solve the rest?
2. **Write the recurrence.** How does one state's answer follow from smaller states?
3. **Set the base cases.** Which states can be answered directly?
4. **Pick an order** in which every state's dependencies are computed before it.
5. **Trim the memory** to only the states still needed.

Step 1 is the important one. A state must capture everything that future decisions depend on and nothing more, because every extra dimension multiplies the size of the table.

## 2. Systems lens

### Two pointers

- **Sort-merge join.** Given two inputs sorted on the join key, a database joins them in one pass with the parallel-pointer walk in `intersect_sorted`. A hash join must build an in-memory hash table of one side, while a merge join needs almost no memory if the inputs are already sorted, for example because they came out of an index.
- **Search engines.** An inverted index maps each term to a sorted list of document IDs. `python AND kafka` is the intersection of two sorted lists.
- **Merging sorted runs.** The merge step of external sorting and of LSM-tree compaction is the same walk. With many inputs it becomes the heap-based merge from Module 3.
- **In-place compaction.** The reader/writer shape is how a buffer is compacted without allocating a second one, for instance when dropping deleted records.
- **Reconciliation.** Walking two sorted snapshots side by side reports what was added, removed, or changed between them.

The broader point is that sorted data enables streaming algorithms with O(1) memory. That is a large part of why storage systems go to such lengths to keep data sorted.

### Sliding window

- **Rate limiting.** `SlidingWindowRateLimiter` in the sample is the "sliding window log" algorithm. It is exact, and it stores one timestamp per accepted request. Systems with millions of clients often use cheaper approximations, fixed counters per time bucket or a token bucket, because the real cost is window state multiplied by the number of keys.
- **Monitoring and alerting.** "Error rate over the last 5 minutes" and moving averages are windowed aggregates. An exponentially weighted moving average approximates a window with a single stored number.
- **Stream processing.** Tumbling, sliding, and session windows in systems such as Flink and Kafka Streams are this idea, with machinery added for events that arrive late or out of order. The sample assumes ordered timestamps, and real streams do not guarantee that.
- **TCP flow control.** The sender may have only a window's worth of unacknowledged bytes in flight, and the window slides forward as acknowledgements arrive.
- **Rolling hashes.** `rsync` and deduplicating backup tools hash a window of bytes and update that hash in O(1) as the window advances by one byte.

### Dynamic programming

**Memoization is caching, with the same structure as the cache in Module 2.** The key is the state (the function's arguments) and the value is the result. It is safe for the same reason any cache is safe: the result depends only on the key. `functools.lru_cache` is an LRU hash map placed in front of a function. The one thing that makes DP easier than production caching is that subproblem answers never change, so there is no invalidation.

**The subproblems form a DAG, and DP evaluates it in dependency order.** Each state depends on smaller states, and those dependencies cannot loop. Top-down memoization is a depth-first search over that graph with a visited set that also stores results. Bottom-up tabulation processes the same graph in topological order. This is Module 4 again.

**Space optimisation is eviction with perfect knowledge.** A cache has to guess what will be needed again. A DP table knows exactly, so the two-row version of edit distance discards each row at the moment nothing can read it again.

Where it runs in real systems:

- **Query planners.** Choosing the order in which to join tables is a DP over subsets of tables. The state space grows exponentially with the number of tables, so PostgreSQL searches exhaustively only up to a threshold (`geqo_threshold`, 12 by default) and switches to a heuristic search beyond it.
- **Diff tools.** `diff` and `git diff` solve a close relative of edit distance: the longest common subsequence of two files.
- **Fuzzy matching.** "Did you mean?" suggestions and spell-checking use edit distance directly, as do record-linkage and sequence-alignment tools.
- **Shortest paths.** The Bellman-Ford and Floyd-Warshall algorithms are DP over path length and intermediate nodes.
- **Resource allocation.** Packing jobs into a fixed capacity is the knapsack problem.

The limit of DP is the state space. When the state needs many dimensions, the table becomes too large to fill, and systems fall back to greedy or heuristic methods, as the query planner example shows.

## 3. Code

Three samples, each runnable on its own.

### [two_pointers.py](two_pointers.py)

```bash
python3 two_pointers.py
```

```
1. Converging: two jobs that exactly fill a 64 GB node
  jobs: [4, 8, 12, 20, 24, 32, 44, 48]
  pair: (20, 44)

2. Parallel: user IDs matching BOTH index lookups
  region = eu : [3, 8, 15, 21, 42, 57, 63, 90]
  plan = paid : [8, 9, 21, 22, 57, 58, 90, 91]
  both        : [8, 21, 57, 90]

3. Reader/writer: compact a sorted batch of event IDs in place
  before: [101, 101, 102, 103, 103, 103, 104, 107, 107]
  after : [101, 102, 103, 104, 107]  (5 kept)
```

What to notice: none of the three functions contains a nested loop over the data, and none allocates a lookup structure. Trace demo 1 by hand: `4 + 48 = 52` is too small, so 4 is discarded; `8 + 48 = 56`, discard 8; `12 + 48 = 60`, discard 12; `20 + 48 = 68` is too big, so 48 is discarded; `20 + 44 = 64`. Five comparisons, where checking every pair would take up to 28.

### [sliding_window.py](sliding_window.py)

```bash
python3 sliding_window.py
```

```
1. Moving average of request latency (window = 4 requests)
  raw      : [20, 22, 19, 21, 23, 180, 210, 190, 205, 24, 21, 20]
  smoothed : [20, 21, 61, 108, 151, 196, 157, 110, 68]

2. Rate limiter: at most 3 requests per 10 seconds
  t= 0s  allow
  t= 1s  allow
  t= 2s  allow
  t= 3s  REJECT
  t= 9s  REJECT
  t=10s  allow
  ...

3. Busiest 5-second burst in an error log
  error timestamps: [1, 4, 9, 30, 31, 31.5, 32, 33, 34.5, 50, 58, 70]
  -> 6 errors in the 5 s starting at t=30
```

What to notice:

- **Demo 1.** The spike enters the average gradually and leaves gradually. A window smooths, and it also lags. That trade-off applies to every windowed alert.
- **Demo 2.** The request at `t=10` is allowed because the one from `t=0` has just slid out. A fixed-bucket limiter that resets every 10 seconds would instead allow 3 requests at `t=9` and 3 more at `t=10`, a burst of 6 in two seconds. The sliding window does not have that boundary problem.
- **Demo 3.** `busiest_window` evaluates a window ending at every event, and it is still O(n), because `left` never moves backward.

### [dynamic_programming.py](dynamic_programming.py)

```bash
python3 dynamic_programming.py
```

```
1. Edit distance from 'intention' to 'execution'  (100 distinct states)
  naive recursion : distance 5, 2,193,844 calls
  memoized        : distance 5,       100 states solved, 144 cache hits
  two-row table   : distance 5

2. The full table for 'kitten' -> 'sitting' (answer is bottom-right)
        s  i  t  t  i  n  g
     0  1  2  3  4  5  6  7
  k  1  1  2  3  4  5  6  7
  i  2  2  1  2  3  4  5  6
  t  3  3  2  1  2  3  4  5
  t  4  4  3  2  1  2  3  4
  e  5  5  4  3  2  2  3  4
  n  6  6  5  4  3  3  2  3

3. 'Did you mean?' for a mistyped command
  'statsu'   -> 'status' (distance 2)
  'restrat'  -> 'restart' (distance 2)
  'stach'    -> 'stash' (distance 1)
```

What to notice:

- **Demo 1.** 2,193,844 calls against 100 states. `edit_distance_naive` and `edit_distance_memo` contain the same recurrence, and the only difference is the dictionary.
- **Demo 2.** Every cell is computed from the cell to its left, the cell above, and the cell diagonally up-left. Pick any cell and verify it. Since a cell never looks more than one row up, the final `edit_distance` function keeps just two rows.
- **Across the four functions.** The recurrence never changes. The progression from naive to memoized to table to two rows changes only how answers are stored and when they are discarded.

### Experiments to try

- In `two_pointers.py`, pass `pair_with_sum` an unsorted list. It returns wrong answers without raising an error. The elimination argument depends entirely on the sort order.
- In `sliding_window.py`, write `moving_max`. Subtracting the departing value does not work for a maximum, and running into that is the fastest way to see why.
- In `dynamic_programming.py`, call `edit_distance_memo` on two 200-character strings and look at the states-solved count. The cache holds 40,401 entries, where `edit_distance` gets the same answer holding two rows of 201 numbers.
