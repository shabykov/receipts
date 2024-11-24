import uuid

import pytest

from .error import ReceiptItemSplitError
from .model import ReceiptItem, Choice


@pytest.fixture()
def receipt_item_uuid():
    return uuid.uuid4()


@pytest.fixture()
def choice1(receipt_item_uuid):
    return Choice(
        uuid=receipt_item_uuid,
        username="user1",
        quantity=1
    )


@pytest.fixture()
def choice2(receipt_item_uuid):
    return Choice(
        uuid=receipt_item_uuid,
        username="user2",
        quantity=1
    )


@pytest.fixture()
def choice3(receipt_item_uuid):
    return Choice(
        uuid=receipt_item_uuid,
        username="user3",
        quantity=2
    )


def test_split(receipt_item_uuid, choice1, choice2, choice3):
    item = ReceiptItem(uuid=receipt_item_uuid, quantity=3)
    item.split(choice1)
    item.split(choice1)
    assert len(item.splits) == 1
    assert "user1" in item.splits

    item.split(choice2)
    assert len(item.splits) == 2
    assert "user2" in item.splits

    with pytest.raises(ReceiptItemSplitError) as err:
        item.split(choice3)

    assert "receipt item can't be split" in str(err.value)


def test_is_splittable(receipt_item_uuid, choice1, choice2):
    item = ReceiptItem(uuid=receipt_item_uuid, quantity=2)
    assert item.is_splittable() is True

    item.split(choice1)
    assert item.is_splittable() is True

    item.split(choice2)
    assert item.is_splittable() is False


def test_price_per_user(receipt_item_uuid, choice1, choice2):
    item = ReceiptItem(uuid=receipt_item_uuid, quantity=2, price=1000)
    assert item.price_per_quantity() == 500

    item.split(choice1)
    assert item.price_per_user(choice1.username) == 500

    item.split(choice2)
    assert item.price_per_user(choice2.username) == 500

    item = ReceiptItem(uuid=receipt_item_uuid, quantity=3, price=1500)
    choice1.quantity = 2
    item.split(choice1)
    assert item.price_per_user(choice1.username) == 1000
