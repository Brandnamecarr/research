"""Module 2 - A hash map with separate chaining, built from scratch.

Run:  python3 hash_map.py

The map is an array of buckets. A key's hash picks the bucket, so a lookup
jumps straight to the right slot instead of scanning. Two keys that pick the
same bucket "collide"; here each bucket is a small list (a chain) that holds
every entry that landed there.

Three demos:

  1. A healthy table: short chains, about one comparison per lookup.
  2. Resizing: rare O(n) rehashes that average out to O(1) per insert.
  3. A hostile hash: every key collides and the map degrades to a linear scan.
"""

from __future__ import annotations

from collections import Counter


class HashMap:
    def __init__(self, capacity: int = 8, max_load: float = 0.75) -> None:
        self._buckets: list[list[list]] = [[] for _ in range(capacity)]
        self._size = 0
        self._max_load = max_load

        # Instrumentation for the demos; a real map would not carry these.
        self.comparisons = 0                        # key comparisons in get()
        self.resize_log: list[tuple[int, int]] = []  # (entries moved, new capacity)

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    def _bucket_for(self, key) -> list[list]:
        # hash() turns any key into a big integer; the modulo folds that
        # integer onto the array. This line is the whole trick: computing an
        # index is O(1) no matter how many entries the map holds.
        return self._buckets[hash(key) % len(self._buckets)]

    def put(self, key, value) -> None:
        bucket = self._bucket_for(key)
        for entry in bucket:
            if entry[0] == key:  # key already present: overwrite
                entry[1] = value
                return
        bucket.append([key, value])
        self._size += 1

        # Load factor = entries / buckets. Past the threshold, chains start
        # getting long, so grow the array to spread the entries back out.
        if self._size / len(self._buckets) > self._max_load:
            self._resize()

    def get(self, key, default=None):
        for stored_key, value in self._bucket_for(key):
            self.comparisons += 1
            if stored_key == key:
                return value
        return default

    def delete(self, key) -> bool:
        bucket = self._bucket_for(key)
        for position, entry in enumerate(bucket):
            if entry[0] == key:
                bucket.pop(position)
                self._size -= 1
                return True
        return False

    def _resize(self) -> None:
        """Double the bucket array and re-place every entry.

        Every entry must move because its bucket is `hash % capacity`, and
        the capacity just changed. This is the O(n) spike hiding inside
        "amortized O(1)" inserts.
        """
        old_buckets = self._buckets
        self._buckets = [[] for _ in range(len(old_buckets) * 2)]
        for bucket in old_buckets:
            for entry in bucket:
                self._bucket_for(entry[0]).append(entry)
        self.resize_log.append((self._size, len(self._buckets)))

    def chain_lengths(self) -> list[int]:
        return [len(bucket) for bucket in self._buckets]


class CollidingKey:
    """A key with a broken hash: every instance lands in the same bucket.

    This stands in for a hash-flooding attack, where an attacker who can
    predict the hash function sends keys chosen to collide.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def __hash__(self) -> int:
        return 42

    def __eq__(self, other) -> bool:
        return isinstance(other, CollidingKey) and self.name == other.name


def average_lookup_cost(table: HashMap, keys: list) -> float:
    table.comparisons = 0
    for key in keys:
        table.get(key)
    return table.comparisons / len(keys)


def demo_healthy_table() -> None:
    keys = [f"user:{n}" for n in range(1_000)]
    table = HashMap()
    for key in keys:
        table.put(key, True)

    lengths = table.chain_lengths()
    print(f"  {len(table):,} entries in {table.capacity:,} buckets "
          f"(load factor {len(table) / table.capacity:.2f})")
    print(f"  {'chain length':>14}{'buckets':>10}")
    for length, buckets in sorted(Counter(lengths).items()):
        print(f"  {length:>14}{buckets:>10,}")
    print(f"  -> average comparisons per lookup: {average_lookup_cost(table, keys):.2f}")


def demo_resizing() -> None:
    table = HashMap()
    for n in range(1_000):
        table.put(f"user:{n}", True)

    print(f"  {'at entry':>10}{'new capacity':>14}{'entries rehashed':>18}")
    for moved, new_capacity in table.resize_log:
        print(f"  {moved:>10,}{new_capacity:>14,}{moved:>18,}")
    total_moved = sum(moved for moved, _ in table.resize_log)
    print(f"  -> {total_moved:,} rehashes spread over {len(table):,} inserts "
          f"= {total_moved / len(table):.2f} extra moves per insert")


def demo_hostile_hash() -> None:
    keys = [CollidingKey(f"user:{n}") for n in range(1_000)]
    table = HashMap()
    for key in keys:
        table.put(key, True)

    print(f"  longest chain: {max(table.chain_lengths()):,} of {len(table):,} entries")
    print(f"  -> average comparisons per lookup: {average_lookup_cost(table, keys):.1f}")


if __name__ == "__main__":
    print("1. Healthy table (string hashes are salted per process, so the exact")
    print("   histogram changes from run to run)")
    demo_healthy_table()
    print("\n2. Resizes while inserting 1,000 entries")
    demo_resizing()
    print("\n3. Every key collides")
    demo_hostile_hash()
