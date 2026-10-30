"""Tests for q3_concurrency/fibonacci.py."""

import os
import sys
import unittest

# The programs run as plain scripts from their own folders, so the tests
# put that folder on the import path in the same way.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "q3_concurrency"))

from fibonacci import fibonacci


class TestFibonacci(unittest.TestCase):
    """Check fibonacci() against known values."""

    def test_base_cases(self):
        """fibonacci(0) and fibonacci(1) return n itself."""
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)

    def test_first_ten_values(self):
        """The first ten values match the known sequence."""
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        for n in range(10):
            self.assertEqual(fibonacci(n), expected[n])

    def test_larger_value(self):
        """A value deep enough to exercise many levels of recursion."""
        self.assertEqual(fibonacci(20), 6765)


if __name__ == "__main__":
    unittest.main()
