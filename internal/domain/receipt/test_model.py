import uuid

import pytest

from internal.domain.receipt import Receipt
from internal.domain.receipt import ReceiptItem
from internal.domain.receipt.item import ReceiptItemSplitError


@pytest.fixture()
def receipt_uuid():
    return uuid.uuid4()


@pytest.fixture()
def receipt_item_1():
    return uuid.uuid4()


@pytest.fixture()
def receipt_item_2():
    return uuid.uuid4()


@pytest.fixture()
def receipt_item_3():
    return uuid.uuid4()


@pytest.fixture()
def receipt_item_4():
    return uuid.uuid4()


@pytest.fixture()
def receipt_items(receipt_item_1, receipt_item_2, receipt_item_3, receipt_item_4):
    return [
        ReceiptItem(
            uuid=receipt_item_1,
            product="Product 1",
            quantity=1,

        ),
        ReceiptItem(
            uuid=receipt_item_2,
            product="Product 2",
            quantity=2,
        ),
        ReceiptItem(
            uuid=receipt_item_3,
            product="Product 3",
            quantity=3,
        ),
        ReceiptItem(
            uuid=receipt_item_4,
            product="Product 4",
            quantity=1,
        ),
    ]


@pytest.fixture()
def receipt(receipt_uuid, receipt_items):
    return Receipt(
        user_id=1,
        uuid=receipt_uuid,
        items=receipt_items,
    )


def test_split(receipt, receipt_item_1, receipt_item_2, receipt_item_3, receipt_item_4):
    receipt.split("user1", [receipt_item_1, receipt_item_2, receipt_item_3, receipt_item_4])
    assert "user1" in receipt.items[0].split_by_users
    assert "user1" in receipt.items[1].split_by_users
    assert "user1" in receipt.items[2].split_by_users
    assert "user1" in receipt.items[3].split_by_users

    receipt.split("user2", [receipt_item_2, receipt_item_3])
    assert "user2" in receipt.items[1].split_by_users
    assert "user2" in receipt.items[2].split_by_users

    with pytest.raises(ReceiptItemSplitError) as err:
        receipt.split("user3", [receipt_item_4])

    assert "receipt item has already splited" in str(err.value)
