from orders.receipt import receipt_preview


def test_preview_line():
    assert receipt_preview({"mouse": 1}).startswith("total: ")
