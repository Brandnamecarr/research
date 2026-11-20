# Module 1: Big O, complexity, and scaling limits

> Big O does not tell you how fast code is. It tells you how the cost changes when the input grows.

[Back to the curriculum](../README.md) · Next: [Module 2, linear structures](../02-linear-structures/README.md)

## 1. Core conceptual model

### What Big O measures

Pick a measure of input size, `n` (rows, requests, bytes). Count the basic steps an algorithm takes as a function of `n`. Then keep only the fastest-growing term and drop its constant:

```
3n² + 50n + 1000   →   O(n²)
```

Dropping the rest is justified because at large `n` the dominant term swamps everything else. At `n = 1,000,000` the `3n²` term is 60,000 times bigger than the `50n` term. Dropping the constant is justified because it depends on the machine and the language, while the shape of the curve does not.

So Big O is a statement about a curve's shape. Two O(n) algorithms can differ in speed by 100x. What they share is that doubling the input doubles the cost of each.

### The complexity classes

| Class | The mechanism | When `n` doubles, cost... | Typical source |
|---|---|---|---|
| O(1) | Cost does not depend on `n` | stays the same | Array index, hash lookup |
| O(log n) | Each step discards half of what remains | goes up by one step | Binary search, walking down a balanced tree |
| O(n) | Touch every item once | doubles | Scan, filter, full table scan |
| O(n log n) | Halve the problem log n times, do `n` work per level | slightly more than doubles | Sorting, building an index |
| O(n²) | Compare every item with every other item | quadruples | Nested loops |
| O(2ⁿ) | Try every subset | squares (adding *one* item doubles it) | Brute-force combinatorial search |

### Logarithmic and exponential are mirror images

**Logarithmic** growth is what you get when each step halves the problem. `log₂(n)` is the number of times you can halve `n` before reaching 1. That number stays tiny: `log₂` of a billion is about 30. An O(log n) operation barely notices the difference between a thousand rows and a billion.

**Exponential** growth is the reverse: each additional item doubles the work. Hardware cannot rescue it. A machine twice as fast lets an O(2ⁿ) algorithm handle exactly one more item.

### Time and space are both costs, and you can trade them

Every algorithm has a time complexity and a space (memory) complexity. Often you can spend one to save the other:

- **Spend memory to save time**: keep an index, a cache, a hash set of things already seen, or a precomputed table, so you never recompute or rescan.
- **Spend time to save memory**: stream through data one item at a time, or compress it, instead of holding it all at once.

Most of the structures in the later modules are a specific version of the first trade.

### Worst case, average case, amortized

One operation can have several complexities depending on which case you ask about:

- **Average vs worst case.** A hash lookup is O(1) on average and O(n) when every key collides.
- **Amortized.** Appending to a dynamic array is usually O(1), but occasionally the array is full and the whole thing is copied, which is O(n). Spread over many appends the average is still O(1). "Amortized O(1)" means cheap on average with occasional expensive spikes.

Average cost predicts throughput. Worst-case cost predicts your slowest requests.

### What Big O hides

Big O counts steps as if they all cost the same. In a real system they do not. These are rough orders of magnitude:

| One step is... | Approximate cost |
|---|---|
| A read from CPU cache | 1 ns |
| A read from main memory | 100 ns |
| A random read from SSD | 100 µs |
| A network round trip inside a datacenter | 500 µs |
| A network round trip across continents | 150 ms |

A network round trip costs about as much as half a million cache reads. So an O(n) loop over in-memory data can easily beat an O(log n) algorithm whose steps are network calls. When you analyse a system, **count the most expensive kind of operation**, such as queries, disk reads, or round trips, rather than lines of code.

Also ask "`n` of what?". Real costs often depend on more than one size: O(V + E) for a graph's nodes and edges, O(n · m) for two collections, O(n log k) for `n` items and a heap of size `k`.

## 2. Systems lens

**Finding the bottleneck is finding the dominant term.** In a request path, the cost that grows fastest with data volume eventually dominates everything else. Time spent optimising any other part is wasted until that one is fixed.

**Accidental quadratic behaviour is the most common scaling bug.** It passes every test at `n = 10` (100 steps) and takes the service down at `n = 100,000` (10 billion steps). The usual forms in a Python backend:

| Pattern | Why it is quadratic (or worse) | Fix |
|---|---|---|
| `if x in some_list` inside a loop | Each `in` scans the list: O(n · m) | Make it a `set`: O(n + m) |
| Matching two collections with nested loops | Every pair is compared | Build a `dict` on one side first (this is a hash join) |
| A query inside a loop over rows ("N+1 queries") | `n` network round trips | One `JOIN`, one `IN (...)` batch, or an ORM prefetch |
| `list.pop(0)` or `list.insert(0, x)` in a loop | Each call shifts the whole list | `collections.deque` |

