from tracker import find_changes


def test_find_changes_reports_a_drop():
    """A price that went down is reported with its old and new value."""
    old_prices = {"Book A": 10.00}
    new_products = [{"title": "Book A", "price": 8.00}]

    result = find_changes(old_prices, new_products)

    assert result == [{"title": "Book A", "old": 10.00, "new": 8.00}]