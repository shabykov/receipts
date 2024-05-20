import typing as t
import uuid
from logging import Logger, getLogger

import psycopg
import pytest
from pydantic import UUID4

from internal.domain.receipt.item import Item
from internal.repository.receipt_item.storage.postgres.repository import Repository


@pytest.fixture(scope="session")
def conn() -> psycopg.Connection:
    conn = psycopg.connect("postgresql://smith:pwd@localhost:5432")
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def logger() -> Logger:
    return getLogger("test")


@pytest.fixture(scope="function")
def repo(conn, logger) -> Repository:
    repo = Repository(conn, logger)

    repo.init_schema()

    yield repo

    repo.clean()


@pytest.fixture(scope="function")
def receipt_uuid() -> UUID4:
    return uuid.uuid4()


@pytest.fixture(scope="function")
def item() -> Item:
    return Item(
        product="pepsi cola",
        quantity=3,
        price=5678
    )


def test_create(repo, receipt_uuid, item):
    err = repo.create(receipt_uuid, item)
    assert err is None

    created_item, err = repo.read_by_uuid(item.uuid)
    assert err is None

    assert created_item == item


@pytest.fixture(scope="function")
def items() -> t.List[Item]:
    return [
        Item(
            product="pepsi cola",
            quantity=3,
            price=5678
        ),
        Item(
            product="banan",
            quantity=3,
            price=100,
        ),
        Item(
            product="apple",
            quantity=3,
            price=100,
        )
    ]


def test_create_many(repo, receipt_uuid, items):
    err = repo.create_many(receipt_uuid, items)
    assert err is None

    created_items, err = repo.read_many(receipt_uuid)
    assert err is None

    assert len(items) == len(created_items)


def test_update(repo, receipt_uuid, item):
    err = repo.create(receipt_uuid, item)
    assert err is None

    created_item, err = repo.read_by_uuid(item.uuid)
    assert err is None

    item.product = "new name"
    item.quantity = 777

    err = repo.update(receipt_uuid, item)
    assert err is None

    updated_item, err = repo.read_by_uuid(item.uuid)
    assert err is None

    assert item.product == updated_item.product
    assert item.quantity == updated_item.quantity


def test_update_many(repo, receipt_uuid, items):
    err = repo.create_many(receipt_uuid, items)
    assert err is None

    items[1].product = "new name"
    items[1].quantity = 777

    err = repo.update_many(receipt_uuid, items)
    assert err is None

    updated_item, err = repo.read_by_uuid(items[1].uuid)
    assert err is None

    assert items[1].product == updated_item.product
    assert items[1].quantity == updated_item.quantity