**An index converts O(n) into O(log n).** Without one, the database reads every row. With one, it walks down a tree (Module 3). The price is space for the index and extra work on every write to keep it current. That is a time/space trade and a read/write trade made together.

**A cache is the time/space trade made explicit.** You spend memory to skip recomputation. It introduces new problems, eviction and invalidation, which Module 2 picks up.

**Memory is a harder limit than time.** A slow request is slow. A process that exceeds its memory limit is killed. `file.read()` or `list(cursor)` is O(n) memory, while iterating line by line or row by row is O(1). Prefer generators and streaming for anything whose size you do not control.

**Bigger machines buy a constant factor. Better algorithms buy a complexity class.** A machine twice as fast lets an O(n) job handle 2x the data, an O(n²) job handle 1.4x, and an O(2ⁿ) job handle one more item.

**Tail latency lives in the worst case.** Structures with amortized O(1) operations have periodic O(n) events: an array resize, a hash table rehash, a garbage collection, a compaction. These surface as p99 latency spikes even when the average looks healthy.

**Both curves are useful on purpose.** Exponential backoff uses the steep curve deliberately, so retrying clients back away from an overloaded service very quickly. `git bisect` uses the flat one: finding the bad commit among 1,000 takes about 10 tests.

## 3. Code

[scaling_limits.py](scaling_limits.py) runs four experiments.

```bash
python3 scaling_limits.py
```

### Experiment 1: steps taken as `n` doubles

Each function does real work and counts its steps, so the numbers are exact.

```
               n        O(1)    O(log n)        O(n)  O(n log n)      O(n^2)
             512           1          10         512       4,608     130,816
           1,024           1          11       1,024      10,240     523,776
           2,048           1          12       2,048      22,528   2,096,128
           4,096           1          13       4,096      49,152   8,386,560
x when n doubles        1.00        1.08        2.00        2.18        4.00
```

The last row is each class's signature. Read down the O(log n) column: every doubling of `n` adds exactly one step. This "doubling test" works on real systems too. Double the input, measure again, and the ratio tells you which class you are in without reading any code.

### Experiment 2: the same curves at production scale

Assume one step costs one microsecond.

```
               n      O(log n)          O(n)    O(n log n)        O(n^2)        O(2^n)
              10          3 µs         10 µs         33 µs        100 µs          1 ms
              30          5 µs         30 µs        147 µs        900 µs        18 min
              50          6 µs         50 µs        282 µs          2 ms      36 years
           1,000         10 µs          1 ms         10 ms         1.0 s    > universe
       1,000,000         20 µs         1.0 s        19.9 s     11.6 days    > universe
   1,000,000,000         30 µs        17 min     8.3 hours  31,710 years    > universe
```

Three things to take from this table:

- At `n = 10` every column is fast. Small inputs hide every problem, which is why tests do not catch them.
- O(n²) is fine at a thousand items and unusable at a million.
- O(log n) goes from 3 µs to 30 µs while `n` grows by a factor of 100 million. O(2ⁿ) stops being usable at about `n = 50`.

### Experiment 3: buying time with memory

Two ways to detect duplicates in 4,000 items. Timings vary by machine.

```
  pairwise     229.49 ms   extra memory: none (two loop counters)
  hash set       0.29 ms   extra memory: 160 KB
  -> 785x faster, paid for with memory
```

The pairwise version remembers nothing, so it has to re-compare everything. The hash set version remembers what it has seen, so each item costs one lookup. 160 KB bought a 785x speedup, and the gap widens as `n` grows.

### Experiment 4: exponential work, before and after caching

```
               n     naive calls    cached calls
              10             177              19
              20          21,891              39
              30       2,692,537              59
```

Adding 10 to `n` multiplies the naive call count by about 123. The cached version grows by 20 calls. The exponential cost came entirely from recomputing the same answers. Module 5 builds dynamic programming out of this observation.

### Experiments to try

- Change `sizes` in `experiment_growth` to four larger powers of two and check that the bottom row of ratios does not change.
- In `experiment_time_space`, put a duplicate near the front of the list. Both versions become fast. That is the best case, and it shows why worst-case analysis is the one to plan around.
- Time `fib_naive_calls(35)` and predict how long `fib_naive_calls(45)` would take before deciding whether to run it.
