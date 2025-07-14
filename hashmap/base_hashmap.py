"""Abstract base class for a hash map implementation."""

from abc import ABC, abstractmethod

from hashmap.utils.custom_types import KeyType, ValueType


class BaseHashMap(ABC):
    """
    Abstract interface for a hash map implementation.

    This class defines the basic structure and methods that any hash map implementation
    should provide. It includes methods for inserting, retrieving, and removing
    key-value pairs, as well as properties for managing the hash map's capacity and
    load factors.

    Attributes
    ----------
    initial_capacity : int
        The initial capacity, or number of supported buckets, in the hash map.
    min_load_factor : float
        The minimum load factor before dynamically resizing the hash map down.
    max_load_factor : float
        The maximum load factor before dynamically resizing the hash map up.
    downsize_factor : float
        The factor by which to decrease the capacity when resizing down.
    upsize_factor : int
        The factor by which to increase the capacity when resizing up.
    size : int
        The number of key-value pair entries in the hash map.
    """

    def __init__(
        self,
        initial_capacity: int,
        min_load_factor: float,
        max_load_factor: float,
        downsize_factor: float,
        upsize_factor: float,
    ) -> None:
        """
        Initialize the hash map.

        Parameters
        ----------
        initial_capacity : int
            The initial capacity, or number of supported buckets, in the hash map.
        min_load_factor : float
            The minimum load factor before dynamically resizing the hash map down.
        max_load_factor : float
            The maximum load factor before dynamically resizing the hash map up.
        downsize_factor : float
            The factor by which to decrease the capacity when resizing down.
        upsize_factor : int
            The factor by which to increase the capacity when resizing up.


        Returns
        -------
        None
        """
        self.initial_capacity = initial_capacity
        self.capacity = initial_capacity
        self.min_load_factor = min_load_factor
        self.max_load_factor = max_load_factor
        self.downsize_factor = downsize_factor
        self.upsize_factor = upsize_factor
        self.size = 0  # Number of key-value pair entries in the hash map

    def _hash(self, key: KeyType) -> int:
        """
        Compute the hash value for the given key.

        This method uses Python's built-in `hash` function and applies a modulo
        operation with the current capacity to ensure the hash value fits within the
        bounds of the hash map.

        This method is used internally to determine the index for storing or retrieving
        values.

        Parameters
        ----------
        key : KeyType
            The key to hash. Must be hashable.

        Returns
        -------
        int
            The hash value of the key.
        """
        return hash(key) % self.capacity

    @abstractmethod
    def get(self, key: KeyType, default_val: ValueType = None) -> ValueType:
        """
        Retrieve the value associated with the given key.

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

    @abstractmethod
    def put(self, key: KeyType, value: ValueType) -> None:
        """
        Insert or update the value for the given key.

        Parameters
        ----------
        key : KeyType
            The key to insert or update. Must be hashable.
        value : ValueType
            The value to associate with the key.

        Returns
        -------
        None
        """

    @abstractmethod
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
