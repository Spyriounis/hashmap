from typing import Iterator

from hashmap.base_hashmap import BaseHashMap
from hashmap.utils.custom_types import KeyType, ValueType
from hashmap.utils.linked_list import Node


class SeparateChainingHashmap(BaseHashMap):
    """Hashmap implementation using separate chaining for collision resolution."""

    def __init__(
        self,
        initial_capacity: int = 16,
        min_load_factor: float = 0.1,
        max_load_factor: float = 0.75,
        downsize_factor: float = 0.5,
        upsize_factor: float = 2.0,
    ) -> None:
        """
        Initialize the separate chaining hashmap.

        Parameters
        ----------
        initial_capacity : int, default=16
            The initial capacity of the hashmap.
        min_load_factor : float, default=0.1
            The minimum load factor before resizing down.
        max_load_factor : float, default=0.75
            The maximum load factor before resizing up.
        downsize_factor : float, default=0.5
            The factor by which to decrease the capacity when resizing down.
        upsize_factor : float, default=2.0
            The factor by which to increase the capacity when resizing up.

        Returns
        -------
        None
        """
        super().__init__(
            initial_capacity,
            min_load_factor,
            max_load_factor,
            downsize_factor,
            upsize_factor,
        )
        self.buckets: list[Node] = [Node() for _ in range(self.capacity)]

    def get(self, key: KeyType, default_val: ValueType = None) -> ValueType:
        """
        Retrieve the value associated with the given key.

        This method searches through the linked list at the computed hash index for the
        key. If the key is found, it returns the associated value. If the key does not
        exist, it returns the default value specified during initialization.

        Parameters
        ----------
        key : KeyType
            The key for which to retrieve the value. Must be hashable.
        default_val : ValueType, default=None
            The default value to return for non-existent keys.

        Returns
        -------
        ValueType
            The value associated with the key, or the default value if the key does not
            exist.
        """
        index = self._hash(key)
        current_node: Node | None = self.buckets[index]

        while current_node is not None:
            if current_node.key == key:
                return current_node.value
            current_node = current_node.next_node

        return default_val

    def put(self, key: KeyType, value: ValueType, new_entry: bool = True) -> None:
        """
        Insert or update the value for the given key.

        Parameters
        ----------
        key : KeyType
            The key to insert or update. Must be hashable.
        value : ValueType
            The value to associate with the key.
        new_entry : bool, default=False
            If True, indicates that this is a potential new entry to the hasmap. False
            indicates that we are putting existing elements to a resized copy of the
            hashmap.

        Returns
        -------
        None
        """
        # Check if resizing up is needed
        if self._load_factor > self.max_load_factor:
            self._resize_and_rehash(self.upsize_factor)

        index = self._hash(key)
        current_node = self.buckets[index]

        # No collision - starting node is empty
        if current_node.key is None:
            current_node.key = key
            current_node.value = value
            if new_entry:
                self.size += 1
            return

        # Collision detected - starting node is occupied
        # Resolve using separate chaining
        while current_node.key is not None:
            if current_node.key == key:
                # Update existing key
                current_node.value = value
                return
            if current_node.next_node is None:
                # Insert new node at the end of the chain
                current_node.next_node = Node(key=key, value=value)
                if new_entry:
                    self.size += 1
                return
            current_node = current_node.next_node

    def remove(self, key: KeyType) -> None:
        """
        Remove the entry for the given key, if it exists.

        Parameters
        ----------
        key : KeyType
            The key to remove from the hash map. Must be hashable.

        Raises
        -------
        KeyError
            If the key does not exist in the hash map.

        Returns
        -------
        None
        """
        # Check if resizing down is needed
        if (
            self._load_factor < self.min_load_factor
            and self.capacity > self.initial_capacity
        ):
            self._resize_and_rehash(self.downsize_factor)

        index = self._hash(key)
        current_node = self.buckets[index]

        if current_node.key is None:
            raise KeyError(f"Key '{key}' not found in the hash map.")

        # Remove the first node in the linked list
        if current_node.key == key:
            # If there's no next node, just clear the current node
            if current_node.next_node is None:
                self.buckets[index] = Node()  # Reset to an empty node
            # If there's a next node, point the bucket to the next node
            else:
                self.buckets[index] = current_node.next_node
            self.size -= 1
            return

        # Traverse the linked list to find and remove the key
        next_node: Node | None = current_node.next_node
        while next_node is not None:
            if next_node.key == key:
                # Remove the current node by linking the previous node to the next node
                current_node.next_node = next_node.next_node
                self.size -= 1
                return
            current_node = next_node
            next_node = current_node.next_node

        raise KeyError(f"Key '{key}' not found in the hash map.")

    def _resize_and_rehash(self, resize_factor: float) -> None:
        """
        Resize the hash map and rehash all existing entries.

        This method is called when the load factor exceeds the maximum load factor
        or falls below the minimum load factor. It creates a new list of buckets with
        the new capacity and rehashes all existing entries into the new buckets.

        Parameters
        ----------
        resize_factor : float
            The factor by which to resize the hash map.

        Returns
        -------
        None
        """
        old_buckets = self.buckets
        self.capacity = (self.capacity * resize_factor).__ceil__()
        self.buckets = [Node() for _ in range(self.capacity)]

        for bucket in old_buckets:
            current_node: Node | None = bucket
            while current_node:
                if current_node.key is not None:
                    self.put(current_node.key, current_node.value, new_entry=False)
                current_node = current_node.next_node

    @property
    def _keys(self) -> list[KeyType]:
        """
        Return a list of keys in the hash map.

        This method iterates through each bucket and collects the keys
        from the linked lists in each bucket.

        Returns
        -------
        list[KeyType]
            A list of key in the hashmap.
        """
        keys = []
        for bucket in self.buckets:
            current_node: Node | None = bucket
            while current_node:
                if current_node.key is not None:
                    keys.append(current_node.key)
                current_node = current_node.next_node
        return keys

    @property
    def _values(self) -> list[ValueType]:
        """
        Return a list of values in the hash map.

        This method iterates through each bucket and collects the values
        from the linked lists in each bucket.

        Returns
        -------
        list[ValueType]
            A list of values in the hashmap.
        """
        values = []
        for bucket in self.buckets:
            current_node: Node | None = bucket
            while current_node:
                if current_node.key is not None:
                    values.append(current_node.value)
                current_node = current_node.next_node
        return values

    @property
    def _pairs(self) -> list[str]:
        """
        Return a list of key-value pairs as strings in the hash map.

        This method iterates through each bucket and collects the key-value pairs
        from the linked lists in each bucket.

        Returns
        -------
        list[str]
            A list of strings, each containing a key and its associated value.
        """
        pairs = []
        for bucket in self.buckets:
            current_node: Node | None = bucket
            while current_node:
                if current_node.key is not None:
                    pairs.append(f"{current_node.key!r}: {current_node.value!r}")
                current_node = current_node.next_node
        return pairs

    @property
    def _load_factor(self) -> float:
        """
        Calculate the current load factor of the hash map.

        The load factor is defined as the number of entries divided by the number of
        buckets. It indicates how full the hash map is, and can be used to determine if
        resizing is needed.

        Returns
        -------
        float
            The current load factor of the hash map.
        """
        return len(self) / self.capacity  # For separate chaining, this can be > 1

    def __str__(self) -> str:
        """
        Return a string representation of the hash map.

        This method iterates through each bucket and constructs a string representation
        of the key-value pairs in the hash map.

        Returns
        -------
        str
            A string representation of the hash map.
        """
        return "{" + ", ".join(self._pairs) + "}"

    def __repr__(self) -> str:
        """
        Return a string representation of the hash map.

        Returns
        -------
        str
            A string representation of the hash map.
        """
        return self.__str__()

    def __len__(self) -> int:
        """
        Return the number of entries in the hash map.

        Returns
        -------
        int
            The number of key-value pairs in the hash map.
        """
        return self.size

    def __contains__(self, key: KeyType) -> bool:
        """
        Check if the hash map contains the given key.

        Parameters
        ----------
        key : KeyType
            The key to check for existence in the hash map.

        Returns
        -------
        bool
            True if the key exists in the hash map, False otherwise.
        """
        return self.get(key, default_val=None) is not None

    def __iter__(self) -> Iterator[KeyType]:
        """
        Return an iterator over the keys in the hash map.
        """
        return iter(self._keys)
