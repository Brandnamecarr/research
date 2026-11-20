"""Module 4 - Breadth-first search: shortest paths by expanding in rings.

Run:  python3 bfs_shortest_path.py

BFS explores a graph in order of distance from the start: first everything
1 hop away, then everything 2 hops away, and so on. A FIFO queue produces
that order for free, because nodes discovered earlier (closer) always leave
the queue before nodes discovered later (farther).

That ordering gives BFS its guarantee: the first time it reaches a node, it
got there by a shortest path (fewest edges). Depth-first search has no such
guarantee; it reports whichever path it happened to dive down first.

The graph is stored as an adjacency list: a dict from each node to the list
of its neighbours. Memory is O(nodes + edges), and "who is next to X?" is a
single dict lookup.
"""

from __future__ import annotations

from collections import deque

Graph = dict[str, list[str]]


def build_graph(links: list[tuple[str, str]]) -> Graph:
    """Turn a list of undirected links into an adjacency list."""
    graph: Graph = {}
    for a, b in links:
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, []).append(a)  # undirected: record both directions
    return graph


def shortest_path(graph: Graph, start: str, goal: str) -> "list[str] | None":
    """Fewest-hops path from start to goal, or None if they are not connected.

    Time O(nodes + edges): each node is queued once, each edge examined once
    from each side.
    """
    # came_from records how each node was first reached. It does two jobs:
    # it is the "visited" set (so cycles cannot trap the search), and it holds
    # the breadcrumbs needed to rebuild the path at the end.
    came_from: dict[str, "str | None"] = {start: None}
    frontier = deque([start])

    while frontier:
        node = frontier.popleft()  # FIFO: closest unexplored node first
        if node == goal:
            path = []
            while node is not None:  # follow the breadcrumbs back to the start
                path.append(node)
                node = came_from[node]
            return path[::-1]
        for neighbour in graph[node]:
            if neighbour not in came_from:
                # Mark on DISCOVERY, not on removal from the queue. Otherwise
                # the same node can be queued once per neighbour that sees it.
                came_from[neighbour] = node
                frontier.append(neighbour)
    return None


def hops_from(graph: Graph, start: str) -> dict[str, int]:
    """Distance in hops from `start` to every node it can reach."""
    distance = {start: 0}
    frontier = deque([start])
    while frontier:
        node = frontier.popleft()
        for neighbour in graph[node]:
            if neighbour not in distance:
                distance[neighbour] = distance[node] + 1
                frontier.append(neighbour)
    return distance


def any_path_dfs(graph: Graph, start: str, goal: str) -> "list[str] | None":
    """A path found depth-first, for contrast: valid, but not always shortest.

    The only real difference from BFS is the container. A stack (LIFO) keeps
    extending the most recent discovery, so the search dives down one branch
    as far as it goes before trying a sibling.
    """
    stack = [[start]]  # each entry is the full path taken to reach its last node
    visited: set[str] = set()
    while stack:
        path = stack.pop()  # LIFO: newest discovery first
        node = path[-1]
        if node == goal:
            return path
        if node in visited:
            continue
        visited.add(node)
        for neighbour in reversed(graph[node]):  # reversed: explore in listed order
            if neighbour not in visited:
                stack.append(path + [neighbour])
    return None


if __name__ == "__main__":
    network = build_graph([
        ("edge-proxy", "auth"),
        ("edge-proxy", "api"),
        ("auth", "sessions"),
        ("sessions", "users-db"),
        ("api", "users-db"),
        ("api", "orders"),
        ("orders", "payments"),
        ("orders", "inventory"),
        ("payments", "ledger-db"),
        ("inventory", "warehouse"),
    ])

    print("1. The adjacency list")
    for node, neighbours in network.items():
        print(f"  {node:<11} -> {neighbours}")

    print("\n2. Path from edge-proxy to users-db")
    bfs_path = shortest_path(network, "edge-proxy", "users-db")
    dfs_path = any_path_dfs(network, "edge-proxy", "users-db")
    print(f"  BFS ({len(bfs_path) - 1} hops): {' -> '.join(bfs_path)}")
    print(f"  DFS ({len(dfs_path) - 1} hops): {' -> '.join(dfs_path)}")

    print("\n3. Blast radius: everything grouped by hops from users-db")
    rings: dict[int, list[str]] = {}
    for node, hops in hops_from(network, "users-db").items():
        rings.setdefault(hops, []).append(node)
    for hops, nodes in rings.items():
        print(f"  {hops} hops: {sorted(nodes)}")
