import requests

URL = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "price-tracker/0.1 (learning project)"}  # says who is asking

# fetch the page (give up after 10 seconds instead of waiting forever)
response = requests.get(URL, headers=HEADERS, timeout=10)
response.encoding = "utf-8"  # the site doesn't say, and requests guesses wrong (see below)

print("Status code:", response.status_code)
print("Page length:", len(response.text), "characters")
print(response.text[:200])  # the first 200 characters of the HTML