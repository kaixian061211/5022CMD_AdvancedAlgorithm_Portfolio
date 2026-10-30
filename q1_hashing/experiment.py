import csv
import os
from decimal import Decimal

from hash_table import HashTable
from inventory_app import store_product, time_list_search, time_table_search
from product import Product

SIZES = (100, 1_000, 10_000, 100_000)
REPEATS = 1000
MISSING_ID = "NOTFOUND"
# Saved next to this script, so the file lands in the same place
# whichever folder the program is started from.
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "search_results.csv")
CSV_COLUMNS = ["n", "load_factor", "key_position", "key",
               "hash_table_ns", "array_ns", "array_to_table_ratio"]


def make_product(number):
    """Return a synthetic product whose ID is "P" followed by number as 6 digits."""
    return Product(f"P{number:06d}", f"Item {number}", Decimal("9.90"), number % 500)


def build_inventory(n):
    """Return a HashTable and a plain list holding the same n synthetic products.

    Uses store_product, the same function the menu uses, so both structures
    are filled exactly as they are in the inventory program.
    """
    table = HashTable()
    products = []
    for number in range(1, n + 1):
        store_product(table, products, make_product(number))
    return table, products


def keys_to_search(products):
    """Return (position, key) pairs: the first, middle and last inserted IDs and a missing ID."""
    return [
        ("first", products[0].product_id),
        ("middle", products[len(products) // 2].product_id),
        ("last", products[-1].product_id),
        ("missing", MISSING_ID),
    ]


def measure(n, repeats):
    """Build an inventory of n products and time both searches for each test key.

    Returns one result row (a dict with the CSV_COLUMNS keys) per key.
    """
    table, products = build_inventory(n)
    rows = []
    for position, key in keys_to_search(products):
        table_ns = time_table_search(table, key, repeats)
        array_ns = time_list_search(products, key, repeats)
        rows.append({
            "n": n,
            "load_factor": round(table.load_factor(), 2),
            "key_position": position,
            "key": key,
            "hash_table_ns": round(table_ns, 1),
            "array_ns": round(array_ns, 1),
            "array_to_table_ratio": round(array_ns / table_ns, 2),
        })
    return rows


def print_results(rows, repeats):
    """Print the result rows as an aligned table."""
    print(f"Average search time in ns, over {repeats:,} searches per key")
    header = (f"{'N':>9}  {'Load':>5}  {'Key':<8}{'ID':<10}"
              f"{'Hash table':>12}{'1-D array':>14}{'Array/Table':>13}")
    print(header)
    print("-" * len(header))
    for row in rows:
        print(f"{row['n']:>9,}  {row['load_factor']:>5.2f}  "
              f"{row['key_position']:<8}{row['key']:<10}"
              f"{row['hash_table_ns']:>12,.0f}{row['array_ns']:>14,.0f}"
              f"{row['array_to_table_ratio']:>13.2f}")
    print("-" * len(header))
    print("Array/Table above 1 means the hash table was faster.")


def save_csv(rows, path):
    """Write the result rows to a CSV file, with a header row."""
    # newline="" stops the csv module writing blank lines between rows on Windows.
    with open(path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    """Run the experiment for every size, print the results and save them as CSV."""
    rows = []
    for n in SIZES:
        print(f"Building and timing N = {n:,} ...")
        rows.extend(measure(n, REPEATS))
    print()
    print_results(rows, REPEATS)
    save_csv(rows, CSV_PATH)
    print(f"Results saved to {CSV_PATH}")


if __name__ == "__main__":
    main()
