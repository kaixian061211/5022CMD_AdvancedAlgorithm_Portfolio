import time
from datetime import date
from decimal import Decimal, InvalidOperation

from hash_table import HashTable
from product import Medicine, Product

MAX_ID_LENGTH = 10
MAX_TEXT_LENGTH = 30
MAX_PRICE = Decimal("99999.99")
MAX_QUANTITY = 999999
SEARCH_REPEATS = 1000

ID_ERROR = f"Use 1 to {MAX_ID_LENGTH} letters or digits, e.g. P011."
TEXT_ERROR = f"Enter 1 to {MAX_TEXT_LENGTH} characters."
PRICE_ERROR = "Enter a price from 0.00 to 99999.99 with at most 2 decimal places."
QUANTITY_ERROR = f"Enter a whole number from 0 to {MAX_QUANTITY}."
DATE_ERROR = "Enter a real date as YYYY-MM-DD, e.g. 2027-06-30."
YES_NO_ERROR = "Enter y or n."

MENU = """
===== Pharmacy Inventory =====
  1. Add a product
  2. Search for a product
  3. Edit a product
  4. Delete a product
  5. List all products
  0. Exit"""


def parse_product_id(text):
    """Return text as an upper-case product ID, or None if it is not 1-10 letters or digits.

    IDs are stored in upper case so that "p001" and "P001" find the same product.
    """
    text = text.upper()
    if 1 <= len(text) <= MAX_ID_LENGTH and text.isalnum():
        return text
    return None


def parse_text(text):
    """Return text if it has 1 to MAX_TEXT_LENGTH characters, otherwise None."""
    if 1 <= len(text) <= MAX_TEXT_LENGTH:
        return text
    return None


def parse_price(text):
    """Return text as a Decimal price with 2 decimal places, or None if invalid."""
    try:
        price = Decimal(text)
    except InvalidOperation:
        return None
    # These checks come before round(), which fails on "NaN", "Infinity"
    # and very large values.
    if not price.is_finite() or price < 0 or price > MAX_PRICE:
        return None
    if price != round(price, 2):
        return None
    return round(price, 2)


def parse_quantity(text):
    """Return text as an int from 0 to MAX_QUANTITY, or None if invalid."""
    try:
        quantity = int(text)
    except ValueError:
        return None
    if quantity < 0 or quantity > MAX_QUANTITY:
        return None
    return quantity


def parse_date(text):
    """Return text (YYYY-MM-DD) as a date, or None if it is not a real date."""
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def parse_yes_no(text):
    """Return True for y/yes, False for n/no, and None for anything else."""
    text = text.lower()
    if text == "y" or text == "yes":
        return True
    if text == "n" or text == "no":
        return False
    return None


def ask(prompt, default=None):
    """Print the prompt, showing any default in brackets, and return the trimmed answer."""
    if default is None:
        return input(f"{prompt}: ").strip()
    if default is True:
        default = "y"
    elif default is False:
        default = "n"
    return input(f"{prompt} [{default}]: ").strip()


def read_value(prompt, parse, error, default=None):
    """Ask until parse() accepts the answer, then return the parsed value.

    parse is one of the parse_ functions: it returns the value, or None if the
    text is invalid. If a default is given, pressing Enter keeps it.
    """
    while True:
        answer = ask(prompt, default)
        if answer == "" and default is not None:
            return default
        value = parse(answer)
        if value is not None:
            return value
        print(f"  {error}")


def ask_product(product_id, is_medicine, current=None):
    """Ask for each field and return a new Product or Medicine.

    When editing, current is the existing record and Enter keeps each value.
    When adding, current is None and every field must be typed in.
    """
    name = read_value("Name", parse_text, TEXT_ERROR,
                      current.name if current else None)
    price = read_value("Price (RM)", parse_price, PRICE_ERROR,
                       current.price if current else None)
    quantity = read_value("Quantity in stock", parse_quantity, QUANTITY_ERROR,
                          current.quantity if current else None)
    if not is_medicine:
        return Product(product_id, name, price, quantity)
    strength = read_value("Strength, e.g. 500 mg", parse_text, TEXT_ERROR,
                          current.strength if current else None)
    expiry = read_value("Expiry date (YYYY-MM-DD)", parse_date, DATE_ERROR,
                        current.expiry_date if current else None)
    prescription = read_value("Prescription required? (y/n)", parse_yes_no,
                              YES_NO_ERROR,
                              current.prescription_required if current else None)
    return Medicine(product_id, name, price, quantity,
                    strength, expiry, prescription)


def linear_search(products, product_id):
    """Return the index of the product with product_id in the list, or -1 if absent.

    This is the 1-D array search: it checks each element in turn, so it is O(n).
    """
    for index in range(len(products)):
        if products[index].product_id == product_id:
            return index
    return -1


def time_table_search(table, product_id, repeats):
    """Return the average time in ns of table.search(product_id) over repeats runs."""
    start = time.perf_counter_ns()
    for _ in range(repeats):
        table.search(product_id)
    end = time.perf_counter_ns()
    return (end - start) / repeats


def time_list_search(products, product_id, repeats):
    """Return the average time in ns of linear_search(products, product_id) over repeats runs."""
    start = time.perf_counter_ns()
    for _ in range(repeats):
        linear_search(products, product_id)
    end = time.perf_counter_ns()
    return (end - start) / repeats


