import psycopg
import pytest

from internal.domain.receipt import Receipt, ReceiptItem
from internal.repository.receipt.storage.postgres.repository import Repository
from internal.repository.receipt_item.storage.postgres.repository import Repository as ItemRepository


@pytest.fixture(scope="session")
def conn() -> psycopg.Connection:
    conn = psycopg.connect("postgresql://smith:pwd@localhost:5432")
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def item_repo(conn) -> ItemRepository:
    repo = ItemRepository(conn)

    repo.init_schema()

    yield repo

    repo.clean()


@pytest.fixture(scope="function")
def repo(conn, item_repo) -> Repository:
    repo = Repository(conn, item_repo)

    repo.init_schema()

    yield repo

    repo.clean()


@pytest.fixture(scope="function")
def receipt() -> Receipt:
    return Receipt(
        user_id=3,
        store_name="magnum",
        store_addr="dostyk avenue 46",
        items=[
            ReceiptItem(
                product="fanta",
                quantity=2,
                price=1000
            ),
            ReceiptItem(
                product="coco col 1",
                quantity=1,
                price=1000
            ),
            ReceiptItem(
                product="coco col 3",
                quantity=1,
                price=1000
            )
        ],
        subtotal=1234.34535,
        tips=123.0,
        total=1234.34535 + 123.0
    )


def test_create(repo, receipt):
    repo.create(receipt)

    created_receipt = repo.read_by_uuid(receipt.uuid)

    assert receipt.uuid == created_receipt.uuid
    assert receipt.user_id == created_receipt.user_id


def test_update(repo, receipt):
    err = repo.create(receipt)
    assert err is None

    repo.read_by_uuid(receipt.uuid)

    receipt.total = 2999.9999
    receipt.subtotal = 1999.8888
    receipt.items[1].quantity = 5

    repo.update(receipt)
    assert err is None

    updated_receipt = repo.read_by_uuid(receipt.uuid)

    assert receipt.uuid == updated_receipt.uuid
    assert receipt.total == updated_receipt.total
    assert receipt.subtotal == updated_receipt.subtotal
