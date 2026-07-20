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


def test_large_cart_flat_discount():
    # 1 monitor = 15900 cents subtotal (>= 5000) -> flat $10 (1000) off.
    assert calculate_total({"monitor": 1}) == 15900 - 1000 + FLAT_SHIPPING


def test_no_large_cart_discount_small_order():
    # 1 mouse = 1900 cents subtotal is below $50 -> no discount.
    assert calculate_total({"mouse": 1}) == 1900 + FLAT_SHIPPING
