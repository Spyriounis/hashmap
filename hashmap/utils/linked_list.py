"""Linked list implementation for separate chaining in hash maps."""

from typing import Self

from hashmap.utils.custom_types import KeyType, ValueType


class Node:
    """
    A node in the hashmap's linked list for handling collisions using separate chaining.
    """

    def __init__(
        self,
        key: KeyType = None,
        value: ValueType = None,
        next_node: Self | None = None,
    ) -> None:
        """
        Initialize a new node with a given key, value and optional pointer to the next node.

        Parameters
        ----------
        key : KeyType
            The key for this node.
        value : ValueType
            The value associated with the key.
        next_node : Node | None, optional
            Pointer to the next node in the linked list (default is None).

        Returns
        -------
        None
        """
        self.key = key
        self.value = value
        self.next_node = next_node
