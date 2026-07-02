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


def test_bulk_discount_applies_at_ten_units():
    subtotal = 10 * 900  # ten usb-cables
    expected = subtotal - subtotal // 20 + FLAT_SHIPPING
    assert calculate_total({"usb-cable": 10}) == expected
