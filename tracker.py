import csv
import re
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup


URL = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "price-tracker/0.1 (learning project)"}  # says who is asking
OUTPUT_FILE = "prices.csv"

def parse_product(product):
    """Pull the title and price out of one product's HTML."""
    title = product.h3.a["title"]
    price_text = product.find("p", class_="price_color").text
    price = float(re.sub(r"[^\d.]", "", price_text))
    return {"title": title, "price": price}

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

# fetch the page (give up after 10 seconds instead of waiting forever)
response = requests.get(URL, headers=HEADERS, timeout=10)
response.encoding = "utf-8"  # the site doesn't say, and requests guesses wrong (see below)
print("Status code:", response.status_code)

# turn the HTML text into something we can search
soup = BeautifulSoup(response.text, "html.parser")

# find_all returns every matching tag, not just the first one
products = []
for product in soup.find_all("article", class_="product_pod"):
    products.append(parse_product(product))

print(f"Found {len(products)} products")

# compare with the last run BEFORE saving, otherwise "last run" would be this one
previous = load_last_run(OUTPUT_FILE)
if previous:
    report_changes(find_changes(previous, products))
else:
    print("First run - nothing to compare with yet.")

save_prices(products, OUTPUT_FILE)
print(f"Saved {len(products)} prices to {OUTPUT_FILE}")