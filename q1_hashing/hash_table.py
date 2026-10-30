BASE = 31
MODULUS = 1_000_000_007
MAX_LOAD_FACTOR = 0.7

# A unique marker object for deleted slots. It is compared with "is", so it
# can never be mistaken for a real entry.
DELETED = object()


def hash_key(key):
    """Return a non-negative hash value for a str or int key.

    Strings use a polynomial rolling hash: each character's code is added
    after multiplying the running total by BASE, so the order of characters
    matters ("ab" and "ba" hash differently). Taking the result mod a large
    prime keeps the number small. An int is used as its own hash.
    """
    if isinstance(key, str):
        total = 0
        for character in key:
            total = (total * BASE + ord(character)) % MODULUS
        return total
    if isinstance(key, int):
        return key
    raise TypeError("HashTable keys must be str or int")


class HashEntry:
    """A key-value pair stored in one slot of a HashTable."""

    def __init__(self, key, value):
        """Store the key and its value."""
        self.key = key
        self.value = value


class HashTable:
    """Hash table using open addressing with linear probing.

    Each slot in the list is None (never used), DELETED (a tombstone left
    by delete) or a HashEntry. A key is looked for at slot
    (hash + i) % capacity for i = 0, 1, 2, ...
    """

    def __init__(self, capacity=11):
        """Create an empty table with the given number of slots."""
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self.slots = [None] * capacity
        self.count = 0

    def _find_slot(self, key):
        """Return the index of the slot holding key, or None if key is absent."""
        start = hash_key(key)
        # Probing at most capacity slots guarantees the loop ends even if
        # no slot is None (for example, every slot is a tombstone).
        for i in range(self.capacity):
            index = (start + i) % self.capacity
            slot = self.slots[index]
            if slot is None:
                # An insert would have used this empty slot, so the key
                # cannot be further along the probe sequence.
                return None
            if slot is not DELETED and slot.key == key:
                return index
        return None

    def _find_free_slot(self, key):
        """Return the first empty or tombstone slot on key's probe sequence."""
        start = hash_key(key)
        for i in range(self.capacity):
            index = (start + i) % self.capacity
            slot = self.slots[index]
            if slot is None or slot is DELETED:
                return index
        # Cannot happen: the load factor limit keeps at least one slot free.
        raise RuntimeError("no free slot in hash table")

    def _resize(self, new_capacity):
        """Move every entry into a new list of slots of size new_capacity.

        Entries are re-inserted, not copied to the same index, because the
        slot a key belongs in depends on the capacity. Tombstones are left
        behind, which also shortens probe sequences.
        """
        old_slots = self.slots
        self.capacity = new_capacity
        self.slots = [None] * new_capacity
        for slot in old_slots:
            if slot is not None and slot is not DELETED:
                index = self._find_free_slot(slot.key)
                self.slots[index] = slot

    def insert(self, key, value):
        """Store value under key and return the index of the slot used.

        If key is already in the table its value is replaced in place.
        Otherwise, if adding one more entry would push the load factor above
        MAX_LOAD_FACTOR, the table is resized first, so the slot index
        returned is still correct after the call.
        """
        index = self._find_slot(key)
        if index is not None:
            self.slots[index].value = value
            return index
        if (self.count + 1) / self.capacity > MAX_LOAD_FACTOR:
            self._resize(self.capacity * 2 + 1)
        index = self._find_free_slot(key)
        self.slots[index] = HashEntry(key, value)
        self.count += 1
        return index

    def search(self, key):
        """Return the value stored under key, or None if key is not in the table."""
        index = self._find_slot(key)
        if index is None:
            return None
        return self.slots[index].value

    def update(self, key, value):
        """Replace the value of an existing key. Return True, or False if key is absent."""
        index = self._find_slot(key)
        if index is None:
            return False
        self.slots[index].value = value
        return True

    def delete(self, key):
        """Remove key and return True, or return False if key is absent.

        The slot is set to DELETED rather than None. A None would stop later
        searches early and hide keys that were placed after this one by probing.
        """
        index = self._find_slot(key)
        if index is None:
            return False
        self.slots[index] = DELETED
        self.count -= 1
        return True

    def size(self):
        """Return the number of keys currently stored."""
        return self.count

    def load_factor(self):
        """Return the number of stored keys divided by the number of slots."""
        return self.count / self.capacity

    def items(self):
        """Return a list of (key, value) pairs in slot order."""
        pairs = []
        for slot in self.slots:
            if slot is not None and slot is not DELETED:
                pairs.append((slot.key, slot.value))
        return pairs
