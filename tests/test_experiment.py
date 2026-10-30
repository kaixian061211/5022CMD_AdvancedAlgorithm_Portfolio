import csv
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "q1_hashing"))

from experiment import (CSV_COLUMNS, MISSING_ID, build_inventory, keys_to_search,
                        make_product, measure, save_csv)
from inventory_app import linear_search


class TestDataGeneration(unittest.TestCase):
    """Synthetic products are stored identically in both structures."""

    def test_make_product_id(self):
        """IDs are P followed by 6 digits."""
        self.assertEqual(make_product(42).product_id, "P000042")

    def test_build_inventory(self):
        """The table and the list hold the same n products in insertion order."""
        table, products = build_inventory(50)
        self.assertEqual(table.size(), 50)
        self.assertEqual(len(products), 50)
        self.assertEqual(products[0].product_id, "P000001")
        self.assertEqual(products[-1].product_id, "P000050")
        for product in products:
            self.assertIs(table.search(product.product_id), product)

    def test_keys_to_search(self):
        """The keys are the first, middle and last inserted IDs and one missing ID."""
        table, products = build_inventory(9)
        self.assertEqual(keys_to_search(products), [
            ("first", "P000001"),
            ("middle", "P000005"),
            ("last", "P000009"),
            ("missing", MISSING_ID),
        ])

    def test_missing_id_is_absent(self):
        """The missing key is in neither structure."""
        table, products = build_inventory(100)
        self.assertIsNone(table.search(MISSING_ID))
        self.assertEqual(linear_search(products, MISSING_ID), -1)


class TestMeasureAndSave(unittest.TestCase):
    """measure produces one complete row per key, and save_csv writes them out."""

    def test_measure_rows(self):
        """Four rows, all with positive times and the right size."""
        rows = measure(20, 3)
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertEqual(sorted(row.keys()), sorted(CSV_COLUMNS))
            self.assertEqual(row["n"], 20)
            self.assertGreater(row["hash_table_ns"], 0)
            self.assertGreater(row["array_ns"], 0)

    def test_save_csv(self):
        """The CSV has the header row followed by one line per result row."""
        rows = measure(10, 2)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "results.csv")
            save_csv(rows, path)
            with open(path, newline="") as file:
                lines = list(csv.reader(file))
        self.assertEqual(lines[0], CSV_COLUMNS)
        self.assertEqual(len(lines), 5)
        self.assertEqual(lines[1][2], "first")


if __name__ == "__main__":
    unittest.main()
