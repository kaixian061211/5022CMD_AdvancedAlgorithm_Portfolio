class Product:
    """A general item sold by the pharmacy, such as a face mask.

    Attribute types:
      product_id (str): an identifier such as "P001". It may contain letters
                        and is never used in arithmetic, so it is not a number.
      name (str):       free text.
      price (Decimal):  money in RM. Decimal stores base-10 values exactly,
                        whereas a float cannot store 0.10 exactly.
      quantity (int):   units in stock, which are always whole.
    """

    def __init__(self, product_id, name, price, quantity):
        """Create a product from already-validated values."""
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    def category(self):
        """Return the product type shown in listings."""
        return "General"

    def details(self):
        """Return the record as (label, text) pairs, in display order."""
        return [
            ("Product ID", self.product_id),
            ("Type", self.category()),
            ("Name", self.name),
            ("Price", f"RM {self.price:,.2f}"),
            ("Quantity in stock", f"{self.quantity:,}"),
        ]


class Medicine(Product):
    """A medicine: a Product with a strength, an expiry date and a prescription rule.

    Extra attribute types:
      strength (str):               amount and unit together, e.g. "500 mg" or
                                    "15 mg/5 ml", so a single number would not fit.
      expiry_date (date):           a real calendar date, so invalid dates are
                                    rejected and dates can be compared.
      prescription_required (bool): there are only two possible answers.
    """

    def __init__(self, product_id, name, price, quantity,
                 strength, expiry_date, prescription_required):
        """Create a medicine from already-validated values."""
        super().__init__(product_id, name, price, quantity)
        self.strength = strength
        self.expiry_date = expiry_date
        self.prescription_required = prescription_required

    def category(self):
        """Return the product type shown in listings."""
        return "Medicine"

    def details(self):
        """Return the Product details followed by the medicine-only fields."""
        rows = super().details()
        rows.append(("Strength", self.strength))
        rows.append(("Expiry date", self.expiry_date.isoformat()))
        if self.prescription_required:
            rows.append(("Prescription required", "Yes"))
        else:
            rows.append(("Prescription required", "No"))
        return rows
