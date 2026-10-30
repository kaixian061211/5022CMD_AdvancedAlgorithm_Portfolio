import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "q1_hashing"))

from hash_table import DELETED, HashTable, hash_key


class TestHashKey(unittest.TestCase):
    """The hash function is deterministic and handles str and int keys."""

    def test_string_hash_by_hand(self):
        """'ab' hashes to 97 * 31 + 98, matching a hand calculation."""
        self.assertEqual(hash_key("a"), 97)
        self.assertEqual(hash_key("ab"), 97 * 31 + 98)

    def test_character_order_matters(self):
        """Anagrams get different hashes."""
        self.assertNotEqual(hash_key("ab"), hash_key("ba"))

    def test_same_key_same_hash(self):
        """Hashing the same string twice gives the same value."""
        self.assertEqual(hash_key("P0001"), hash_key("P0001"))

    def test_int_is_own_hash(self):
        """An int key is used as its own hash."""
        self.assertEqual(hash_key(42), 42)

    def test_unsupported_type(self):
        """Keys that are not str or int are rejected."""
        with self.assertRaises(TypeError):
            hash_key(3.5)


class TestBasicOperations(unittest.TestCase):
    """Insert, search, update, delete, size and load factor."""

    def setUp(self):
        """Start each test with an empty table of 11 slots."""
        self.table = HashTable(11)

    def test_insert_and_search(self):
        """An inserted value can be found again by its key."""
        self.table.insert("P001", "Paracetamol")
        self.assertEqual(self.table.search("P001"), "Paracetamol")
        self.assertEqual(self.table.size(), 1)

    def test_insert_returns_slot_used(self):
        """The returned index is the slot that now holds the key."""
        index = self.table.insert("P001", "Paracetamol")
        self.assertEqual(self.table.slots[index].key, "P001")

    def test_insert_existing_key_updates(self):
        """Inserting an existing key replaces its value in the same slot."""
        first = self.table.insert("P001", "old")
        second = self.table.insert("P001", "new")
        self.assertEqual(first, second)
        self.assertEqual(self.table.search("P001"), "new")
        self.assertEqual(self.table.size(), 1)

    def test_search_missing_key(self):
        """Searching for a key that was never inserted returns None."""
        self.assertIsNone(self.table.search("missing"))

    def test_update(self):
        """update changes an existing value and refuses a missing key."""
        self.table.insert("P001", "old")
        self.assertTrue(self.table.update("P001", "new"))
        self.assertEqual(self.table.search("P001"), "new")
        self.assertFalse(self.table.update("P999", "x"))
        self.assertIsNone(self.table.search("P999"))

    def test_delete(self):
        """delete removes a key, and reports False for a missing key."""
        self.table.insert("P001", "Paracetamol")
        self.assertTrue(self.table.delete("P001"))
        self.assertIsNone(self.table.search("P001"))
        self.assertEqual(self.table.size(), 0)
        self.assertFalse(self.table.delete("P001"))

    def test_load_factor(self):
        """Load factor is stored keys divided by capacity."""
        for key in range(5):
            self.table.insert(key, "value")
        self.assertAlmostEqual(self.table.load_factor(), 5 / 11)

    def test_items(self):
        """items returns every stored pair and skips deleted ones."""
        self.table.insert("a", 1)
        self.table.insert("b", 2)
        self.table.insert("c", 3)
        self.table.delete("b")
        self.assertEqual(sorted(self.table.items()), [("a", 1), ("c", 3)])

    def test_invalid_capacity(self):
        """A table must have at least one slot."""
        with self.assertRaises(ValueError):
            HashTable(0)


