"""Module 3 - A basic tree, walked with DFS and BFS.

Run:  python3 tree.py

Each node holds an int and a list of children:

            1
          / | \\
         2  3  4
        / \\     \\
       5   6     7

DFS (depth-first) goes all the way down one branch before trying the next.
BFS (breadth-first) visits the tree level by level.

The two traversals are the same loop. DFS takes the NEWEST node from a stack;
BFS takes the OLDEST node from a queue.

A plain tree has no ordering rule (unlike a BST), so:
  * insert needs to be told which parent the new node goes under
  * find has to search the whole tree: O(n)
"""

from __future__ import annotations

from collections import deque


class Node:
    def __init__(self, value: int) -> None:
        self.value = value
        self.children: list[Node] = []


class Tree:
    def __init__(self, root_value: int) -> None:
        self.root = Node(root_value)

    def insert(self, value: int, parent_value: int) -> Node:
        """Add `value` as a new child of the node holding `parent_value`."""
        parent = self.find(parent_value)
        if parent is None:
            raise ValueError(f"no node with value {parent_value}")
        child = Node(value)
        parent.children.append(child)
        return child

    def find(self, value: int) -> Node | None:
        """Return the first node holding `value` (BFS order), or None."""
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            if node.value == value:
                return node
            queue.extend(node.children)
        return None

    def dfs(self) -> list[int]:
        """Depth-first: follow one branch to the bottom before trying the next."""
        order = []

        # The stack holds nodes we've discovered but not visited yet.
        # A stack is last-in, first-out: the most recently added node
        # comes off first.
        stack = [self.root]

        while stack:
            # Take the NEWEST node. Its children were pushed after its
            # siblings, so they come off before the siblings do. That is
            # what makes the walk go deep before it goes wide.
            node = stack.pop()
            order.append(node.value)

            # Push the children so they get visited next. Reversed, so
            # that the first child ends up on top and is popped first,
            # which visits children left to right.
            #   at node 1: stack = [4, 3, 2]  -> pop 2
            #   at node 2: stack = [4, 3, 6, 5] -> pop 5, then 6, then 3...
            stack.extend(reversed(node.children))

        return order

    def bfs(self) -> list[int]:
        """Breadth-first: visit every node on one level before the next level."""
        order = []

        # The queue holds nodes we've discovered but not visited yet.
        # A queue is first-in, first-out: nodes come off in the order
        # they were added. deque makes popleft() O(1); list.pop(0) is O(n).
        queue = deque([self.root])

        while queue:
            # Take the OLDEST node. Everything on the current level was
            # added before any of its children, so the whole level is
            # visited before the next level starts.
            node = queue.popleft()
            order.append(node.value)

            # Add the children to the back of the line. They wait behind
            # the rest of the current level.
            #   at node 1: queue = [2, 3, 4]
            #   at node 2: queue = [3, 4, 5, 6] -> 3 and 4 go before 5 and 6
            queue.extend(node.children)

        return order


if __name__ == "__main__":
    tree = Tree(1)
    tree.insert(2, parent_value=1)
    tree.insert(3, parent_value=1)
    tree.insert(4, parent_value=1)
    tree.insert(5, parent_value=2)
    tree.insert(6, parent_value=2)
    tree.insert(7, parent_value=4)

    print("DFS:", tree.dfs())  # [1, 2, 5, 6, 3, 4, 7]
    print("BFS:", tree.bfs())  # [1, 2, 3, 4, 5, 6, 7]

    print("find(6):", tree.find(6) is not None)  # True
    print("find(9):", tree.find(9) is not None)  # False
