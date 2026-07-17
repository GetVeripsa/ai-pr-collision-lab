"""Receipt preview for the order flow.

Renders a one-line total preview for a cart. Uses the pricing contract as it
exists on main today.
"""
from orders.pricing import calculate_total


def receipt_preview(items: dict[str, int]) -> str:
    """Return a short preview line for the cart's total."""
    total = calculate_total(items)
    return f"total: {total} cents"
