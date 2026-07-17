import pytest

from orders.pricing import FLAT_SHIPPING, calculate_total


def test_single_item_total():
    assert calculate_total({"mouse": 1}, "usd") == 1900 + FLAT_SHIPPING


def test_multiple_items_total():
    assert calculate_total({"keyboard": 1, "mouse": 2}, "usd") == 4900 + 3800 + FLAT_SHIPPING


def test_empty_order_rejected():
    with pytest.raises(ValueError):
        calculate_total({}, "usd")


def test_zero_quantity_rejected():
    with pytest.raises(ValueError):
        calculate_total({"mouse": 0}, "usd")


def test_unknown_sku_rejected():
    with pytest.raises(KeyError):
        calculate_total({"flux-capacitor": 1}, "usd")
