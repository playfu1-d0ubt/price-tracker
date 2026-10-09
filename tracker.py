"""Price tracker: reads product prices from a web page, saves each check to a CSV,
and reports any prices that have changed since the last check.

Usage:
    python tracker.py                         # checks the default practice site
    python tracker.py URL                     # checks a different page
    python tracker.py URL -o other_prices.csv # keeps that page's history in its own file
"""
import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup


DEFAULT_URL = "https://books.toscrape.com/"
DEFAULT_OUTPUT = "prices.csv"
HEADERS = {"User-Agent": "price-tracker/0.1 (learning project)"}

def fetch_page(url):
    """Download a page and return its HTML, or exit with a friendly message."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # turns 404, 403, 500... into an error
    except requests.exceptions.HTTPError as error:
        sys.exit(f"Error: the site answered with status {error.response.status_code} for '{url}'.")
    except requests.exceptions.ConnectionError:
        sys.exit(f"Error: can't connect to '{url}'. Check your internet connection and the address.")
    except requests.exceptions.Timeout:
        sys.exit(f"Error: '{url}' took too long to respond.")
    except requests.exceptions.RequestException as error:
        sys.exit(f"Error: couldn't fetch '{url}' ({error}).")
    response.encoding = "utf-8"
    return response.text

def parse_product(product):
    """Pull the title and price out of one product's HTML."""
    title = product.h3.a["title"]
    price_text = product.find("p", class_="price_color").text
    price = float(re.sub(r"[^\d.]", "", price_text))
    return {"title": title, "price": price}

def get_products(html):
    """Parse every product on the page, skipping (and counting) any that don't look right."""
    soup = BeautifulSoup(html, "html.parser")
    products = []
    skipped = 0
    for tag in soup.find_all("article", class_="product_pod"):
        try:
            products.append(parse_product(tag))
        except (AttributeError, KeyError, ValueError):
            skipped += 1
    if skipped:
        print(f"Warning: skipped {skipped} product(s) that didn't look right.")
    return products

def load_last_run(filename):
    """Return {title: price} for the most recent run in the CSV, or {} if there isn't one."""
    if not Path(filename).exists():
        return {}
    with open(filename, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        return {}
    # timestamps are written year-first, so the biggest one as text is also the latest
    latest = max(row["timestamp"] for row in rows)
    # prices come back from the CSV as text, so turn them back into numbers
    return {row["title"]: float(row["price"]) for row in rows if row["timestamp"] == latest}


def find_changes(old_prices, new_products):
    """Return the products whose price is different from the last run."""
    changes = []
    for item in new_products:
        old_price = old_prices.get(item["title"])  # None if we haven't seen this product before
        if old_price is not None and round(item["price"] - old_price, 2) != 0:
            changes.append({"title": item["title"], "old": old_price, "new": item["price"]})
    return changes


def report_changes(changes):
    """Print each price change, drops first."""
    if not changes:
        print("No price changes since the last check.")
        return
    for change in sorted(changes, key=lambda c: c["new"] - c["old"]):
        word = "DROPPED" if change["new"] < change["old"] else "ROSE"
        print(f"{word}: {change['title']}  £{change['old']:.2f} -> £{change['new']:.2f}")

def save_prices(products, filename):
    """Add this run's prices to the end of the CSV, all stamped with the same time."""
    is_new_file = not Path(filename).exists()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # "a" = append, so earlier runs are kept
    with open(filename, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if is_new_file:
            writer.writerow(["timestamp", "title", "price"])  # header only once
        for item in products:
            writer.writerow([timestamp, item["title"], item["price"]])

def main():
    parser = argparse.ArgumentParser(description="Track product prices on a page and flag changes.")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL,
                        help="page to check (default: the books.toscrape.com practice site)")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                        help="CSV file that stores the price history (default: prices.csv)")
    args = parser.parse_args()

    html = fetch_page(args.url)
    products = get_products(html)
    if not products:
        sys.exit("Error: no products found. Is this the right page, or has its layout changed?")
    print(f"Found {len(products)} products")

    # compare with the last run BEFORE saving, otherwise "last run" would be this one
    previous = load_last_run(args.output)
    if previous:
        report_changes(find_changes(previous, products))
    else:
        print("First run - nothing to compare with yet.")

    save_prices(products, args.output)
    print(f"Saved {len(products)} prices to {args.output}")


if __name__ == "__main__":
    main()