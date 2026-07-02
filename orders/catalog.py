"""A tiny in-memory product catalog for the demo order service."""

# Prices are in cents to keep the arithmetic honest.
CATALOG = {
    "keyboard": 4900,
    "mouse": 1900,
    "monitor": 15900,
    "usb-cable": 900,
    "webcam": 6900,
}


def unit_price(sku: str) -> int:
    """Return the unit price for a SKU, in cents."""
    try:
        return CATALOG[sku]
    except KeyError:
        raise KeyError(f"unknown SKU: {sku!r}") from None
