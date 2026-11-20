"""Module 3 - A B-tree: the structure behind database indexes.

Run:  python3 btree.py

A binary tree stores one key per node, so a million keys need ~20 levels.
On disk every level is a separate page read, and page reads are the expensive
part. A B-tree makes nodes WIDE instead: each node holds many sorted keys and
has one more child than it has keys, so the tree is very shallow.

    one node:   [ 17 | 42 | 88 ]
               /     |    |     \\
            <17   17-42  42-88   >88

Each node is sized to fill one disk page. With hundreds of keys per page,
three or four levels are enough for billions of rows.

Two rules keep the tree balanced (`t` is the "minimum degree"):

  * every node holds between t-1 and 2t-1 keys (the root may hold fewer)
  * all leaves are at the same depth

The tree grows at the ROOT, not at the leaves: when a node overflows it splits
in two and pushes its middle key up into the parent. Only when the root itself
splits does the tree gain a level, and every leaf gets deeper at once.
"""

from __future__ import annotations

import random
from bisect import bisect_left, bisect_right, insort
from typing import Iterator


class BTreeNode:
    __slots__ = ("keys", "children", "leaf")

    def __init__(self, leaf: bool = True) -> None:
        self.keys: list[int] = []            # sorted
        self.children: list[BTreeNode] = []  # len(keys) + 1 of them, unless leaf
        self.leaf = leaf


class BTree:
    def __init__(self, min_degree: int = 64) -> None:
        self.t = min_degree
        self.max_keys = 2 * min_degree - 1
        self.root = BTreeNode()

    def search(self, key: int) -> tuple[bool, int]:
        """Return (found, pages read). One node visited = one page read."""
        node, pages = self.root, 0
        while True:
            pages += 1
            # Inside a node the keys are a sorted array already in memory, so
            # a binary search here is nearly free compared with the page read.
            position = bisect_left(node.keys, key)
            if position < len(node.keys) and node.keys[position] == key:
                return True, pages
            if node.leaf:
                return False, pages
            node = node.children[position]

    def insert(self, key: int) -> None:
        if len(self.root.keys) == self.max_keys:
            # The root is full. Put a new, empty root above it and split the
            # old one. This is the only place the tree gets taller.
            old_root = self.root
            self.root = BTreeNode(leaf=False)
            self.root.children.append(old_root)
            self._split_child(self.root, 0)

        # Walk down to a leaf, splitting any full node met on the way so there
        # is always room in the parent for a key pushed up from below.
        node = self.root
        while not node.leaf:
            position = bisect_right(node.keys, key)
            if len(node.children[position].keys) == self.max_keys:
                self._split_child(node, position)
                if key > node.keys[position]:  # the pushed-up key decides the side
                    position += 1
            node = node.children[position]
        insort(node.keys, key)

    def _split_child(self, parent: BTreeNode, position: int) -> None:
        """Split a full child into two half-full nodes; the middle key moves up.

            parent: [ .. | .. ]                parent: [ .. | M | .. ]
                        |                 ->                /     \\
            full:  [ a b M c d ]                    [ a b ]       [ c d ]
        """
        t = self.t
        full = parent.children[position]
        right = BTreeNode(leaf=full.leaf)
        middle_key = full.keys[t - 1]

        right.keys = full.keys[t:]
        full.keys = full.keys[: t - 1]
        if not full.leaf:
            right.children = full.children[t:]
            full.children = full.children[:t]

        parent.keys.insert(position, middle_key)
        parent.children.insert(position + 1, right)

    def range_scan(self, low: int, high: int) -> Iterator[int]:
        """Yield keys in [low, high] in sorted order.

        Descend to `low`, then read forward. This is why B-trees serve
        `WHERE x BETWEEN a AND b` and `ORDER BY x` so well.
        """

        def walk(node: BTreeNode) -> Iterator[int]:
            position = bisect_left(node.keys, low)
            while True:
                if not node.leaf:
                    yield from walk(node.children[position])
                if position == len(node.keys) or node.keys[position] > high:
                    return
                yield node.keys[position]
                position += 1

        yield from walk(self.root)

    def stats(self) -> tuple[int, int, float]:
        """Return (height, node count, average fill of a node)."""
        height, node = 1, self.root
        while not node.leaf:
            height += 1
            node = node.children[0]

        nodes = keys = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            nodes += 1
            keys += len(node.keys)
            stack.extend(node.children)
        return height, nodes, keys / (nodes * self.max_keys)


def levels_needed(rows: int, fanout: int) -> int:
    """How many levels until `fanout ** levels` covers `rows`."""
    levels, reachable = 0, 1
    while reachable < rows:
        reachable *= fanout
        levels += 1
    return levels


if __name__ == "__main__":
    count = 200_000
    sequential_keys = list(range(count))
    random_keys = sequential_keys[:]
    random.Random(7).shuffle(random_keys)

    print(f"1. {count:,} keys, up to 127 keys per node")
    print(f"  {'insert order':<14}{'height':>8}{'nodes':>8}{'avg fill':>10}")
    trees = {}
    for label, keys in [("random", random_keys), ("sequential", sequential_keys)]:
        tree = BTree(min_degree=64)
        for key in keys:
            tree.insert(key)
        trees[label] = tree
        height, nodes, fill = tree.stats()
        print(f"  {label:<14}{height:>8}{nodes:>8,}{fill:>10.0%}")

    tree = trees["random"]
    found, pages = tree.search(123_456)
    print(f"\n2. Point lookup of 123,456: found={found}, pages read={pages}")
    print(f"   (a balanced binary tree would visit up to {levels_needed(count, 2)} nodes)")

    print("\n3. Range scan 1,000..1,010")
    print(f"  {list(tree.range_scan(1_000, 1_010))}")

    print("\n4. Levels needed as the table grows")
    print(f"  {'rows':>18}{'binary tree':>14}{'B-tree, fanout 500':>22}")
    for rows in [1_000_000, 1_000_000_000, 1_000_000_000_000]:
        print(f"  {rows:>18,}{levels_needed(rows, 2):>14}{levels_needed(rows, 500):>22}")
