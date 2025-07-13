"""Unit tests for the separate chaining hashmap implementation."""

from unittest.mock import Mock, patch

import pytest

from hashmap.separate_chaining_hashmap import SeparateChainingHashmap


def test_put_new_key_no_collision() -> None:
    """Test inserting a new key-value pair without collision."""
    hashmap = SeparateChainingHashmap()
    hashmap.put("key1", "value1")

    index = hashmap._hash("key1")
    node = hashmap.buckets[index]

    assert node is not None
    assert node.key == "key1"
    assert node.value == "value1"


def test_put_existing_key_updates_value() -> None:
    """Test updating the value of an existing key."""
    hashmap = SeparateChainingHashmap()
    hashmap.put("key1", "value1")
    hashmap.put("key1", "value2")

    index = hashmap._hash("key1")
    node = hashmap.buckets[index]

    assert node is not None
    assert node.key == "key1"
    assert node.value == "value2"


@patch("hashmap.separate_chaining_hashmap.SeparateChainingHashmap._hash")
def test_put_with_collision(mock_hash: Mock) -> None:
    """Test inserting a key-value pair that collides with an existing key."""
    mock_hash.return_value = 0  # Force all keys to hash to the same index

    hashmap = SeparateChainingHashmap()
    hashmap.put("key1", "value1")
    hashmap.put("key2", "value2")  # Assuming key2 hashes to the same index as key1

    index = hashmap._hash("key1")
    node = hashmap.buckets[index]

    # Check the first node in the chain for key1
    assert node is not None
    assert node.key == "key1"
    assert node.value == "value1"

    # Check the next node in the chain for key2
    next_node = node.next_node
    assert next_node is not None
    assert next_node.key == "key2"
    assert next_node.value == "value2"


@patch("hashmap.separate_chaining_hashmap.SeparateChainingHashmap._resize_and_rehash")
def test_put_resizes_up_when_max_load_factor_exceeded(
    mock_resize_and_rehash: Mock,
) -> None:
    """Test that the hashmap resizes up when the max load factor is exceeded."""

    # Should resize up when before the third insertion
    hashmap = SeparateChainingHashmap(initial_capacity=2, max_load_factor=0.5)

    hashmap.put("key1", "value1")
    hashmap.put("key2", "value2")
    hashmap.put("key3", "value3")  # This should trigger a resize

    mock_resize_and_rehash.assert_called_once_with(hashmap.upsize_factor)


def test_put_multiple_keys() -> None:
    """Test inserting multiple key-value pairs."""
    hashmap = SeparateChainingHashmap(initial_capacity=10, max_load_factor=0.75)
    for index in range(1000):
        hashmap.put(f"key_{index}", f"value_{index}")

    assert hashmap.size == 1000
    assert hashmap.capacity > 10  # Ensure the capacity has increased due to resizing

    expected_keys = [f"key_{index}" for index in range(1000)]
    assert sorted(expected_keys) == sorted(hashmap._keys)


def test_get_existing_key() -> None:
    """Test retrieving the value of an existing key."""
    hashmap = SeparateChainingHashmap()
    hashmap.put("key1", "value1")

    value = hashmap.get("key1")
    assert value == "value1"


def test_get_non_existing_key() -> None:
    """Test retrieving a value for a non-existing key."""
    hashmap = SeparateChainingHashmap()
    value = hashmap.get("non_existing_key")
    assert value is None  # Default value for non-existing keys is None


def test_get_non_existing_key_with_default_value() -> None:
    """Test retrieving a value for a non-existing key with a default value."""
    hashmap = SeparateChainingHashmap()
    default_value = "default_value"
    value = hashmap.get("non_existing_key", default_value)
    assert value == default_value  # Should return the provided default value


@patch("hashmap.separate_chaining_hashmap.SeparateChainingHashmap._hash")
def test_get_with_collision(mock_hash: Mock) -> None:
    """Test retrieving a value for a key that collides with another key."""
    mock_hash.return_value = 0  # Force all keys to hash to the same index

    hashmap = SeparateChainingHashmap()
    hashmap.put("key1", "value1")
    hashmap.put("key2", "value2")  # Assuming key2 collides with key1

    value = hashmap.get("key2")
    assert value == "value2"  # Should return the value for key2


def test_remove_existing_key() -> None:
    """Test removing an existing key."""
    hashmap = SeparateChainingHashmap()
    hashmap.put("key1", "value1")

    hashmap.remove("key1")

    value = hashmap.get("key1")
    assert value is None  # Should return None after removal


def test_remove_non_existing_key_throws_key_error() -> None:
    """Test that removing a non-existing key raises a KeyError."""
    hashmap = SeparateChainingHashmap()

    with pytest.raises(KeyError):
        hashmap.remove("non_existing_key")


def test_remove_resizes_down_when_min_load_factor_exceeded() -> None:
    """Test that the hashmap resizes down when the min load factor is exceeded."""

    # Should resize down when after the third removal
    hashmap = SeparateChainingHashmap(
        initial_capacity=4,
        min_load_factor=0.5,
        max_load_factor=0.75,
        upsize_factor=2,
        downsize_factor=0.5,
    )

    hashmap.put("key1", "value1")
    hashmap.put("key2", "value2")
    hashmap.put("key3", "value3")
    hashmap.put("key4", "value4")
    hashmap.put("key5", "value5")  # This should trigger a resize up

    assert hashmap.size == 5
    assert hashmap.capacity == hashmap.initial_capacity * hashmap.upsize_factor

    hashmap.remove("key5")
    hashmap.remove("key4")
    hashmap.remove("key3")  # This should trigger a resize down

    assert hashmap.size == 2
    assert (
        hashmap.capacity
        == hashmap.initial_capacity * hashmap.upsize_factor * hashmap.downsize_factor
    )