class TestLinearProbing(unittest.TestCase):
    """Int keys 1, 12 and 23 all hash to slot 1 in a table of 11 slots."""

    def setUp(self):
        """Start each test with an empty table of 11 slots."""
        self.table = HashTable(11)

    def test_collision_moves_to_next_slot(self):
        """A colliding key goes to the next free slot."""
        self.assertEqual(self.table.insert(1, "a"), 1)
        self.assertEqual(self.table.insert(12, "b"), 2)
        self.assertEqual(self.table.insert(23, "c"), 3)

    def test_probe_wraps_around(self):
        """Probing past the last slot continues from slot 0."""
        self.assertEqual(self.table.insert(10, "a"), 10)
        self.assertEqual(self.table.insert(21, "b"), 0)

    def test_delete_leaves_tombstone(self):
        """A deleted slot holds DELETED, not None."""
        index = self.table.insert(1, "a")
        self.table.delete(1)
        self.assertIs(self.table.slots[index], DELETED)

    def test_search_continues_past_tombstone(self):
        """A key placed after a deleted one is still found."""
        self.table.insert(1, "a")
        self.table.insert(12, "b")
        self.table.delete(1)
        self.assertEqual(self.table.search(12), "b")

    def test_insert_reuses_tombstone(self):
        """A new key can take the slot of a deleted one."""
        self.table.insert(1, "a")
        self.table.insert(12, "b")
        self.table.delete(1)
        self.assertEqual(self.table.insert(23, "c"), 1)

    def test_no_duplicate_after_tombstone(self):
        """Re-inserting a key that sits past a tombstone updates it, not duplicates it."""
        self.table.insert(1, "a")
        self.table.insert(12, "b")
        self.table.delete(1)
        self.assertEqual(self.table.insert(12, "new"), 2)
        self.assertEqual(self.table.size(), 1)
        self.assertEqual(self.table.search(12), "new")

    def test_tombstone_count(self):
        """delete adds a tombstone; an insert that reuses it removes one."""
        self.table.insert(1, "a")
        self.table.insert(12, "b")
        self.table.delete(1)
        self.assertEqual(self.table.deleted, 1)
        self.table.insert(23, "c")
        self.assertEqual(self.table.deleted, 0)


class TestResize(unittest.TestCase):
    """The table is rebuilt before keys plus tombstones would exceed 0.7 of the slots."""

    def test_grows_before_exceeding_limit(self):
        """In 11 slots, 7 keys fit (0.64); the 8th (0.73) triggers a resize to 23."""
        table = HashTable(11)
        for key in range(7):
            table.insert(key, "x")
        self.assertEqual(table.capacity, 11)
        table.insert(7, "x")
        self.assertEqual(table.capacity, 23)

    def test_keys_survive_resize(self):
        """Every key is still found, with its slot index correct, after resizes."""
        table = HashTable(11)
        for number in range(1000):
            key = f"P{number:05d}"
            index = table.insert(key, number)
            self.assertEqual(table.slots[index].key, key)
        self.assertEqual(table.size(), 1000)
        self.assertLessEqual(table.load_factor(), 0.7)
        for number in range(1000):
            self.assertEqual(table.search(f"P{number:05d}"), number)

    def test_rebuild_at_same_size_clears_tombstones(self):
        """6 keys + 1 tombstone fill 7 of 11 slots. A 7th key would make 8 (0.73),
        but 7 keys alone (0.64) fit, so the table is rebuilt at 11 without tombstones."""
        table = HashTable(11)
        table.insert(10, "x")
        table.delete(10)
        for key in range(6):
            table.insert(key, "x")
        self.assertIn(DELETED, table.slots)
        table.insert(6, "x")
        self.assertNotIn(DELETED, table.slots)
        self.assertEqual(table.deleted, 0)
        self.assertEqual(table.capacity, 11)

    def test_insert_delete_cycles_keep_empty_slots(self):
        """Repeated insert and delete never fills every slot with tombstones,
        and the table does not keep growing while it holds almost no keys."""
        table = HashTable(11)
        for key in range(100):
            table.insert(key, "x")
            table.delete(key)
            self.assertIn(None, table.slots)
        self.assertEqual(table.capacity, 11)


if __name__ == "__main__":
    unittest.main()
