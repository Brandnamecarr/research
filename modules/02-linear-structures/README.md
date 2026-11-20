# Module 2: Linear structures

> There are two ways to lay data out in memory: side by side, or scattered and linked by pointers. Almost every performance property of a data structure follows from which one it uses.

Previous: [Module 1, complexity](../01-complexity-and-scaling/README.md) · [Back to the curriculum](../README.md) · Next: [Module 3, trees](../03-trees/README.md)

## 1. Core conceptual model

### Arrays: contiguous memory

An array is one unbroken block of memory holding equal-sized slots.

```
address:   1000   1008   1016   1024   1032
          +------+------+------+------+------+
          |  a   |  b   |  c   |  d   |  e   |
          +------+------+------+------+------+
index:       0      1      2      3      4
```

Because the slots are the same size and adjacent, the address of element `i` is arithmetic: `base + i × slot_size`. That is why indexing is O(1) regardless of length. Nothing is searched.

The same property makes changes expensive. To insert in the middle, every later element has to shift one slot to keep the block unbroken: O(n). Only the end is cheap.

**Dynamic arrays** (Python's `list`) grow by over-allocating. When the block is full, the list allocates a larger one, copies everything across, and leaves spare slots at the end. Most appends land in a spare slot; a few trigger a copy. The average works out to amortized O(1).

One Python-specific detail matters for memory: a `list` is a contiguous array of **pointers**. The objects themselves live elsewhere on the heap. `array.array`, `bytes`, and NumPy arrays store the values inline.

### Linked lists: pointer-based memory

A linked list scatters its elements across memory. Each node holds a value and the address of the next node.

```
 +---+------+      +---+------+      +---+------+
 | a | next-+----->| b | next-+----->| c | None |
 +---+------+      +---+------+      +---+------+
```

Inserting or removing a node means rewriting one or two pointers. Nothing shifts, so it is O(1) *if you already hold the node*. Reaching the i-th element means following `i` pointers: O(n). A doubly linked list adds a `prev` pointer, so a node can be unlinked without knowing what came before it.

| Operation | Array | Linked list |
|---|---|---|
| Read element `i` | O(1) | O(n) |
| Append at the end | amortized O(1) | O(1) with a tail pointer |
| Insert or remove at the front | O(n) | O(1) |
| Insert or remove in the middle, position known | O(n) shift | O(1) |
| Memory per element | the element | the element, 1 or 2 pointers, allocator overhead |
| Memory access pattern | sequential | scattered |

**Stacks and queues** are interfaces over these layouts. A stack only touches one end, so an array is ideal. A queue adds at one end and removes at the other, so it needs something cheap at both: a linked structure or a ring buffer. Python's `collections.deque` is a hybrid, a doubly linked list of 64-slot arrays.

### Hash tables

A hash table is an array plus a function that turns a key into an index.

```
key  ──hash()──>  big integer  ──% capacity──>  bucket index
```

Computing an index does not depend on how many entries exist, so lookup, insert, and delete are O(1) on average.

**Collisions** are unavoidable, since there are more possible keys than buckets. There are two ways to resolve them:

| | Separate chaining | Open addressing |
|---|---|---|
| Mechanism | Each bucket holds a small list of entries | Every entry lives in the array itself; on a collision, probe for another free slot |
| Memory | An extra allocation and pointer per entry | Compact, no per-entry allocations |
| Cache behaviour | Follows a pointer per lookup | Probes adjacent slots, which is cache-friendly |
| Under high load | Degrades gradually as chains lengthen | Degrades sharply; needs more empty slots |
| Deleting | Remove from the chain | Needs "tombstone" markers so probe sequences stay intact |
| Used by | Java's `HashMap` | CPython's `dict` |

**Load factor** is entries divided by buckets. As it rises, collisions rise, so past a threshold the table allocates a bigger array and re-places every entry. Every entry must move because its bucket is `hash % capacity` and the capacity changed. That rehash is O(n), and it is the spike inside "amortized O(1)". CPython's `dict` resizes at two-thirds full.

**What a hash table gives up is order.** Hashing deliberately scatters keys, so there is no "next key", no sorted iteration, and no range query. (Python dicts remember insertion order, which is a different thing from key order.) When you need order, you need a tree. That is Module 3.

### A cache is a hash map plus a recency list

A cache needs to find an entry by key, record that it was just used, and evict the entry unused the longest. A hash map does the first but has no order. A doubly linked list keeps an order but cannot find a key. Combined, every operation is O(1):

```
hash map:   key ──────────────┐
                              v
list:   HEAD <-> [newest] <-> [...] <-> [oldest] <-> TAIL
                                           ^
                                      evict from here
```

The map hands you the node. With the node in hand, moving it to the head or dropping the tail is a few pointer writes. This is the LRU (least recently used) cache.

## 2. Systems lens

**The memory hierarchy rewards contiguity.** A CPU loads memory in 64-byte cache lines and prefetches ahead when it detects sequential access. Walking an array of 8-byte integers pulls in 8 values per line, mostly before you ask. Walking a linked list can miss the cache at every hop, at roughly 100 ns each instead of 1 ns. Both are O(n), and the constant can differ by two orders of magnitude. This is the largest thing Big O hides. In Python, interpreter overhead masks much of the effect; it shows fully in C, Rust, Go, and inside NumPy.

**The same rule holds on disk.** Sequential I/O is far cheaper than random I/O. Append-only logs such as Kafka's and a database's write-ahead log are arrays on disk. Columnar formats such as Parquet, Arrow, and NumPy store each column as one contiguous array, which is why analytical scans over them are fast.

**Python's object model multiplies memory.** The experiment below measures 8 bytes per integer in an `array`, 36 in a `list`, and 76 in a linked list. At 100 million integers that is 0.8 GB, 3.6 GB, and 7.6 GB. When a Python service runs out of memory on data that "should fit", this is usually why.

**Pure linked lists are rare. Hybrids are common.** Linked nodes win when you already hold the node and need to splice it in O(1): LRU lists, allocator free lists, kernel scheduling queues. Elsewhere, systems use linked lists *of small arrays* to get cheap ends and good locality together. `deque` does this, and so does Redis for its list type.

**Hash tables are the workhorse.** `dict` and `set`, database hash joins and `GROUP BY` aggregation, the keyspace of Redis and memcached, deduplication, and hash partitioning of data across shards are all the same structure.

**A resize is a latency spike.** Rehashing millions of entries in one step stalls whatever triggered it. Redis avoids this by rehashing incrementally: it keeps the old and new tables side by side and migrates a few buckets on each operation. If you know the final size up front, pre-size the table.

**Predictable hashes are an attack surface.** If an attacker can choose keys that all collide, every operation becomes O(n) and inserting `n` keys costs O(n²), so a small request body can pin a CPU. This is "hash flooding". Python defends against it by salting string hashes with a per-process random seed, which is also why `hash("abc")` differs between runs. Java converts long chains into balanced trees.

**`hash(key) % N` is also how distributed systems place data**, where N is the number of shards or cache nodes. It has the same weakness as an in-memory resize: change N and nearly every key maps somewhere else. In a cache cluster that means almost every key misses at once and the load lands on the database. Consistent hashing exists to fix this; adding a node then moves only about 1/N of the keys.

**Caches work because traffic is skewed.** A few keys receive most requests. In the simulation below, a cache holding 10% of the keys serves 58% of the reads. The costs of LRU are two pointers per entry, and that every *read* also writes to the recency list, which becomes a lock-contention point under concurrency. This is why some systems approximate it. Redis, for example, samples a handful of keys and evicts the oldest of the sample instead of maintaining a list. `functools.lru_cache` uses the same hash-map-plus-linked-list design shown here.

## 3. Code

Three samples, each runnable on its own.

### [memory_layout.py](memory_layout.py): contiguous vs pointer-based

```bash
python3 memory_layout.py
```

```
1. Dynamic array growth (a row is printed at each reallocation)
    length  capacity  spare slots
         1         4            3
         5         8            3
         9        16            7
        17        24            7
        ...
        93       108           15
  -> 100 appends caused only 11 reallocations

2. Bytes per element for 100,000 integers
  layout                                 total   per element
  array('q')  values inline              0.8MB          8 B
  list        pointers -> objects        3.6MB         36 B
  linked list nodes -> objects           7.6MB         76 B

3. Inserting at the front
     inserts   list.insert(0, x)   deque.appendleft(x)
      20,000             43.3 ms                1.2 ms
      40,000            173.3 ms                2.4 ms
  -> doubling the inserts cost the list 4.0x and the deque 2.0x
```

What to notice:

- **Experiment 1.** The list reallocates 11 times in 100 appends, and the spare room grows with the list. That is amortized O(1) in action.
- **Experiment 2.** The same data costs between 8 and 76 bytes per element depending only on layout.
- **Experiment 3.** Apply the doubling test from Module 1. A ratio of 4.0x means front-insertion into a list is quadratic overall; 2.0x means the deque is linear.

### [hash_map.py](hash_map.py): collisions, resizing, and the worst case

```bash
python3 hash_map.py
```

```
1. Healthy table
  1,000 entries in 2,048 buckets (load factor 0.49)
    chain length   buckets
               0     1,247
               1       622
               2       159
               3        20
  -> average comparisons per lookup: 1.22

2. Resizes while inserting 1,000 entries
    at entry  new capacity  entries rehashed
           7            16                 7
          13            32                13
         ...
         769         2,048               769
  -> 1,538 rehashes spread over 1,000 inserts = 1.54 extra moves per insert

3. Every key collides
  longest chain: 1,000 of 1,000 entries
  -> average comparisons per lookup: 500.5
```

What to notice:

- **Demo 1.** Collisions are normal even when the table is half empty: 179 buckets hold more than one entry. They stay cheap because chains stay short. The histogram changes between runs because of the hash salting described above.
- **Demo 2.** A single insert (number 769) moved 769 entries, yet the average over all inserts is 1.54 moves. That is the difference between amortized and worst-case cost.
- **Demo 3.** The same code with a hash function that always returns 42. The map is now a linked list, and a lookup costs 500 comparisons instead of 1.2.

### [lru_cache.py](lru_cache.py): a hash map and a linked list working together

```bash
python3 lru_cache.py
```

```
1. Recency order in a 3-entry cache
  operation   newest -> oldest
  put a       ['a']
  put b       ['b', 'a']
  put c       ['c', 'b', 'a']
  get a       ['a', 'c', 'b']
  put d       ['d', 'a', 'c']
  get b       ['d', 'a', 'c']
  -> hits=1 misses=1 evictions=1

2. Hit rate on skewed traffic (1,000 distinct keys, 50,000 requests)
    cache size  % of keys  hit rate
            10         1%       21%
            50         5%       46%
           100        10%       58%
           500        50%       86%
```

What to notice:

- **Demo 1.** `get a` moves `a` to the front, so when `d` arrives the cache evicts `b`. Reads change the eviction order.
- **Demo 2.** Returns diminish quickly. The first 1% of capacity buys 21 points of hit rate; going from 10% to 50% of all keys buys 28 more. Cache sizing is about finding the knee of this curve.

### Experiments to try

- In `hash_map.py`, raise `max_load` to 5.0 and watch the comparisons per lookup. Then lower it to 0.25 and compare the memory spent on empty buckets.
- In `lru_cache.py`, replace the Zipf weights with uniform ones (`weights=None`). The hit rate falls to roughly the cache's share of the keys. No skew means no benefit from caching.
- In `memory_layout.py`, change experiment 3 to append at the end. The list becomes as fast as the deque.
