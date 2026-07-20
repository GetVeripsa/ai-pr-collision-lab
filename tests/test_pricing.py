import pytest

from orders.pricing import FLAT_SHIPPING, calculate_total


def test_single_item_total():
    assert calculate_total({"mouse": 1}) == 1900 + FLAT_SHIPPING


def test_multiple_items_total():
    assert calculate_total({"keyboard": 1, "mouse": 2}) == 4900 + 3800 + FLAT_SHIPPING


def test_empty_order_rejected():
    with pytest.raises(ValueError):
        calculate_total({})


def test_zero_quantity_rejected():
    with pytest.raises(ValueError):
        calculate_total({"mouse": 0})


def test_unknown_sku_rejected():
    with pytest.raises(KeyError):
        calculate_total({"flux-capacitor": 1})


def test_bulk_discount_applies_over_100_dollars():
    # 1 monitor = 15900 cents subtotal -> 5% (795) off, plus flat shipping.
    assert calculate_total({"monitor": 1}) == 15900 - 795 + FLAT_SHIPPING


def test_no_bulk_discount_under_threshold():
    # 1 mouse = 1900 cents subtotal is below $100 -> no discount.
    assert calculate_total({"mouse": 1}) == 1900 + FLAT_SHIPPING
