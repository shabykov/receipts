import uuid

import pytest

from internal.domain.receipt import Receipt
from internal.domain.receipt.item import ReceiptItem, Choice


@pytest.fixture()
def receipt_uuid():
    return uuid.uuid4()


@pytest.fixture()
def receipt_item_choice_1():
    return Choice(
        uuid=uuid.uuid4(),
        quantity=1,
        username="user1"
    )


@pytest.fixture()
def receipt_item_choice_2():
    return Choice(
        uuid=uuid.uuid4(),
        quantity=1,
        username="user1"
    )


@pytest.fixture()
def receipt_item_choice_3():
    return Choice(
        uuid=uuid.uuid4(),
        quantity=1,
        username="user1"
    )


@pytest.fixture()
def receipt_item_choice_4():
    return Choice(
        uuid=uuid.uuid4(),
        quantity=1,
        username="user1"
    )


@pytest.fixture()
def receipt_items(receipt_item_choice_1, receipt_item_choice_2, receipt_item_choice_3, receipt_item_choice_4):
    return [
        ReceiptItem(
            uuid=receipt_item_choice_1.uuid,
            product="Product 1",
            quantity=1,
            price=1000,
        ),
        ReceiptItem(
            uuid=receipt_item_choice_2.uuid,
            product="Product 2",
            quantity=2,
            price=1000,
        ),
        ReceiptItem(
            uuid=receipt_item_choice_3.uuid,
            product="Product 3",
            quantity=3,
            price=1000,
        ),
        ReceiptItem(
            uuid=receipt_item_choice_4.uuid,
            product="Product 4",
            quantity=1,
            price=1000,
        ),
    ]


@pytest.fixture()
def receipt(receipt_uuid, receipt_items):
    return Receipt(
        user_id=1,
        uuid=receipt_uuid,
        items=receipt_items,
    )


def test_split(receipt, receipt_item_choice_1, receipt_item_choice_2, receipt_item_choice_3, receipt_item_choice_4):
    receipt.split(
        [
            receipt_item_choice_1,
            receipt_item_choice_2,
            receipt_item_choice_3,
            receipt_item_choice_4,
        ]
    )
    assert "user1" in receipt.items[0].splits
    assert "user1" in receipt.items[1].splits
    assert "user1" in receipt.items[2].splits
    assert "user1" in receipt.items[3].splits

    receipt.split(
        [
            Choice(
                username="user2",
                uuid=receipt_item_choice_2.uuid,
                quantity=receipt_item_choice_2.quantity
            ),
            Choice(
                username="user2",
                uuid=receipt_item_choice_3.uuid,
                quantity=receipt_item_choice_3.quantity
            )
        ]
    )
    assert "user2" in receipt.items[1].splits
    assert "user2" in receipt.items[2].splits


def test_result(receipt, receipt_item_choice_1, receipt_item_choice_2, receipt_item_choice_3, receipt_item_choice_4):
    receipt.split(
        [
            receipt_item_choice_1,
            receipt_item_choice_2,
            receipt_item_choice_3,
            receipt_item_choice_4,
        ]
    )
    receipt.split(
        [
            Choice(
                username="user2",
                uuid=receipt_item_choice_2.uuid,
                quantity=receipt_item_choice_2.quantity
            ),
            Choice(
                username="user2",
                uuid=receipt_item_choice_3.uuid,
                quantity=receipt_item_choice_3.quantity
            ),
        ]
    )
    splits = receipt.results()
    assert len(splits) == 2
    assert splits[0].username == "user1"
    assert splits[0].amount == 1000 + 500 + 1000 / 3 + 1000
    assert splits[1].username == "user2"
    assert splits[1].amount == 500 + 1000 / 3


def test_dump(receipt):

    resp = receipt.model_dump()
    assert resp
