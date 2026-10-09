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

save_prices(products, OUTPUT_FILE)
print(f"Saved {len(products)} prices to {OUTPUT_FILE}")