"""Module 5 - Sliding window: aggregates over a stream without re-reading it.

Run:  python3 sliding_window.py

A window is a contiguous slice of a sequence: the last 5 values, the last 60
seconds. Recomputing an aggregate from scratch every time the window moves
costs O(window) per step. But consecutive windows overlap almost entirely,
so instead keep a running result and apply only the difference:

    add what just entered  +  remove what just left

Every item enters the window once and leaves once, so the total work is O(n)
for the whole stream, and memory is bounded by the window size no matter how
long the stream runs.

Three windows:

  1. Fixed count:   moving average over the last N values.
  2. Fixed time:    rate limiter over the last N seconds.
  3. Variable size: the busiest N-second burst in a log.
"""

from __future__ import annotations

from collections import deque
from typing import Iterable, Iterator


def moving_average(values: Iterable[float], size: int) -> Iterator[float]:
    """Average of the most recent `size` values, updated in O(1) per value."""
    window: deque[float] = deque()
    total = 0.0
    for value in values:
        window.append(value)  # the new value enters on the right ...
        total += value
        if len(window) > size:
            total -= window.popleft()  # ... and the oldest leaves on the left
        if len(window) == size:
            yield total / size


class SlidingWindowRateLimiter:
    """Allow at most `limit` requests in any `window_seconds` span.

    The window is defined by time, not count, so its length in items varies.
    The deque holds the timestamps of accepted requests, oldest on the left.
    Timestamps arrive in order, so everything expired is at the left end and
    can be dropped without searching.
    """

    def __init__(self, limit: int, window_seconds: float) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._accepted: deque[float] = deque()

    def allow(self, now: float) -> bool:
        # Slide: drop requests that have aged out of the window.
        while self._accepted and self._accepted[0] <= now - self.window_seconds:
            self._accepted.popleft()
        if len(self._accepted) >= self.limit:
            return False
        self._accepted.append(now)
        return True


def busiest_window(timestamps: list[float], window_seconds: float) -> tuple[int, float]:
    """Return (count, start time) of the densest `window_seconds` span.

    `timestamps` must be sorted. `right` extends the window one event at a
    time; `left` advances only as far as needed to keep the span within the
    limit. Neither index ever moves backward, so the scan is O(n) even though
    it considers a window ending at every event.
    """
    best_count, best_start = 0, 0.0
    left = 0
    for right, timestamp in enumerate(timestamps):
        while timestamp - timestamps[left] >= window_seconds:
            left += 1  # shrink from the left until the span fits again
        count = right - left + 1
        if count > best_count:
            best_count, best_start = count, timestamps[left]
    return best_count, best_start


if __name__ == "__main__":
    print("1. Moving average of request latency (window = 4 requests)")
    latencies_ms = [20, 22, 19, 21, 23, 180, 210, 190, 205, 24, 21, 20]
    print(f"  raw      : {latencies_ms}")
    print(f"  smoothed : {[round(avg) for avg in moving_average(latencies_ms, 4)]}")

    print("\n2. Rate limiter: at most 3 requests per 10 seconds")
    limiter = SlidingWindowRateLimiter(limit=3, window_seconds=10)
    for second in [0, 1, 2, 3, 9, 10, 11, 12, 13, 25]:
        verdict = "allow" if limiter.allow(second) else "REJECT"
        print(f"  t={second:>2}s  {verdict}")

    print("\n3. Busiest 5-second burst in an error log")
    error_times = [1, 4, 9, 30, 31, 31.5, 32, 33, 34.5, 50, 58, 70]
    count, start = busiest_window(error_times, 5)
    print(f"  error timestamps: {error_times}")
    print(f"  -> {count} errors in the 5 s starting at t={start}")
