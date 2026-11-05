# Price Tracker
![Tests](https://github.com/playfu1-d0ubt/price-tracker/actions/workflows/tests.yml/badge.svg)

A command-line tool, written in Python, that checks the prices on a web page, keeps a history of every check, and tells you which prices have dropped or risen since the last time. The practice site it reads is built for scraping practice.

## How it works

1. Download the page, with a timeout and a clear message for each kind of failure.
2. Find each product with BeautifulSoup and read its title and price. Products that look wrong are skipped and logged as a warning.
3. Read the history CSV and take the prices from the most recent check.
4. Compare old and new prices, and print every change, biggest drops first.
5. Add the new check to the end of the CSV, with one timestamp for the whole run.
6. Log what happened (products found, first run, prices saved) with a time and a level, so a run you did not watch can be read later.

The history file has three columns: `timestamp`, `title` and `price`. Prices are matched by product title.

## Example

The practice site's prices never change, so to show a change I edited three prices in the history file by hand and ran the script again.

```
$ python tracker.py
2026-11-05 09:00:01 INFO Found 20 products
DROPPED: Libertarianism for Beginners  £55.00 -> £51.33
DROPPED: Mesaerion: The Best Science Fiction Stories 1800-1849  £40.50 -> £37.59
ROSE: It's Only the Himalayas  £45.00 -> £45.17
2026-11-05 09:00:01 INFO Saved 20 prices to prices.csv
```

When nothing has changed it prints `No price changes since the last check.`

The price changes are the result, so they are printed plainly. The lines with a time and a level are the log of what the program did.

## How to run

```bash
git clone https://github.com/playfu1-d0ubt/price-tracker.git
cd price-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python tracker.py                           # checks the default practice site
python tracker.py URL                       # checks a different page
python tracker.py URL -o other_prices.csv   # keeps that page's history in its own file
python tracker.py --help                    # shows all options
python -m pytest                            # run the tests
```

Use a separate `-o` file for each page you track. Mixing two pages in one file would compare the wrong products.

### Running it every day

On Linux, `cron` can run it on a schedule. Run `crontab -e` and add a line like this, which checks every day at 9am (use the full path to your own project folder):

```
0 9 * * * cd /home/YOUR-NAME/projects/price-tracker && ./venv/bin/python tracker.py >> tracker.log 2>&1
```

The computer needs to be switched on at that time. Everything the script prints and logs is added to `tracker.log`. Each log line has a date and time, so you can see which run it came from.

## Files

| File | What it does |
| --- | --- |
| `tracker.py` | Downloads the page, finds the products, compares prices, reports changes, saves the history and logs progress |
| `requirements.txt` | The Python packages needed |
| `sample_data/` | An example history file |
| `tests/test_tracker.py` | Tests for finding changes, reading the CSV, parsing the HTML and saving prices |
| `pytest.ini` | Settings for `pytest` |
| `.github/workflows/tests.yml` | Runs the tests on GitHub on every push |

The tests use small fake data and temporary files, so no website is needed and your real `prices.csv` is never touched.

## Limitations

- It only reads the page you give it, not the following pages of a listing.
- It looks for the HTML structure used by the practice site (`article.product_pod` and `price_color`). A different site needs those lines changed in `parse_product` and `get_products`.
- It reads prices in pounds only, and ignores any product it hasn't seen before.
- It prints changes in the terminal. It doesn't send emails or notifications yet.
- Logging goes to the terminal only. It is not saved to a file unless `cron` or `>>` does that.
- Before scraping a real site, check its terms of service and `robots.txt`, and use an official API or data feed if there is one. This project uses [books.toscrape.com](https://books.toscrape.com/), which exists for scraping practice.
- Tested on Linux Mint only.

## What I learned

I practised downloading a web page with `requests`, reading it with BeautifulSoup, building a command-line tool with `argparse`, keeping a CSV history, handling errors with clear messages, and scheduling a script with `cron`. I added tests with `pytest` and a GitHub Actions workflow that runs them on every push.

The practice site's prices never change, so I edited prices in the history file by hand to check the comparison worked.

Later I swapped most of the `print` lines for the `logging` module. I learned to split the two jobs: `print` is for the result the user wants to read, and `logging` is the diary of what the program did, with a time and a level (`INFO`, `WARNING`). I set it up once in `main`, so importing the file in tests does not switch logging on.

The bug that surprised me was line order in `tracker.log`. Log lines go to stderr and `print` goes to stdout. When both go to a file, Python holds the `print` text until the end, so the result line landed after `Saved`. I only saw it by running the script twice into a file, because the first run has no result line. Adding `flush=True` to those `print` calls fixed it.