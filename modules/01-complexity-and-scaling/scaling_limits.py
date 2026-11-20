"""Module 1 - Big O, complexity, and scaling limits.

Run:  python3 scaling_limits.py

Four experiments, each answering one question:

  1. How does the work grow when the input doubles?   (the complexity classes)
  2. What does that growth mean at production scale?  (scaling limits)
  3. Can I buy speed with memory?                     (time/space trade-off)
  4. Why is exponential growth a wall, not a slope?   (and how caching removes it)

Experiments 1 and 4 count steps instead of measuring seconds. Step counts are
exact and identical on every machine, which is the point of Big O: it describes
the shape of the growth, not the speed of the hardware.
"""

from __future__ import annotations

import time
import tracemalloc
from math import log2


# ---------------------------------------------------------------------------
# Experiment 1: count the steps each complexity class takes
# ---------------------------------------------------------------------------

def steps_constant(items: list[int]) -> int:
    """O(1): index into an array. One step, however long the array is."""
    _ = items[len(items) // 2]
    return 1


def steps_logarithmic(items: list[int]) -> int:
    """O(log n): binary search. Every step discards half of what is left."""
    target = items[-1] + 1  # not present, so this is the worst case
    low, high, steps = 0, len(items) - 1, 0
    while low <= high:
        steps += 1
        middle = (low + high) // 2
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return steps


def steps_linear(items: list[int]) -> int:
    """O(n): scan. To prove a value is absent you must look at every item."""
    target = items[-1] + 1
    steps = 0
    for item in items:
        steps += 1
        if item == target:
            break
    return steps


def steps_linearithmic(items: list[int]) -> int:
    """O(n log n): merge sort. log n levels of halving, n writes per level."""
    steps = 0

    def merge_sort(values: list[int]) -> list[int]:
        nonlocal steps
        if len(values) <= 1:
            return values
        middle = len(values) // 2
        left, right = merge_sort(values[:middle]), merge_sort(values[middle:])

        # Merging writes every element of both halves exactly once.
        merged, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        steps += len(merged)
        return merged

    merge_sort(items)
    return steps


def steps_quadratic(items: list[int]) -> int:
    """O(n^2): compare every item with every other item."""
    steps = 0
    for i in range(len(items)):
        for _ in range(i + 1, len(items)):
            steps += 1
    return steps


def experiment_growth() -> None:
    classes = [
        ("O(1)", steps_constant),
        ("O(log n)", steps_logarithmic),
        ("O(n)", steps_linear),
        ("O(n log n)", steps_linearithmic),
        ("O(n^2)", steps_quadratic),
    ]
    sizes = [512, 1024, 2048, 4096]
    rows = [[count(list(range(n))) for _, count in classes] for n in sizes]

    print(f"{'n':>16}" + "".join(f"{name:>12}" for name, _ in classes))
    for n, row in zip(sizes, rows):
        print(f"{n:>16,}" + "".join(f"{steps:>12,}" for steps in row))

    # The ratio between the last two rows is the signature of each class.
    # You can run this "doubling test" against any real system: double the
    # input, measure again, and the ratio tells you the complexity class.
    ratios = [after / before for before, after in zip(rows[-2], rows[-1])]
    print(f"{'x when n doubles':>16}" + "".join(f"{r:>12.2f}" for r in ratios))


# ---------------------------------------------------------------------------
# Experiment 2: project those growth rates onto production-sized inputs
# ---------------------------------------------------------------------------

STEP_SECONDS = 1e-6  # pretend one step costs one microsecond
AGE_OF_UNIVERSE_SECONDS = 4.35e17


def human_duration(seconds: float) -> str:
    if seconds > AGE_OF_UNIVERSE_SECONDS:
        return "> universe"
    if seconds < 1e-3:
        return f"{seconds * 1e6:.0f} µs"
    if seconds < 1:
        return f"{seconds * 1e3:.0f} ms"
    if seconds < 60:
        return f"{seconds:.1f} s"
    if seconds < 3600:
        return f"{seconds / 60:.0f} min"
    if seconds < 86_400:
        return f"{seconds / 3600:.1f} hours"
    if seconds < 365 * 86_400:
        return f"{seconds / 86_400:.1f} days"
    return f"{seconds / (365 * 86_400):,.0f} years"


def experiment_projection() -> None:
    growth = [
        ("O(log n)", lambda n: log2(n)),
        ("O(n)", lambda n: n),
        ("O(n log n)", lambda n: n * log2(n)),
        ("O(n^2)", lambda n: n**2),
        # 2^n overflows everything long before n = 1,000; cap it.
        ("O(2^n)", lambda n: 2**n if n <= 100 else float("inf")),
    ]
    print(f"{'n':>16}" + "".join(f"{name:>14}" for name, _ in growth))
    for n in [10, 30, 50, 1_000, 1_000_000, 1_000_000_000]:
        cells = [human_duration(steps(n) * STEP_SECONDS) for _, steps in growth]
        print(f"{n:>16,}" + "".join(f"{cell:>14}" for cell in cells))


# ---------------------------------------------------------------------------
# Experiment 3: trade memory for time
# ---------------------------------------------------------------------------

def has_duplicates_pairwise(items: list[int]) -> bool:
    """O(n^2) time, O(1) extra space: nothing is remembered, so everything
    has to be re-compared."""
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False


def has_duplicates_hashed(items: list[int]) -> bool:
    """O(n) time, O(n) extra space: remember what has been seen in a hash set,
    so each item costs one O(1) lookup instead of a scan."""
    seen: set[int] = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False


def experiment_time_space() -> None:
    items = list(range(4_000))  # all unique: the worst case for both versions

    start = time.perf_counter()
    has_duplicates_pairwise(items)
    pairwise_seconds = time.perf_counter() - start

    start = time.perf_counter()
    has_duplicates_hashed(items)
    hashed_seconds = time.perf_counter() - start

    # Measure the memory the hash set costs (traced separately so the tracing
    # overhead does not distort the timings above).
    tracemalloc.start()
    has_duplicates_hashed(items)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  pairwise  {pairwise_seconds * 1e3:>9.2f} ms   extra memory: none (two loop counters)")
    print(f"  hash set  {hashed_seconds * 1e3:>9.2f} ms   extra memory: {peak_bytes / 1024:,.0f} KB")
    print(f"  -> {pairwise_seconds / hashed_seconds:,.0f}x faster, paid for with memory")


# ---------------------------------------------------------------------------
# Experiment 4: exponential growth, and removing it by remembering answers
# ---------------------------------------------------------------------------

def fib_naive_calls(n: int) -> int:
    """Count the calls a naive recursive Fibonacci makes: O(2^n).

    fib(n) calls fib(n-1) and fib(n-2), and both of those recompute the same
    smaller values from scratch. The call tree roughly doubles at every level.
    """
    calls = 0

    def fib(k: int) -> int:
        nonlocal calls
        calls += 1
        return k if k < 2 else fib(k - 1) + fib(k - 2)

    fib(n)
    return calls


def fib_memo_calls(n: int) -> int:
    """Same recursion with a cache: O(n). Each distinct input is solved once."""
    calls = 0
    cache: dict[int, int] = {}

    def fib(k: int) -> int:
        nonlocal calls
        calls += 1
        if k < 2:
            return k
        if k not in cache:
            cache[k] = fib(k - 1) + fib(k - 2)
        return cache[k]

    fib(n)
    return calls


def experiment_exponential() -> None:
    print(f"{'n':>16}{'naive calls':>16}{'cached calls':>16}")
    for n in [10, 20, 30]:
        print(f"{n:>16}{fib_naive_calls(n):>16,}{fib_memo_calls(n):>16,}")


if __name__ == "__main__":
    print("1. Steps taken as n doubles")
    experiment_growth()
    print("\n2. Wall-clock time if one step costs 1 microsecond")
    experiment_projection()
    print("\n3. Duplicate detection on 4,000 items: time vs space")
    experiment_time_space()
    print("\n4. Exponential work, before and after caching")
    experiment_exponential()
