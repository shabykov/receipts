import pytest

from internal.domain.receipt import Receipt
from internal.domain.receipt.split import Split


@pytest.fixture()
def receipt():
    return Receipt(

    )


def splits():
    return [
        Split()
    ]


def test_receipt_split_by(receipt, splits):
    receipt.split_by(splits)
