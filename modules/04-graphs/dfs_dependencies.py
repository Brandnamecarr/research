"""Module 4 - Depth-first search: dependency ordering and cycle detection.

Run:  python3 dfs_dependencies.py

DFS follows one path as deep as it goes, then backs up and tries the next
branch. The moment it BACKS OUT of a node is the useful one: by then,
everything that node depends on has been fully explored.

    Record nodes as you back out of them   -> a valid build order
                                              (dependencies before dependents)
    Meet a node you are still inside of    -> a cycle

The graph here is directed: `graph[x]` lists what x depends on.

The recursive form below is the clearest way to see the idea. Python's call
stack is limited (about 1,000 frames by default), so for very deep graphs use
an explicit stack as `dependents_of` does, or the standard library's
`graphlib.TopologicalSorter`.
"""

from __future__ import annotations

Graph = dict[str, list[str]]

# Each node is in exactly one of three states during the search.
UNVISITED = 0    # not reached yet
IN_PROGRESS = 1  # entered but not finished: it is on the path we are walking now
DONE = 2         # it and everything below it are fully explored


class CycleError(Exception):
    def __init__(self, cycle: list[str]) -> None:
        super().__init__(" -> ".join(cycle))
        self.cycle = cycle


def build_order(graph: Graph) -> list[str]:
    """Return every node with its dependencies listed before it.

    Raises CycleError (carrying the offending loop) if no such order exists.
    Time O(nodes + edges): every node is entered once, every edge followed once.
    """
    state = {node: UNVISITED for node in graph}
    order: list[str] = []
    path: list[str] = []  # the chain of nodes currently IN_PROGRESS

    def visit(node: str) -> None:
        state[node] = IN_PROGRESS
        path.append(node)

        for dependency in graph.get(node, []):
            dependency_state = state.get(dependency, UNVISITED)
            if dependency_state == IN_PROGRESS:
                # The dependency is already on the current path, so following
                # this edge leads back to where we came from. Slice out the loop.
                raise CycleError(path[path.index(dependency):] + [dependency])
            if dependency_state == UNVISITED:
                visit(dependency)
            # DONE needs no action: it was reached earlier by another route and
            # is already in `order`. This check is also what keeps the search
            # linear when many nodes share a dependency (a "diamond").

        path.pop()
        state[node] = DONE
        order.append(node)  # backing out: all of its dependencies are placed

    for node in graph:  # start from every node so disconnected parts are covered
        if state[node] == UNVISITED:
            visit(node)
    return order


def dependents_of(graph: Graph, changed: str) -> list[str]:
    """Everything that depends on `changed`, directly or through others.

    "What must be rebuilt if X changes?" asks the edges in the opposite
    direction, so flip them first, then collect whatever is reachable.
    This DFS uses an explicit stack instead of recursion.
    """
    used_by: Graph = {}
    for node, dependencies in graph.items():
        for dependency in dependencies:
            used_by.setdefault(dependency, []).append(node)

    reached: set[str] = set()
    stack = [changed]
    while stack:
        node = stack.pop()
        for dependent in used_by.get(node, []):
            if dependent not in reached:
                reached.add(dependent)
                stack.append(dependent)
    return sorted(reached)


if __name__ == "__main__":
    packages: Graph = {
        "web-app": ["api-client", "ui-kit"],
        "api-client": ["http", "auth"],
        "ui-kit": ["design-tokens"],
        "auth": ["http", "crypto"],
        "http": ["sockets"],
        "crypto": [],
        "sockets": [],
        "design-tokens": [],
    }

    print("1. Build order (each package appears after everything it needs)")
    for step, package in enumerate(build_order(packages), start=1):
        needs = ", ".join(packages[package]) or "nothing"
        print(f"  {step}. {package:<14} needs: {needs}")

    print("\n2. What must be rebuilt if `http` changes?")
    print(f"  {dependents_of(packages, 'http')}")

    print("\n3. Add a bad edge: crypto now depends on api-client")
    broken = {**packages, "crypto": ["api-client"]}
    try:
        build_order(broken)
    except CycleError as error:
        print(f"  cycle detected: {error}")
