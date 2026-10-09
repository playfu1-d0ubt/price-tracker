# Price Tracker

A command-line tool, written in Python, that checks the prices on a web page, keeps a history of every check, and tells you which prices have dropped or risen since the last time.

## The problem

Keeping an eye on prices by hand means opening a page, scrolling, and trying to remember what things cost last week. This script does the checking in one command and does the remembering for you, so you only see what changed. It could be used to watch competitors' prices, a supplier's catalogue, or products you're waiting to go on sale.

## What it does

- Downloads a product listing page and reads the title and price of every product
- Saves each check to a CSV file with a timestamp, so you build up a price history
- Compares the new prices with the previous check and prints every change, biggest drops first
- Takes the page address as an argument, so it isn't tied to one page
- Shows a clear message, not a crash, when the site is down, the address is wrong or the page layout isn't what it expects

## Example

The practice site's prices never change, so to show a change I edited three prices in the history file by hand and ran the script again.

```
$ python tracker.py
Status code: 200
Found 20 products
DROPPED: Libertarianism for Beginners  £55.00 -> £51.33
DROPPED: Mesaerion: The Best Science Fiction Stories 1800-1849  £40.50 -> £37.59
ROSE: It's Only the Himalayas  £45.00 -> £45.17
Saved 20 prices to prices.csv
```

When nothing has changed it says `No price changes since the last check.`

## How to run

You need Python 3.

```bash
git clone git@github.com:playfu1-d0ubt/price-tracker.git
cd price-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python tracker.py
```

### Options

```bash
python tracker.py                           # checks the default practice site
python tracker.py URL                       # checks a different page
python tracker.py URL -o other_prices.csv   # keeps that page's history in its own file
python tracker.py --help                    # shows all options
```

Use a separate `-o` file for each page you track. The history is matched by product title, so mixing two different pages in one file would compare the wrong products.

### Running it every day

On Linux, `cron` can run it on a schedule. Run `crontab -e` and add a line like this, which checks every day at 9am (use the full path to your own project folder):

```
0 9 * * * cd /home/YOUR-NAME/price-tracker && ./venv/bin/python tracker.py >> tracker.log 2>&1
```

The computer needs to be switched on at that time. Anything the script prints is added to `tracker.log`.

## How it works

| Part | What it does |
| --- | --- |
| `fetch_page` | Downloads the page, with a timeout and a clear message for each kind of failure |
| `get_products` / `parse_product` | Finds each product on the page with BeautifulSoup and reads its title and price, skipping any that look wrong |
| `load_last_run` | Reads the history CSV and returns the prices from the most recent check |
| `find_changes` / `report_changes` | Compares old and new prices and prints the differences |
| `save_prices` | Adds the new check to the end of the CSV, with one timestamp for the whole run |

The history file has three columns: `timestamp`, `title` and `price`. `sample_data/` holds an example history file.

## Limitations

- It only reads the page you give it, not the following pages of a listing.
- It looks for the HTML structure used by the practice site (`article.product_pod` and `price_color`). A different site needs those lines changed in `parse_product` and `get_products`.
- It reads prices in pounds only, and ignores any product it hasn't seen before.
- It prints changes in the terminal. It doesn't send emails or notifications yet.
- Before scraping a real site, check its terms of service and `robots.txt`, and use an official API or data feed if there is one. This project uses [books.toscrape.com](https://books.toscrape.com/), which exists for scraping practice.

## Ideas for later

- Follow the "next page" links to read a whole catalogue
- Send an email when a price drops below a target
- Make the page structure a setting, so one script can read several sites
- Draw a chart of how a price has moved over time
