"""Tests for price-tracker"""

from bs4 import BeautifulSoup

from tracker import find_changes, get_products, load_last_run, parse_product


def test_find_changes_reports_a_drop():
    """A price that went down is reported with its old and new value."""
    old_prices = {"Book A": 10.00}
    new_products = [{"title": "Book A", "price": 8.00}]

    result = find_changes(old_prices, new_products)

    assert result == [{"title": "Book A", "old": 10.00, "new": 8.00}]

def test_find_changes_ignores_an_unchanged_price():
    """A price that stayed the same is not reported."""
    old_prices = {"Book A": 10.00}
    new_products = [{"title": "Book A", "price": 10.00}]

    assert find_changes(old_prices, new_products) == []


def test_find_changes_ignores_a_new_product():
    """A product with no old price has nothing to compare with, so it is not reported."""
    old_prices = {}
    new_products = [{"title": "Book A", "price": 10.00}]

    assert find_changes(old_prices, new_products) == []

def test_find_changes_empty_input():
    """Two empty inputs have nothing to report"""
    old_prices = {}
    new_products = []
    assert find_changes(old_prices, new_products) == []

def test_load_last_run_returns_empty_when_file_is_missing(tmp_path):
    """With no CSV yet, there is no last run, so the result is empty."""
    missing_file = tmp_path / "does_not_exist.csv"

    assert load_last_run(missing_file) == {}

def test_load_last_run_uses_only_the_latest_run(tmp_path):
    """If the CSV has multiple runs, only the latest one is used."""
    file_path = tmp_path / "prices.csv"
    file_path.write_text(
        "timestamp,title,price\n"
        "2026-10-01 09:00:00,Book A,10.00\n"
        "2026-10-02 09:00:00,Book A,8.00\n"
    )

    result = load_last_run(file_path)

    assert result == {"Book A": 8.00}

GOOD_PRODUCT = (
    '<article class="product_pod">'
    '<h3><a title="Book A">Book A</a></h3>'
    '<p class="price_color">£51.77</p>'
    "</article>"
)

BAD_PRODUCT = (
    '<article class="product_pod">'
    '<h3><a title="Book A">Book A</a></h3>'
    "</article>"
)

def test_parse_product_reads_title_and_price():
    """The title and a numeric price are pulled out of one product's HTML."""
    product = BeautifulSoup(GOOD_PRODUCT, "html.parser").find("article")

    assert parse_product(product) == {"title": "Book A", "price": 51.77}

def test_get_products_skips_a_product_with_no_price():
    """If a product has no price, it is skipped."""
    html = f"<html><body>{GOOD_PRODUCT}{BAD_PRODUCT}</body></html>"

    assert get_products(html) == [{"title": "Book A", "price": 51.77}]