"""Module 5 - Two pointers: one pass instead of nested loops.

Run:  python3 two_pointers.py

The brute-force way to relate items in a sequence is a loop inside a loop:
O(n^2). Two pointers gets the same answer in a single O(n) pass by using
some structure in the data (usually sort order) to prove that most pairs
never need to be looked at. Each pointer only ever moves forward, so the
total work is bounded by the length of the input.

Three shapes of the pattern:

  1. Converging:    one pointer at each end, moving toward each other.
  2. Parallel:      one pointer in each of two sequences (a merge).
  3. Reader/writer: both in the same sequence, one ahead of the other.
"""

from __future__ import annotations


def pair_with_sum(sorted_values: list[int], target: int) -> "tuple[int, int] | None":
    """Find two values that add up to `target` in a sorted list.

    Start with the smallest and the largest. If their sum is too small, the
    smallest value cannot pair with ANYTHING (it was already paired with the
    largest available), so discard it by moving `left` up. If the sum is too
    big, the same argument discards the largest. Every step eliminates one
    value for good, so there are at most n steps.
    """
    left, right = 0, len(sorted_values) - 1
    while left < right:
        total = sorted_values[left] + sorted_values[right]
        if total == target:
            return sorted_values[left], sorted_values[right]
        if total < target:
            left += 1
        else:
            right -= 1
    return None


def intersect_sorted(a: list[int], b: list[int]) -> list[int]:
    """Values present in both sorted lists: O(len(a) + len(b)), O(1) extra space.

    Compare the two heads. The smaller one cannot appear later in the other
    list (everything there is larger still), so advance past it. Equal heads
    are a match. This is a sort-merge join in miniature.
    """
    matches = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            matches.append(a[i])
            i += 1
            j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return matches


def dedupe_sorted_in_place(values: list[int]) -> int:
    """Remove duplicates from a sorted list without allocating a second list.

    `read` scans every element; `write` marks the end of the cleaned region.
    Everything before `write` is final. Because `write` never overtakes
    `read`, compacted values only overwrite slots that were already read.
    Returns the new length; the list is truncated to it.
    """
    if not values:
        return 0
    write = 1
    for read in range(1, len(values)):
        if values[read] != values[write - 1]:  # a value not yet kept
            values[write] = values[read]
            write += 1
    del values[write:]
    return write


if __name__ == "__main__":
    print("1. Converging: two jobs that exactly fill a 64 GB node")
    job_memory_gb = [4, 8, 12, 20, 24, 32, 44, 48]
    print(f"  jobs: {job_memory_gb}")
    print(f"  pair: {pair_with_sum(job_memory_gb, 64)}")

    print("\n2. Parallel: user IDs matching BOTH index lookups")
    users_in_region = [3, 8, 15, 21, 42, 57, 63, 90]
    users_on_paid_plan = [8, 9, 21, 22, 57, 58, 90, 91]
    print(f"  region = eu : {users_in_region}")
    print(f"  plan = paid : {users_on_paid_plan}")
    print(f"  both        : {intersect_sorted(users_in_region, users_on_paid_plan)}")

    print("\n3. Reader/writer: compact a sorted batch of event IDs in place")
    event_ids = [101, 101, 102, 103, 103, 103, 104, 107, 107]
    print(f"  before: {event_ids}")
    kept = dedupe_sorted_in_place(event_ids)
    print(f"  after : {event_ids}  ({kept} kept)")
