import typing as t
import uuid

import psycopg
import pytest

from internal.domain.receipt.item import ReceiptItem, Split, Choice
from internal.domain.receipt.uuid import ReceiptUUID
from internal.repository.receipt_item.storage.postgres.repository import Repository


@pytest.fixture(scope="session")
def conn() -> psycopg.Connection:
    conn = psycopg.connect("postgresql://smith:pwd@localhost:5432")
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def repo(conn) -> Repository:
    repo = Repository(conn)

    repo.init_schema()

    yield repo

    repo.clean()


@pytest.fixture(scope="function")
def receipt_uuid() -> ReceiptUUID:
    return ReceiptUUID(uuid.uuid4())


@pytest.fixture(scope="function")
def item() -> ReceiptItem:
    return ReceiptItem(
        product="pepsi cola",
        quantity=3,
        price=5678,
        splits={
            Split(username="user1"),
            Split(username="user2")
        }
    )


@pytest.fixture(scope="function")
def receipt_items() -> t.List[ReceiptItem]:
    return [
        ReceiptItem(
            product="pepsi cola",
            quantity=3,
            price=5678,
            splits={
                Split(username="user1", quantity=2),
                Split(username="user2")
            }
        ),
        ReceiptItem(
            product="banan",
            quantity=3,
            price=100,
            splits={
                Split(username="user1"),
                Split(username="user2", quantity=2)
            }
        ),
        ReceiptItem(
            product="apple",
            quantity=3,
            price=100,
            split_error_message="receipt item can't be split",
            splits={
                Split(username="user1"),
                Split(username="user2")
            }
        ),
    ]


def test_create_many(repo, receipt_uuid, receipt_items):
    repo.create_many(receipt_uuid, receipt_items)

    created_items = repo.read_by_receipt_uuid(receipt_uuid)

    assert len(receipt_items) == len(created_items)


def test_update_many(repo, receipt_uuid, receipt_items):
    repo.create_many(receipt_uuid, receipt_items)

    receipt_items[1].product = "new name"
    receipt_items[1].quantity = 777
    receipt_items[1].split(
        Choice(
            username="user1",
            uuid=receipt_items[1].uuid,
        )
    )

    repo.update_many(receipt_uuid, receipt_items)

    updated_item = repo.read_by_uuid(receipt_items[1].uuid)

    assert receipt_items[1].product == updated_item.product
    assert receipt_items[1].quantity == updated_item.quantity
