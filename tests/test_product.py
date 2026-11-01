import os
import sys
import unittest
from datetime import date
from decimal import Decimal

# The programs run as plain scripts from their own folders, so the tests
# put that folder on the import path in the same way.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "q1_hashing"))

from product import Medicine, Product


class TestProduct(unittest.TestCase):
    """A general product reports its type and formats its details."""

    def setUp(self):
        """Create one general product."""
        self.product = Product("P100", "Face mask", Decimal("1234.5"), 2500)

    def test_category(self):
        """A plain Product is listed as General."""
        self.assertEqual(self.product.category(), "General")

    def test_details(self):
        """Details are in display order, with money and quantity formatted."""
        self.assertEqual(self.product.details(), [
            ("Product ID", "P100"),
            ("Type", "General"),
            ("Name", "Face mask"),
            ("Price", "RM 1,234.50"),
            ("Quantity in stock", "2,500"),
        ])


class TestMedicine(unittest.TestCase):
    """A medicine is a Product with three extra fields."""

    def setUp(self):
        """Create one prescription medicine."""
        self.medicine = Medicine("P200", "Amoxicillin", Decimal("18.00"), 45,
                                 "250 mg", date(2027, 1, 31), True)

    def test_is_a_product(self):
        """Medicine inherits from Product, so it keeps the Product fields."""
        self.assertIsInstance(self.medicine, Product)
        self.assertEqual(self.medicine.price, Decimal("18.00"))

    def test_category(self):
        """A Medicine overrides category()."""
        self.assertEqual(self.medicine.category(), "Medicine")

    def test_details_extend_product_details(self):
        """The Product rows come first, then the medicine-only rows."""
        rows = self.medicine.details()
        self.assertEqual(rows[1], ("Type", "Medicine"))
        self.assertEqual(rows[5:], [
            ("Strength", "250 mg"),
            ("Expiry date", "2027-01-31"),
            ("Prescription required", "Yes"),
        ])

    def test_no_prescription(self):
        """A medicine sold without prescription shows No."""
        medicine = Medicine("P201", "Paracetamol", Decimal("4.50"), 10,
                            "500 mg", date(2027, 6, 30), False)
        self.assertEqual(medicine.details()[-1], ("Prescription required", "No"))


if __name__ == "__main__":
    unittest.main()
