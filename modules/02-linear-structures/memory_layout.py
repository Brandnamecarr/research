"""Module 2 - Contiguous memory vs pointer-based memory.

Run:  python3 memory_layout.py

Three experiments:

  1. Watch a dynamic array (Python's list) over-allocate as it grows.
  2. Count the bytes per element for three ways of storing the same integers.
  3. Insert at the front of an array vs a linked structure and watch one of
     them go quadratic.
"""

from __future__ import annotations

import struct
import sys
import time
from array import array
from collections import deque

POINTER_BYTES = struct.calcsize("P")  # 8 on a 64-bit machine


class Node:
    """One singly linked list node: a value and a pointer to the next node."""

    __slots__ = ("value", "next")  # no per-instance dict: just the two fields

    def __init__(self, value: int, next: "Node | None" = None) -> None:
        self.value = value
        self.next = next


# ---------------------------------------------------------------------------
# Experiment 1: a dynamic array grows in jumps, not one slot at a time
# ---------------------------------------------------------------------------

def experiment_growth(appends: int = 100) -> None:
    """An array is one contiguous block, so it cannot grow in place if the
    memory after it is taken. Growing means: allocate a bigger block, copy
    everything over, free the old one. That copy is O(n).

    To avoid paying it on every append, the list asks for more room than it
    needs. Most appends then land in a spare slot (O(1)); only the occasional
    append triggers a reallocation. Averaged out, append is "amortized O(1)".
    """
    items: list[int] = []
    empty_bytes = sys.getsizeof(items)
    last_bytes = empty_bytes
    reallocations = 0

    print(f"  {'length':>8}{'capacity':>10}{'spare slots':>13}")
    for value in range(appends):
        items.append(value)
        current_bytes = sys.getsizeof(items)
        if current_bytes != last_bytes:  # the block was reallocated
            capacity = (current_bytes - empty_bytes) // POINTER_BYTES
            print(f"  {len(items):>8}{capacity:>10}{capacity - len(items):>13}")
            last_bytes = current_bytes
            reallocations += 1
    print(f"  -> {appends} appends caused only {reallocations} reallocations")


# ---------------------------------------------------------------------------
# Experiment 2: what one element really costs in each layout
# ---------------------------------------------------------------------------

def experiment_bytes_per_element(count: int = 100_000) -> None:
    values = range(1_000, 1_000 + count)

    # array('q'): the 8-byte integers themselves, packed side by side.
    packed = array("q", values)
    packed_bytes = sys.getsizeof(packed)

    # list: a contiguous array of 8-byte POINTERS. Each pointer leads to a
    # separate int object living somewhere else on the heap.
    boxed = list(values)
    boxed_bytes = sys.getsizeof(boxed) + sum(sys.getsizeof(v) for v in boxed)

    # Linked list: every element is its own node object (value pointer + next
    # pointer + object header) plus the int object it points to.
    head = None
    linked_bytes = 0
    for value in values:
        head = Node(value, head)
        linked_bytes += sys.getsizeof(head) + sys.getsizeof(value)

    print(f"  {'layout':<34}{'total':>10}{'per element':>14}")
    for label, total in [
        ("array('q')  values inline", packed_bytes),
        ("list        pointers -> objects", boxed_bytes),
        ("linked list nodes -> objects", linked_bytes),
    ]:
        print(f"  {label:<34}{total / 1e6:>8.1f}MB{total / count:>11.0f} B")


# ---------------------------------------------------------------------------
# Experiment 3: inserting at the front
# ---------------------------------------------------------------------------

def time_front_inserts(container, insert_front, count: int) -> float:
    start = time.perf_counter()
    for value in range(count):
        insert_front(container, value)
    return time.perf_counter() - start


def experiment_front_insert() -> None:
    """list.insert(0, x) must shift every existing element one slot right to
    keep the block contiguous: O(n) per insert, O(n^2) for n inserts.

    deque is a linked list of small fixed-size blocks, so adding at either
    end only touches the end block: O(1) per insert, O(n) for n inserts.
    """
    print(f"  {'inserts':>10}{'list.insert(0, x)':>20}{'deque.appendleft(x)':>22}")
    timings = []
    for count in [20_000, 40_000]:
        list_seconds = time_front_inserts([], lambda c, v: c.insert(0, v), count)
        deque_seconds = time_front_inserts(deque(), lambda c, v: c.appendleft(v), count)
        timings.append((list_seconds, deque_seconds))
        print(f"  {count:>10,}{list_seconds * 1e3:>17.1f} ms{deque_seconds * 1e3:>19.1f} ms")

    (list_small, deque_small), (list_big, deque_big) = timings
    print(f"  -> doubling the inserts cost the list {list_big / list_small:.1f}x "
          f"and the deque {deque_big / deque_small:.1f}x")


if __name__ == "__main__":
    print("1. Dynamic array growth (a row is printed at each reallocation)")
    experiment_growth()
    print("\n2. Bytes per element for 100,000 integers")
    experiment_bytes_per_element()
    print("\n3. Inserting at the front")
    experiment_front_insert()
