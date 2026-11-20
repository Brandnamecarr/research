"""Module 3 - A trie (prefix tree).

Run:  python3 trie.py

In a search tree a node holds a whole key. In a trie a node holds nothing but
its position: the key is spelled out by the PATH from the root, one symbol per
edge. Keys that start the same way share the same nodes.

    "car", "card", "care", "cat"

            (root)
              c
              a
            /   \\
           r*    t*          * = a key ends here
          / \\
         d*  e*

Consequences:

  * lookup cost is the LENGTH OF THE KEY, not the number of keys stored
  * every key with a given prefix lives in one subtree (autocomplete)
  * walking a key passes every stored prefix of it on the way down
    (longest-prefix matching, which is how routers pick a route)
"""

from __future__ import annotations

from typing import Iterator


class TrieNode:
    __slots__ = ("children", "is_key", "value")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}  # symbol -> child node
        self.is_key = False  # does a stored key end exactly here?
        self.value = None


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()
        self.node_count = 1

    def insert(self, key: str, value=None) -> None:
        node = self.root
        for symbol in key:
            child = node.children.get(symbol)
            if child is None:  # first key to go this way: extend the path
                child = node.children[symbol] = TrieNode()
                self.node_count += 1
            node = child
        node.is_key = True
        node.value = value

    def _walk(self, prefix: str) -> "TrieNode | None":
        """Follow `prefix` from the root; None if the path does not exist."""
        node = self.root
        for symbol in prefix:
            node = node.children.get(symbol)
            if node is None:
                return None
        return node

    def __contains__(self, key: str) -> bool:
        node = self._walk(key)
        return node is not None and node.is_key

    def autocomplete(self, prefix: str, limit: int = 10) -> list[str]:
        """Every stored key that starts with `prefix`, in sorted order.

        One walk reaches the subtree for the prefix; everything below it is a
        match. Cost depends on the prefix length and the number of results,
        never on the total number of keys in the trie.
        """
        start = self._walk(prefix)
        if start is None:
            return []

        def collect(node: TrieNode, spelled: str) -> Iterator[str]:
            if node.is_key:
                yield spelled
            for symbol in sorted(node.children):
                yield from collect(node.children[symbol], spelled + symbol)

        results = []
        for key in collect(start, prefix):
            results.append(key)
            if len(results) == limit:
                break
        return results

    def longest_prefix(self, key: str):
        """Return (prefix, value) for the longest stored key that prefixes `key`.

        Walk down as far as the key allows and remember the deepest stored key
        passed on the way. One pass, bounded by the key length.
        """
        node = self.root
        best = ("", node.value) if node.is_key else None
        for depth, symbol in enumerate(key, start=1):
            node = node.children.get(symbol)
            if node is None:
                break
            if node.is_key:
                best = (key[:depth], node.value)
        return best


# ---------------------------------------------------------------------------
# IP routing: the classic longest-prefix-match problem
# ---------------------------------------------------------------------------

def ip_to_bits(address: str) -> str:
    """'10.1.2.7' -> its 32 bits as a string of 0s and 1s."""
    return "".join(f"{int(octet):08b}" for octet in address.split("."))


def build_routing_table(routes: dict[str, str]) -> Trie:
    """A CIDR block like 10.1.0.0/16 means "addresses whose first 16 bits
    match". So a route is a bit-string prefix, and the table is a trie over
    the alphabet {0, 1}."""
    table = Trie()
    for cidr, target in routes.items():
        network, prefix_length = cidr.split("/")
        table.insert(ip_to_bits(network)[: int(prefix_length)], (cidr, target))
    return table


if __name__ == "__main__":
    print("1. Autocomplete")
    commands = ["config", "connect", "connection", "container", "context",
                "copy", "count", "create", "cron", "curl"]
    trie = Trie()
    for command in commands:
        trie.insert(command)
    for prefix in ["con", "co", "cr", "x"]:
        print(f"  {prefix!r:<6} -> {trie.autocomplete(prefix)}")
    total_symbols = sum(len(command) for command in commands)
    print(f"  -> {total_symbols} characters stored in {trie.node_count - 1} nodes "
          f"(shared prefixes are stored once)")

    print("\n2. Longest-prefix match in a routing table")
    table = build_routing_table({
        "0.0.0.0/0": "internet-gateway",  # the default route: an empty prefix
        "10.0.0.0/8": "vpc",
        "10.1.0.0/16": "app-subnet",
        "10.1.2.0/24": "db-subnet",
    })
    for address in ["10.1.2.7", "10.1.9.9", "10.200.0.1", "8.8.8.8"]:
        _, (cidr, target) = table.longest_prefix(ip_to_bits(address))
        print(f"  {address:<12} -> {target:<18} (matched {cidr})")
