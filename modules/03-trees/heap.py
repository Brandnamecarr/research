"""Module 3 - A binary heap, and the two jobs it does best.

Run:  python3 heap.py

A heap answers one question fast: "what is the smallest item right now?"
It keeps a much weaker rule than a search tree:

    every parent  <=  both of its children

That is enough to guarantee the minimum sits at the root, and cheap to
maintain, because siblings are never compared or ordered with each other.

The tree is always completely filled level by level, so it needs no node
objects or pointers. It lives in a flat array and the links are arithmetic:

    index:    0   1   2   3   4   5   6
    tree:     root
              |- 1 and 2 are its children
                  |- 3,4 belong to 1;  5,6 belong to 2

    parent(i) = (i - 1) // 2      children(i) = 2i + 1  and  2i + 2

Python ships this as the `heapq` module; it is built by hand here to show the
mechanics. Use `heapq` in real code.
"""

from __future__ import annotations

from typing import Iterable, Iterator


class MinHeap:
    def __init__(self) -> None:
        self._items: list = []

    def __len__(self) -> int:
        return len(self._items)

    def peek(self):
        """The smallest item, without removing it: O(1)."""
        return self._items[0]

    def push(self, item) -> None:
        """Add at the bottom, then swap upward until the parent is smaller.

        The item climbs at most one level per swap, and the tree has log2(n)
        levels, so this is O(log n).
        """
        items = self._items
        items.append(item)
        child = len(items) - 1
        while child > 0:
            parent = (child - 1) // 2
            if not items[child] < items[parent]:
                break
            items[child], items[parent] = items[parent], items[child]
            child = parent

    def pop(self):
        """Remove and return the smallest item: O(log n).

        Taking the root leaves a hole. Fill it with the LAST item (which keeps
        the array gap-free), then swap that item downward, always with its
        smaller child, until it is no larger than both children.
        """
        items = self._items
        smallest = items[0]
        last = items.pop()
        if items:
            items[0] = last
            parent, size = 0, len(items)
            while True:
                left, right = 2 * parent + 1, 2 * parent + 2
                candidate = parent
                if left < size and items[left] < items[candidate]:
                    candidate = left
                if right < size and items[right] < items[candidate]:
                    candidate = right
                if candidate == parent:
                    break
                items[parent], items[candidate] = items[candidate], items[parent]
                parent = candidate
        return smallest

    def as_list(self) -> list:
        return list(self._items)


def top_k(stream: Iterable, k: int) -> list:
    """The k largest items of a stream, using O(k) memory.

    Sorting everything would need the whole stream in memory: O(n) space and
    O(n log n) time. Instead keep a min-heap of the best k seen so far. Its
    root is the WEAKEST of the current top k, so a new item only has to beat
    the root to get in. Time is O(n log k); memory never exceeds k items,
    however long the stream runs.
    """
    heap = MinHeap()
    for item in stream:
        if len(heap) < k:
            heap.push(item)
        elif item > heap.peek():
            heap.pop()
            heap.push(item)
    return sorted(heap.as_list(), reverse=True)


def merge_sorted(streams: list[Iterable]) -> Iterator:
    """Merge k sorted streams into one sorted stream, lazily.

    The next output item must be the head of one of the k streams. A heap
    holding just those k heads finds the smallest in O(log k), so merging n
    items in total costs O(n log k) and holds only k items in memory at once.
    """
    iterators = [iter(stream) for stream in streams]
    heap = MinHeap()
    for stream_id, iterator in enumerate(iterators):
        first = next(iterator, None)
        if first is not None:
            # (value, stream_id): the id says which stream to refill from, and
            # breaks ties so equal values never compare anything further.
            heap.push((first, stream_id))

    while len(heap):
        value, stream_id = heap.pop()
        yield value
        following = next(iterators[stream_id], None)
        if following is not None:
            heap.push((following, stream_id))


if __name__ == "__main__":
    print("1. The heap as a flat array")
    heap = MinHeap()
    for priority in [50, 30, 40, 10, 20, 5]:
        heap.push(priority)
        print(f"  push {priority:>2} -> {heap.as_list()}")
    print(f"  pops come out sorted: {[heap.pop() for _ in range(len(heap))]}")

    print("\n2. Top 3 slowest requests from a latency stream (ms)")
    latencies_ms = [12, 480, 33, 9, 1250, 41, 87, 15, 902, 26, 310, 18]
    print(f"  {top_k(latencies_ms, 3)}")

    print("\n3. Merging three sorted log shards by timestamp")
    shard_a = [(1, "a: boot"), (4, "a: ready"), (9, "a: request")]
    shard_b = [(2, "b: boot"), (3, "b: ready"), (8, "b: request")]
    shard_c = [(5, "c: boot"), (6, "c: ready"), (7, "c: request")]
    for timestamp, line in merge_sorted([shard_a, shard_b, shard_c]):
        print(f"  t={timestamp}  {line}")
