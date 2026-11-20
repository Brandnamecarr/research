"""Module 5 - Dynamic programming as caching over a state space.

Run:  python3 dynamic_programming.py

The problem: edit distance. How many single-character inserts, deletes, or
substitutions turn string `a` into string `b`? (It powers "did you mean?",
fuzzy matching, and diff tools.)

The same recurrence is solved four ways, and only the bookkeeping changes:

  1. Naive recursion      - exponential: re-solves the same subproblems.
  2. Memoized recursion   - a cache keyed by the subproblem's state.
  3. Bottom-up table      - the same cache, filled in dependency order.
  4. Two rows             - evict cache entries nothing will read again.

The state is the pair (i, j): "the distance between a[i:] and b[j:]".
There are only (len(a) + 1) * (len(b) + 1) distinct states. The naive
recursion makes millions of calls, but almost all of them repeat a state that
was already solved. Dynamic programming is noticing that and solving each
state once.
"""

from __future__ import annotations


def edit_distance_naive(a: str, b: str) -> tuple[int, int]:
    """Return (distance, calls made). Exponential time."""
    calls = 0

    def solve(i: int, j: int) -> int:
        nonlocal calls
        calls += 1
        if i == len(a):
            return len(b) - j  # a is used up: insert the rest of b
        if j == len(b):
            return len(a) - i  # b is used up: delete the rest of a
        return min(
            solve(i + 1, j) + 1,                    # delete a[i]
            solve(i, j + 1) + 1,                    # insert b[j]
            solve(i + 1, j + 1) + (a[i] != b[j]),   # substitute (free if equal)
        )

    return solve(0, 0), calls


def edit_distance_memo(a: str, b: str) -> tuple[int, int, int]:
    """Return (distance, states solved, cache hits). O(len(a) * len(b)).

    Identical to the naive version except for the cache. The answer for a
    state depends only on (i, j), never on how the recursion got there, and
    that is what makes it safe to reuse.
    """
    cache: dict[tuple[int, int], int] = {}
    hits = 0

    def solve(i: int, j: int) -> int:
        nonlocal hits
        if (i, j) in cache:
            hits += 1
            return cache[(i, j)]
        if i == len(a):
            result = len(b) - j
        elif j == len(b):
            result = len(a) - i
        else:
            result = min(
                solve(i + 1, j) + 1,
                solve(i, j + 1) + 1,
                solve(i + 1, j + 1) + (a[i] != b[j]),
            )
        cache[(i, j)] = result
        return result

    return solve(0, 0), len(cache), hits


def edit_distance_table(a: str, b: str) -> list[list[int]]:
    """Fill the whole state space bottom-up and return the table.

    table[i][j] = distance between the first i characters of a and the first
    j characters of b. (Prefixes instead of suffixes: the same idea, indexed
    so the table fills top-left to bottom-right.) Each cell reads only its
    left, upper, and upper-left neighbours, so filling row by row guarantees
    every dependency is ready before it is needed. No recursion, no cache
    misses: the loop order IS the dependency order.
    """
    rows, columns = len(a) + 1, len(b) + 1
    table = [[0] * columns for _ in range(rows)]
    for i in range(rows):
        table[i][0] = i  # turning i characters into nothing: i deletes
    for j in range(columns):
        table[0][j] = j  # turning nothing into j characters: j inserts

    for i in range(1, rows):
        for j in range(1, columns):
            table[i][j] = min(
                table[i - 1][j] + 1,                            # delete
                table[i][j - 1] + 1,                            # insert
                table[i - 1][j - 1] + (a[i - 1] != b[j - 1]),   # substitute
            )
    return table


def edit_distance(a: str, b: str) -> int:
    """The production version: O(len(a) * len(b)) time, O(len(b)) memory.

    A cell only reads the current row and the row above it. Older rows will
    never be read again, so they do not need to exist. Keeping two rows turns
    O(n * m) memory into O(m).
    """
    previous = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        current = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            current[j] = min(
                previous[j] + 1,
                current[j - 1] + 1,
                previous[j - 1] + (a[i - 1] != b[j - 1]),
            )
        previous = current
    return previous[-1]


def closest_match(word: str, candidates: list[str]) -> tuple[str, int]:
    """The candidate with the smallest edit distance to `word`."""
    return min(((c, edit_distance(word, c)) for c in candidates), key=lambda pair: pair[1])


if __name__ == "__main__":
    a, b = "intention", "execution"
    states = (len(a) + 1) * (len(b) + 1)

    print(f"1. Edit distance from {a!r} to {b!r}  ({states} distinct states)")
    distance, calls = edit_distance_naive(a, b)
    print(f"  naive recursion : distance {distance}, {calls:>9,} calls")
    distance, solved, hits = edit_distance_memo(a, b)
    print(f"  memoized        : distance {distance}, {solved:>9,} states solved, {hits} cache hits")
    print(f"  two-row table   : distance {edit_distance(a, b)}")

    print("\n2. The full table for 'kitten' -> 'sitting' (answer is bottom-right)")
    a, b = "kitten", "sitting"
    table = edit_distance_table(a, b)
    print("        " + "  ".join(b))
    for label, row in zip(" " + a, table):
        print(f"  {label}  " + "  ".join(str(cell) for cell in row))

    print("\n3. 'Did you mean?' for a mistyped command")
    commands = ["status", "start", "stop", "restart", "stash", "stage"]
    for typo in ["statsu", "restrat", "stach"]:
        match, distance = closest_match(typo, commands)
        print(f"  {typo!r:<10} -> {match!r} (distance {distance})")
