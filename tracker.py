import re
import requests
from bs4 import BeautifulSoup


URL = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "price-tracker/0.1 (learning project)"}  # says who is asking

def parse_product(product):
    """Pull the title and price out of one product's HTML."""
    title = product.h3.a["title"]
    price_text = product.find("p", class_="price_color").text
    price = float(re.sub(r"[^\d.]", "", price_text))
    return {"title": title, "price": price}

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
for item in products[:5]:  # show the first 5 as a quick check
    print(f"{item['title']}: £{item['price']:.2f}")