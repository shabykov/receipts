import typing as t

import psycopg
from pydantic import UUID4

from internal.domain.receipt.item import (
    Item,
    Creator,
    Updater,
    Reader,
)
from internal.domain.receipt.item.error import (
    ReceiptItemCreateError,
    ReceiptItemUpdateError,
    ReceiptItemReadError
)

CREATE_SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS tbl_receipt_item (
        receipt_uuid text NOT NULL,
        uuid         varchar(255) PRIMARY KEY,
        product      text,
        quantity     text,
        price        numeric(6),
        created_at   timestamp without time zone,
        UNIQUE(receipt_uuid, product)
    );
"""

CLEAN_SCHEMA_SQL = """
    truncate table tbl_receipt_item;
"""

INSERT_RECEIPT_ITEM_SQL = """
    INSERT INTO tbl_receipt_item (
        receipt_uuid,
        uuid, 
        product, 
        quantity, 
        price,
        created_at
    )
    VALUES (%s, %s, %s, %s, %s, %s) 
    ON CONFLICT (receipt_uuid, product) 
    DO NOTHING;
"""

UPSERT_RECEIPT_ITEM_SQL = """
    INSERT INTO tbl_receipt_item (
        receipt_uuid,
        uuid,
        product,
        quantity,
        price
    )
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT(uuid)
    DO UPDATE SET
        product = EXCLUDED.product, 
        quantity = EXCLUDED.quantity,
        price = EXCLUDED.price;
"""

SELECT_RECEIPT_ITEM_SQL = """
    SELECT
        uuid, 
        product, 
        quantity, 
        price,
        created_at
    FROM tbl_receipt_item 
    WHERE uuid = %(uuid)s;
"""

SELECT_RECEIPT_ITEMS_SQL = """
    SELECT
        uuid, 
        product, 
        quantity, 
        price,
        created_at
    FROM tbl_receipt_item 
    WHERE receipt_uuid=%(receipt_uuid)s
    ORDER BY created_at
    LIMIT %(limit)s
    OFFSET %(offset)s;
"""


class Repository(Creator, Updater, Reader):
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn

    def init_schema(self):
        with self._conn.cursor() as cur:
            cur.execute(query=CREATE_SCHEMA_SQL)
        self._conn.commit()

    def clean(self):
        with self._conn.cursor() as cur:
            cur.execute(query=CLEAN_SCHEMA_SQL)
        self._conn.commit()

    def create(self, receipt_uuid: UUID4, item: Item) -> t.Optional[ReceiptItemCreateError]:
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    query=INSERT_RECEIPT_ITEM_SQL,
                    params=(
                        receipt_uuid,
                        item.uuid,
                        item.product,
                        item.quantity,
                        item.price,
                        item.created_at
                    )
                )
        except psycopg.errors.DatabaseError as e:
            self._conn.rollback()
            return ReceiptItemCreateError(
                message="insert items err: %s" % e,
                code="database_error"
            )
        else:
            self._conn.commit()
        return None

    def create_many(self, receipt_uuid: UUID4, items: t.List[Item]) -> t.Optional[ReceiptItemCreateError]:
        try:
            with self._conn.cursor() as cur:
                cur.executemany(
                    query=INSERT_RECEIPT_ITEM_SQL,
                    params_seq=[
                        (
                            receipt_uuid,
                            item.uuid,
                            item.product,
                            item.quantity,
                            item.price,
                            item.created_at
                        ) for item in items
                    ]
                )
        except psycopg.errors.DatabaseError as e:
            self._conn.rollback()
            return ReceiptItemCreateError(
                message="insert items err: %s" % e,
                code="database_error"
            )
        else:
            self._conn.commit()
        return None

    def update(self, receipt_uuid: UUID4, item: Item) -> t.Optional[ReceiptItemUpdateError]:
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    query=UPSERT_RECEIPT_ITEM_SQL,
                    params=(
                        receipt_uuid,
                        item.uuid,
                        item.product,
                        item.quantity,
                        item.price
                    )
                )
        except psycopg.errors.DatabaseError as e:
            self._conn.rollback()
            return ReceiptItemUpdateError(
                message="upsert items err: %s" % e,
                code="database_error"
            )
        else:
            self._conn.commit()
        return None

    def update_many(self, receipt_uuid: UUID4, items: t.List[Item]) -> t.Optional[ReceiptItemUpdateError]:
        try:
            with self._conn.cursor() as cur:
                cur.executemany(
                    query=UPSERT_RECEIPT_ITEM_SQL,
                    params_seq=[
                        (
                            receipt_uuid,
                            item.uuid,
                            item.product,
                            item.quantity,
                            item.price
                        ) for item in items
                    ]
                )
        except psycopg.errors.DatabaseError as e:
            self._conn.rollback()
            return ReceiptItemUpdateError(
                message="upsert items err: %s" % e,
                code="database_error"
            )
        else:
            self._conn.commit()
        return None

    def read_by_uuid(self, uuid: UUID4) -> t.Tuple[
        t.Optional[Item], t.Optional[ReceiptItemReadError]
    ]:
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    SELECT_RECEIPT_ITEM_SQL,
                    params={
                        "uuid": str(uuid)
                    }
                )

                row = cur.fetchone()
        except psycopg.errors.DatabaseError as e:
            return None, ReceiptItemReadError(
                message="select item err: %s" % e,
                code="database_error"
            )

        return Item(
            uuid=row[0],
            product=row[1],
            quantity=row[2],
            price=row[3],
            created_at=row[4]
        ), None

    def read_many(self, receipt_uuid: UUID4, limit: int = 100, offset: int = 0) -> t.Tuple[
        t.List[Item], t.Optional[ReceiptItemReadError]
    ]:
        items = []
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    SELECT_RECEIPT_ITEMS_SQL,
                    params={
                        "receipt_uuid": str(receipt_uuid),
                        "limit": limit,
                        "offset": offset
                    }
                )

                for row in cur:
                    items.append(
                        Item(
                            uuid=row[0],
                            product=row[1],
                            quantity=row[2],
                            price=row[3],
                            created_at=row[4]
                        )
                    )
        except psycopg.errors.DatabaseError as e:
            return items, ReceiptItemReadError(
                message="select items err: %s" % e,
                code="database_error"
            )

        return items, None
