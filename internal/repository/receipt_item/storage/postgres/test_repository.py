import typing as t
import uuid

import psycopg
import pytest
from pydantic import UUID4

from internal.domain.receipt.item import ReceiptItem, Split
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
def receipt_uuid() -> UUID4:
    return uuid.uuid4()


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
def items() -> t.List[ReceiptItem]:
    return [
        ReceiptItem(
            product="pepsi cola",
            quantity=3,
            price=5678,
            splits={
                Split(username="user1"),
                Split(username="user2")
            }
        ),
        ReceiptItem(
            product="banan",
            quantity=3,
            price=100,
            splits={
                Split(username="user1"),
                Split(username="user2")
            }
        ),
        ReceiptItem(
            product="apple",
            quantity=3,
            price=100,
            splits={
                Split(username="user1"),
                Split(username="user2")
            }
        )
    ]


def test_create_many(repo, receipt_uuid, items):

    repo.create_many(receipt_uuid, items)

    created_items = repo.read_many(receipt_uuid)

    assert len(items) == len(created_items)


def test_update_many(repo, receipt_uuid, items):
    repo.create_many(receipt_uuid, items)

    items[1].product = "new name"
    items[1].quantity = 777
    items[1].split(
        Split(username="user1", uuid=items[1].uuid)
    )

    repo.update_many(receipt_uuid, items)

    updated_item = repo.read_by_uuid(items[1].uuid)

    assert items[1].product == updated_item.product
    assert items[1].quantity == updated_item.quantity
