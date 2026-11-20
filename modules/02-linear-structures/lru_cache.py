"""Module 2 - An LRU cache: a hash map and a doubly linked list working together.

Run:  python3 lru_cache.py

A cache has to do three things quickly:

  * find an entry by key                 -> a hash map does this in O(1)
  * record that an entry was just used   -> needs an ORDER, which a hash map lacks
  * evict the entry unused the longest   -> needs the far end of that order

A doubly linked list keeps the recency order: most recent at the head, least
recent at the tail. Moving a node to the head or dropping the tail is O(1)
if you already hold the node, and the hash map hands you the node. Neither
structure can do the job alone; together every operation is O(1).

    hash map:   key ----------------+
                                    v
    list:  HEAD <-> [newest] <-> [ ... ] <-> [oldest] <-> TAIL
"""

from __future__ import annotations

import random


class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None) -> None:
        self.key = key
        self.value = value
        self.prev: "_Node | None" = None
        self.next: "_Node | None" = None


class LRUCache:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self._nodes: dict[object, _Node] = {}  # key -> its node in the list

        # Sentinel nodes at both ends mean real nodes always have a neighbour
        # on each side, so linking and unlinking never has to check for None.
        self._head = _Node()  # most recently used side
        self._tail = _Node()  # least recently used side
        self._head.next = self._tail
        self._tail.prev = self._head

        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key, default=None):
        node = self._nodes.get(key)
        if node is None:
            self.misses += 1
            return default
        self.hits += 1
        self._unlink(node)        # a read counts as a use,
        self._link_at_head(node)  # so the entry becomes the newest
        return node.value

    def put(self, key, value) -> None:
        node = self._nodes.get(key)
        if node is not None:  # update in place and refresh its recency
            node.value = value
            self._unlink(node)
            self._link_at_head(node)
            return

        if len(self._nodes) >= self.capacity:
            oldest = self._tail.prev  # the tail side is always the LRU entry
            self._unlink(oldest)
            del self._nodes[oldest.key]  # the node stores its key for this line
            self.evictions += 1

        node = _Node(key, value)
        self._nodes[key] = node
        self._link_at_head(node)

    def keys_newest_first(self) -> list:
        keys, node = [], self._head.next
        while node is not self._tail:
            keys.append(node.key)
            node = node.next
        return keys

    # -- linked-list surgery: each is a fixed number of pointer writes, O(1) --

    def _unlink(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _link_at_head(self, node: _Node) -> None:
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node
        self._head.next = node


def demo_mechanics() -> None:
    cache = LRUCache(capacity=3)
    steps = [
        ("put a", lambda: cache.put("a", 1)),
        ("put b", lambda: cache.put("b", 2)),
        ("put c", lambda: cache.put("c", 3)),
        ("get a", lambda: cache.get("a")),      # a becomes the newest
        ("put d", lambda: cache.put("d", 4)),   # full: evicts b, not a
        ("get b", lambda: cache.get("b")),      # miss
    ]
    print(f"  {'operation':<12}newest -> oldest")
    for label, operation in steps:
        operation()
        print(f"  {label:<12}{cache.keys_newest_first()}")
    print(f"  -> hits={cache.hits} misses={cache.misses} evictions={cache.evictions}")


def demo_hit_rate() -> None:
    """Real traffic is skewed: a few keys get most of the requests. That skew
    is why a cache holding a small slice of the data absorbs a large share
    of the reads."""
    rng = random.Random(42)
    key_count, request_count = 1_000, 50_000
    # Zipf-like popularity: the key ranked r is requested in proportion to 1/r.
    weights = [1 / rank for rank in range(1, key_count + 1)]
    requests = rng.choices(range(key_count), weights=weights, k=request_count)

    print(f"  {'cache size':>12}{'% of keys':>11}{'hit rate':>10}")
    for capacity in [10, 50, 100, 500]:
        cache = LRUCache(capacity)
        for key in requests:
            if cache.get(key) is None:
                cache.put(key, f"row-{key}")  # miss: "query the database", then cache it
        print(f"  {capacity:>12}{capacity / key_count:>11.0%}{cache.hits / request_count:>10.0%}")


if __name__ == "__main__":
    print("1. Recency order in a 3-entry cache")
    demo_mechanics()
    print("\n2. Hit rate on skewed traffic (1,000 distinct keys, 50,000 requests)")
    demo_hit_rate()
