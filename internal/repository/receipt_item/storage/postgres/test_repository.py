import typing as t
import uuid

import psycopg
import pytest
from pydantic import UUID4

from internal.domain.receipt.item import ReceiptItem
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
        split_by_users=set(["user1", "user2"])
    )


def test_create(repo, receipt_uuid, item):
    repo.create(receipt_uuid, item)

    created_item = repo.read_by_uuid(item.uuid)
    assert created_item.uuid == item.uuid
    assert created_item.product == item.product
    assert created_item.quantity == item.quantity
    assert created_item.price == item.price
    assert created_item.split_by_users == item.split_by_users


@pytest.fixture(scope="function")
def items() -> t.List[ReceiptItem]:
    return [
        ReceiptItem(
            product="pepsi cola",
            quantity=3,
            price=5678,
            split_by_users=set(["user1", "user2"])
        ),
        ReceiptItem(
            product="banan",
            quantity=3,
            price=100,
            split_by_users=set(["user1", "user2"])
        ),
        ReceiptItem(
            product="apple",
            quantity=3,
            price=100,
            split_by_users=set(["user1", "user2"])
        )
    ]


def test_create_many(repo, receipt_uuid, items):

    repo.create_many(receipt_uuid, items)

    created_items = repo.read_many(receipt_uuid)

    assert len(items) == len(created_items)


def test_update(repo, receipt_uuid, item):
    repo.create(receipt_uuid, item)

    item.product = "new name"
    item.quantity = 777
    item.quantity += 1
    item.split("user1")

    repo.update(receipt_uuid, item)

    updated_item = repo.read_by_uuid(item.uuid)

    assert item.product == updated_item.product
    assert item.quantity == updated_item.quantity


def test_update_many(repo, receipt_uuid, items):
    repo.create_many(receipt_uuid, items)

    items[1].product = "new name"
    items[1].quantity = 777
    items[1].split("user1")

    repo.update_many(receipt_uuid, items)

    updated_item = repo.read_by_uuid(items[1].uuid)

    assert items[1].product == updated_item.product
    assert items[1].quantity == updated_item.quantity
