from tracker import find_changes


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