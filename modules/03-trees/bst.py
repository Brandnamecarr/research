"""Module 3 - Binary search trees, and why they must be kept balanced.

Run:  python3 bst.py

A binary search tree keeps one rule at every node:

    everything in the left subtree  <  node.key  <  everything in the right subtree

So a search discards one whole subtree per step, and the cost of every
operation is the HEIGHT of the tree. Height is the number that matters:

    balanced tree of n keys  -> height ~ log2(n)   (1,000,000 keys: about 20)
    degenerate tree          -> height = n         (a linked list in disguise)

A plain BST has no control over its height: the insertion order decides it.
An AVL tree adds a repair step (rotations) after each insert to keep the two
sides of every node within one level of each other.
"""

from __future__ import annotations

import random
from collections import deque
from typing import Iterator


class Node:
    __slots__ = ("key", "left", "right", "height")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: "Node | None" = None
        self.right: "Node | None" = None
        self.height = 1  # height of the subtree rooted here; used by AVL only


# ---------------------------------------------------------------------------
# Plain BST: no balancing
# ---------------------------------------------------------------------------

def bst_insert(root: "Node | None", key: int) -> Node:
    """Walk down, going left or right at each node, and attach a new leaf.

    Written as a loop rather than recursion so that a degenerate (very deep)
    tree cannot overflow Python's call stack.
    """
    if root is None:
        return Node(key)
    node = root
    while True:
        if key < node.key:
            if node.left is None:
                node.left = Node(key)
                break
            node = node.left
        elif key > node.key:
            if node.right is None:
                node.right = Node(key)
                break
            node = node.right
        else:
            break  # duplicate key: nothing to do
    return root


def search(root: "Node | None", key: int) -> tuple[bool, int]:
    """Return (found, nodes visited). Works for both tree types."""
    node, visited = root, 0
    while node is not None:
        visited += 1
        if key == node.key:
            return True, visited
        node = node.left if key < node.key else node.right
    return False, visited


def range_scan(root: "Node | None", low: int, high: int) -> Iterator[int]:
    """Yield the keys in [low, high] in sorted order.

    In-order traversal (left subtree, node, right subtree) visits a BST in
    sorted order. This version also skips subtrees that cannot contain keys
    in range, so the cost is O(height + results), not O(n). Hash maps cannot
    do this at all: hashing destroys the ordering.
    """
    stack: list[Node] = []
    node = root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            # Keys to the left are smaller; skip them once we are at or below `low`.
            node = node.left if node.key > low else None
        node = stack.pop()
        if node.key > high:
            return  # everything from here on is larger still
        if node.key >= low:
            yield node.key
        node = node.right


def tree_height(root: "Node | None") -> int:
    """Count levels with a breadth-first walk (safe for very deep trees)."""
    levels, queue = 0, deque([root] if root else [])
    while queue:
        levels += 1
        for _ in range(len(queue)):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return levels


# ---------------------------------------------------------------------------
# AVL tree: a BST that repairs its own shape
# ---------------------------------------------------------------------------

def _height(node: "Node | None") -> int:
    return node.height if node else 0


def _refresh(node: Node) -> None:
    node.height = 1 + max(_height(node.left), _height(node.right))


def _rotate_right(top: Node) -> Node:
    """Lift the left child up; the old top becomes its right child.

            top                pivot
           /   \\              /     \\
        pivot   C     ->      A      top
        /   \\                       /   \\
       A     B                     B     C

    Three pointers change. The left-to-right order A, pivot, B, top, C is
    exactly the same before and after, so the search rule still holds; the
    tree is simply one level shorter on its heavy side.
    """
    pivot = top.left
    top.left = pivot.right
    pivot.right = top
    _refresh(top)
    _refresh(pivot)
    return pivot


def _rotate_left(top: Node) -> Node:
    """Mirror image of _rotate_right: lift the right child up."""
    pivot = top.right
    top.right = pivot.left
    pivot.left = top
    _refresh(top)
    _refresh(pivot)
    return pivot


def avl_insert(node: "Node | None", key: int) -> Node:
    """Insert like a BST, then rebalance every node on the way back up.

    Recursion is safe here: the tree is balanced, so the depth is ~log2(n).
    """
    if node is None:
        return Node(key)
    if key < node.key:
        node.left = avl_insert(node.left, key)
    elif key > node.key:
        node.right = avl_insert(node.right, key)
    else:
        return node

    _refresh(node)
    balance = _height(node.left) - _height(node.right)

    if balance > 1:  # left side is two levels taller
        if key > node.left.key:  # the new key went left-then-right: straighten it first
            node.left = _rotate_left(node.left)
        return _rotate_right(node)
    if balance < -1:  # right side is two levels taller
        if key < node.right.key:  # right-then-left
            node.right = _rotate_right(node.right)
        return _rotate_left(node)
    return node


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def build(insert, keys) -> "Node | None":
    root = None
    for key in keys:
        root = insert(root, key)
    return root


if __name__ == "__main__":
    count = 1_023  # 2^10 - 1: a perfectly balanced tree would be 10 levels
    sorted_keys = list(range(count))
    shuffled_keys = sorted_keys[:]
    random.Random(7).shuffle(shuffled_keys)

    trees = [
        ("plain BST, random insert order", build(bst_insert, shuffled_keys)),
        ("plain BST, sorted insert order", build(bst_insert, sorted_keys)),
        ("AVL tree,  sorted insert order", build(avl_insert, sorted_keys)),
    ]

    print(f"1. Same {count:,} keys, three trees")
    print(f"  {'tree':<34}{'height':>8}{'avg nodes visited per lookup':>31}")
    for label, root in trees:
        average = sum(search(root, key)[1] for key in sorted_keys) / count
        print(f"  {label:<34}{tree_height(root):>8,}{average:>31.1f}")

    print("\n2. Range scan on the AVL tree: keys between 500 and 510")
    print(f"  {list(range_scan(trees[2][1], 500, 510))}")
