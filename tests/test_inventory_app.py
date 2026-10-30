import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from datetime import date
from decimal import Decimal
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "q1_hashing"))

from hash_table import HashTable
from inventory_app import (delete_product, edit_product, linear_search,
                           parse_date, parse_price, parse_product_id,
                           parse_quantity, parse_text, parse_yes_no,
                           read_value, sample_products, store_product)


def run_with_input(function, answers, *args):
    """Call function(*args) with input() returning answers in turn, hiding its output."""
    with patch("builtins.input", side_effect=answers):
        with redirect_stdout(io.StringIO()):
            return function(*args)


class TestParsers(unittest.TestCase):
    """Each parse_ function returns a value for valid text and None otherwise."""

    def test_product_id(self):
        """IDs are upper-cased and must be 1-10 letters or digits."""
        self.assertEqual(parse_product_id("p001"), "P001")
        self.assertEqual(parse_product_id("A123456789"), "A123456789")
        self.assertIsNone(parse_product_id(""))
        self.assertIsNone(parse_product_id("P-01"))
        self.assertIsNone(parse_product_id("P 01"))
        self.assertIsNone(parse_product_id("A1234567890"))

    def test_text(self):
        """Text must have 1 to 30 characters."""
        self.assertEqual(parse_text("Paracetamol"), "Paracetamol")
        self.assertEqual(parse_text("x" * 30), "x" * 30)
        self.assertIsNone(parse_text(""))
        self.assertIsNone(parse_text("x" * 31))

    def test_valid_prices(self):
        """Valid prices come back as Decimals with two decimal places."""
        self.assertEqual(str(parse_price("12.5")), "12.50")
        self.assertEqual(parse_price("0"), Decimal("0.00"))
        self.assertEqual(parse_price("99999.99"), Decimal("99999.99"))

    def test_invalid_prices(self):
        """Non-numbers, negatives, too many decimals and extreme values are rejected."""
        for text in ["", "abc", "RM5", "-1", "12.345", "100000",
                     "nan", "inf", "1e999999"]:
            self.assertIsNone(parse_price(text), text)

    def test_quantity(self):
        """Quantities are whole numbers from 0 to 999999."""
        self.assertEqual(parse_quantity("0"), 0)
        self.assertEqual(parse_quantity("150"), 150)
        for text in ["", "abc", "2.5", "-1", "1000000"]:
            self.assertIsNone(parse_quantity(text), text)

    def test_date(self):
        """Only real dates in YYYY-MM-DD form are accepted."""
        self.assertEqual(parse_date("2028-02-29"), date(2028, 2, 29))
        self.assertIsNone(parse_date("2027-02-29"))
        self.assertIsNone(parse_date("30/06/2027"))
        self.assertIsNone(parse_date(""))

    def test_yes_no(self):
        """y/yes and n/no in any case; anything else is rejected."""
        self.assertIs(parse_yes_no("Y"), True)
        self.assertIs(parse_yes_no("yes"), True)
        self.assertIs(parse_yes_no("n"), False)
        self.assertIs(parse_yes_no("No"), False)
        self.assertIsNone(parse_yes_no("maybe"))


class TestReadValue(unittest.TestCase):
    """read_value keeps asking until the answer is valid."""

    def test_retries_until_valid(self):
        """Invalid answers are rejected and the first valid one is returned."""
        answers = ["abc", "-3", "2.5", "7"]
        self.assertEqual(run_with_input(read_value, answers, "Qty", parse_quantity, "err"), 7)

    def test_enter_keeps_default(self):
        """An empty answer returns the default, even when the default is 0 or False."""
        self.assertEqual(run_with_input(read_value, [""], "Qty", parse_quantity, "err", 0), 0)
        self.assertIs(run_with_input(read_value, [""], "Rx", parse_yes_no, "err", False), False)


class TestInventorySync(unittest.TestCase):
    """The hash table and the array always hold the same products."""

    def setUp(self):
        """Load the sample products into a new table and list."""
        self.table = HashTable()
        self.products = []
        for product in sample_products():
            store_product(self.table, self.products, product)

    def assert_in_sync(self):
        """Check both structures have the same size and the same objects."""
        self.assertEqual(self.table.size(), len(self.products))
        for product in self.products:
            self.assertIs(self.table.search(product.product_id), product)

    def test_sample_products_load(self):
        """All 10 sample products are stored with unique IDs."""
        self.assertEqual(len(self.products), 10)
        self.assert_in_sync()

    def test_linear_search(self):
        """linear_search returns the list index, or -1 if the ID is absent."""
        self.assertEqual(linear_search(self.products, "P001"), 0)
        self.assertEqual(linear_search(self.products, "P010"), 9)
        self.assertEqual(linear_search(self.products, "P999"), -1)

    def test_edit_replaces_in_both(self):
        """Editing P001's price changes it in the table and the array."""
        # ID, then name, price, quantity, strength, expiry, prescription.
        run_with_input(edit_product, ["P001", "", "5.00", "", "", "", ""],
                       self.table, self.products)
        self.assertEqual(self.table.search("P001").price, Decimal("5.00"))
        self.assertEqual(self.table.search("P001").name, "Paracetamol")
        self.assert_in_sync()

    def test_delete_removes_from_both(self):
        """Confirmed delete removes P002 from the table and the array."""
        run_with_input(delete_product, ["P002", "y"], self.table, self.products)
        self.assertIsNone(self.table.search("P002"))
        self.assertEqual(linear_search(self.products, "P002"), -1)
        self.assert_in_sync()

    def test_delete_can_be_cancelled(self):
        """Answering n keeps the product."""
        run_with_input(delete_product, ["P002", "n"], self.table, self.products)
        self.assertIsNotNone(self.table.search("P002"))
        self.assert_in_sync()


if __name__ == "__main__":
    unittest.main()
