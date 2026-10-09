import re
import requests
from bs4 import BeautifulSoup


URL = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "price-tracker/0.1 (learning project)"}  # says who is asking

# fetch the page (give up after 10 seconds instead of waiting forever)
response = requests.get(URL, headers=HEADERS, timeout=10)
response.encoding = "utf-8"  # the site doesn't say, and requests guesses wrong (see below)
print("Status code:", response.status_code)

# turn the HTML text into something we can search
soup = BeautifulSoup(response.text, "html.parser")

# find the first product on the page
product = soup.find("article", class_="product_pod")

# the full title is stored in the link's title attribute
title = product.h3.a["title"]

# the price is text like "£51.77", so strip everything except digits and the dot
price_text = product.find("p", class_="price_color").text
price = float(re.sub(r"[^\d.]", "", price_text))

print(title, price)