def test_remove_multiple_keys() -> None:
    """Test removing multiple keys."""
    hashmap = SeparateChainingHashmap(initial_capacity=10, max_load_factor=0.75)
    for index in range(1000):
        hashmap.put(f"key_{index}", f"value_{index}")

    assert hashmap.size == 1000

    for index in range(500):
        hashmap.remove(f"key_{index}")

    assert hashmap.size == 500
    assert (
        f"key_499" not in hashmap._keys
    )  # Ensure the removed key is no longer present


def test_resize_and_rehash_all_pairs_are_copied() -> None:
    """Test that all key value pairs are copied during resizing and rehashing."""
    hashmap = SeparateChainingHashmap(initial_capacity=2, max_load_factor=0.5)

    # Insert enough elements to trigger a resize
    for i in range(15):
        hashmap.put(f"key_{i}", f"value_{i}")

    # Check that all keys are present after resizing
    for i in range(15):
        assert hashmap.get(f"key_{i}") == f"value_{i}"

    # Ensure the size is correct
    assert hashmap.size == 15
    assert (
        hashmap.capacity > hashmap.initial_capacity
    )  # Ensure the capacity has increased due to resizing


def test_resize_and_rehash_no_data_loss() -> None:
    """Test that no data is lost during resizing and rehashing."""
    hashmap = SeparateChainingHashmap(initial_capacity=2, max_load_factor=0.5)

    # Insert enough elements to trigger a resize
    for i in range(10):
        hashmap.put(f"key_{i}", f"value_{i}")

    # Remove some elements
    for i in range(5):
        hashmap.remove(f"key_{i}")

    # Trigger a resize by adding more elements
    for i in range(10, 15):
        hashmap.put(f"key_{i}", f"value_{i}")

    # Check that all remaining keys are present after resizing
    for i in range(5, 15):
        assert hashmap.get(f"key_{i}") == f"value_{i}"

    # Ensure the size is correct
    assert hashmap.size == 10
    assert (
        hashmap.capacity > hashmap.initial_capacity
    )  # Ensure the capacity has increased due to resizing


@pytest.mark.parametrize("resize_factor", [2, 3, 4])
def test_resize_and_rehash_new_capacity_is_correct(resize_factor: int) -> None:
    """Test that the new capacity is correct after resizing and rehashing."""
    initial_capacity = 4
    hashmap = SeparateChainingHashmap(
        initial_capacity=initial_capacity, max_load_factor=0.5
    )

    # Trigger a resize with the specified factor
    hashmap._resize_and_rehash(resize_factor)

    expected_capacity = initial_capacity * resize_factor
    assert hashmap.capacity == expected_capacity


def test_expected_keys_are_present() -> None:
    """Test that the expected keys are present in the hashmap."""
    hashmap = SeparateChainingHashmap(initial_capacity=10, max_load_factor=0.75)

    # Insert multiple key-value pairs
    for index in range(100):
        hashmap.put(f"key_{index}", f"value_{index}")

    # Check that all expected keys are present
    expected_keys = [f"key_{index}" for index in range(100)]
    assert sorted(expected_keys) == sorted(hashmap._keys)


def test_expected_values_are_present() -> None:
    """Test that the expected values are present in the hashmap."""
    hashmap = SeparateChainingHashmap(initial_capacity=10, max_load_factor=0.75)

    # Insert multiple key-value pairs
    for index in range(100):
        hashmap.put(f"key_{index}", f"value_{index}")

    # Check that all expected values are present
    expected_values = [f"value_{index}" for index in range(100)]
    assert sorted(expected_values) == sorted(hashmap._values)


def test_load_factor_calculation() -> None:
    """Test that the load factor is calculated correctly."""
    hashmap = SeparateChainingHashmap(initial_capacity=10, max_load_factor=0.75)

    # Insert some key-value pairs
    for index in range(5):
        hashmap.put(f"key_{index}", f"value_{index}")

    # Calculate the expected load factor
    expected_load_factor = hashmap.size / hashmap.capacity

    # Check that the load factor is as expected
    assert expected_load_factor == 0.5  # 5 entries in a capacity of 10


def test_expected_length() -> None:
    """Test that the expected length of the hashmap is correct."""
    hashmap = SeparateChainingHashmap(initial_capacity=10, max_load_factor=0.75)

    # Insert multiple key-value pairs
    for index in range(100):
        hashmap.put(f"key_{index}", f"value_{index}")

    # Check that the length of the hashmap is as expected
    assert len(hashmap) == 100  # Should return the number of key-value pairs


def test_hashmap_contains_existing_key() -> None:
    """Test that the hashmap contains an existing key."""
    hashmap = SeparateChainingHashmap()
    hashmap.put("key1", "value1")

    assert "key1" in hashmap  # Should return True for existing keys


def test_hashmap_does_not_contain_non_existing_key() -> None:
    """Test that the hashmap does not contain a non-existing key."""
    hashmap = SeparateChainingHashmap()

    assert (
        "non_existing_key" not in hashmap
    )  # Should return False for non-existing keys
