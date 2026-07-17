"""Order pricing for the demo order service.

Both walkthrough branches (``collide-a`` and ``collide-b``) change the
discount section of ``calculate_total`` below. That is deliberate: it gives
you two pull requests that edit the same lines of the same file, which is
the situation the walkthrough exists to demonstrate.
"""

from orders.catalog import unit_price

FLAT_SHIPPING = 500  # cents


def calculate_total(items: dict[str, int], currency: str) -> int:
    """Return the order total for a ``{sku: quantity}`` mapping in ``currency`` minor units."""
    if not items:
        raise ValueError("an order needs at least one item")

    subtotal = 0
    for sku, quantity in items.items():
        if quantity < 1:
            raise ValueError(f"quantity for {sku!r} must be positive")
        subtotal += unit_price(sku) * quantity

    # Discount rules: none yet. Orders pay the plain subtotal.
    discount = 0

    return subtotal - discount + FLAT_SHIPPING