def store_product(table, products, product):
    """Add a product to both the hash table and the array, and return its slot.

    Loading and adding both go through here, so the two always hold the same records.
    """
    slot = table.insert(product.product_id, product)
    products.append(product)
    return slot


def sample_products():
    """Return the records the inventory starts with."""
    return [
        Medicine("P001", "Paracetamol", Decimal("4.50"), 120, "500 mg", date(2027, 6, 30), False),
        Medicine("P002", "Amoxicillin", Decimal("18.00"), 45, "250 mg", date(2027, 1, 31), True),
        Medicine("P003", "Cetirizine", Decimal("9.90"), 80, "10 mg", date(2027, 9, 30), False),
        Medicine("P004", "Omeprazole", Decimal("22.50"), 30, "20 mg", date(2027, 3, 31), True),
        Medicine("P005", "Ibuprofen", Decimal("7.80"), 95, "200 mg", date(2027, 11, 30), False),
        Medicine("P006", "Metformin", Decimal("15.00"), 60, "500 mg", date(2028, 2, 29), True),
        Medicine("P007", "Dextromethorphan cough syrup", Decimal("12.90"), 35,
                 "15 mg/5 ml", date(2027, 4, 30), False),
        Product("P008", "Hand sanitiser 500 ml", Decimal("8.50"), 150),
        Product("P009", "Surgical face mask (50 pcs)", Decimal("12.90"), 70),
        Product("P010", "Digital thermometer", Decimal("25.00"), 20),
    ]


def print_details(product):
    """Print one product's fields as aligned label and value lines."""
    for label, value in product.details():
        print(f"  {label:<23}{value}")


def ask_existing_product(table):
    """Ask for a product ID and return that product, or None if there is no such product."""
    product_id = read_value("Product ID", parse_product_id, ID_ERROR)
    product = table.search(product_id)
    if product is None:
        print(f"No product with ID {product_id}. Option 5 lists all products.")
    return product


def add_product(table, products):
    """Ask for a new product's details and store it in the table and the array."""
    product_id = read_value("New product ID", parse_product_id, ID_ERROR)
    if table.search(product_id) is not None:
        print(f"A product with ID {product_id} already exists.")
        return
    is_medicine = read_value("Is it a medicine? (y/n)", parse_yes_no, YES_NO_ERROR)
    product = ask_product(product_id, is_medicine)
    slot = store_product(table, products, product)
    print(f"Added {product_id}: hash table slot {slot}, array index {len(products) - 1}.")


def search_product(table, products):
    """Find a product by ID, show it, and show how long each structure took to search."""
    product_id = read_value("Product ID", parse_product_id, ID_ERROR)
    table_ns = time_table_search(table, product_id, SEARCH_REPEATS)
    list_ns = time_list_search(products, product_id, SEARCH_REPEATS)
    product = table.search(product_id)
    if product is None:
        print(f"No product with ID {product_id}. Option 5 lists all products.")
    else:
        print_details(product)
    print(f"  Average search time over {SEARCH_REPEATS:,} searches:")
    print(f"    Hash table: {table_ns:>10,.0f} ns")
    print(f"    1-D array:  {list_ns:>10,.0f} ns")


def edit_product(table, products):
    """Change an existing product's details, keeping its ID and type.

    A new object replaces the old one in both the table and the array.
    """
    product = ask_existing_product(table)
    if product is None:
        return
    print("Press Enter to keep the value shown in brackets.")
    is_medicine = isinstance(product, Medicine)
    new_product = ask_product(product.product_id, is_medicine, product)
    table.update(product.product_id, new_product)
    index = linear_search(products, product.product_id)
    products[index] = new_product
    print(f"Updated {product.product_id}.")


def delete_product(table, products):
    """Remove a product from the table and the array after the user confirms."""
    product = ask_existing_product(table)
    if product is None:
        return
    print_details(product)
    if not read_value("Delete this product? (y/n)", parse_yes_no, YES_NO_ERROR):
        print("Nothing deleted.")
        return
    table.delete(product.product_id)
    index = linear_search(products, product.product_id)
    products.pop(index)
    print(f"Deleted {product.product_id}.")


def list_products(table, products):
    """Print every product in array order, then the hash table's size and load factor."""
    header = f"{'ID':<11}{'Type':<10}{'Name':<31}{'Price (RM)':>11}{'Qty':>8}"
    print(header)
    print("-" * len(header))
    for product in products:
        print(f"{product.product_id:<11}{product.category():<10}{product.name:<31}"
              f"{product.price:>11,.2f}{product.quantity:>8,}")
    print("-" * len(header))
    print(f"{table.size()} products in {table.capacity} hash table slots "
          f"(load factor {table.load_factor():.2f})")


def run_menu(table, products):
    """Show the menu and carry out the user's choices until they choose Exit."""
    while True:
        print(MENU)
        choice = input("Choose an option (0-5): ").strip()
        if choice == "1":
            add_product(table, products)
        elif choice == "2":
            search_product(table, products)
        elif choice == "3":
            edit_product(table, products)
        elif choice == "4":
            delete_product(table, products)
        elif choice == "5":
            list_products(table, products)
        elif choice == "0":
            print("Goodbye.")
            return
        else:
            print("Please enter a number from 0 to 5.")


def main():
    """Load the sample products and run the menu."""
    table = HashTable()
    products = []
    for product in sample_products():
        store_product(table, products, product)
    try:
        run_menu(table, products)
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or end of input: leave cleanly instead of showing a traceback.
        print("\nExiting.")


if __name__ == "__main__":
    main()
