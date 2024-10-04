import typing as t
from logging import getLogger

import psycopg
from pydantic import UUID4

from internal.domain.receipt.item import (
    ReceiptItem,
    ICreator,
    IUpdater,
    IReader,
)
from internal.domain.receipt.item import (
    ReceiptItemCreateError,
    ReceiptItemUpdateError,
    ReceiptItemReadError,
)

logger = getLogger("receipt_item.storage.postgres")

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


class Repository(ICreator, IUpdater, IReader):
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn
        self.init_schema()

    def init_schema(self):
        with self._conn.cursor() as cur:
            cur.execute(query=CREATE_SCHEMA_SQL)
        self._conn.commit()
        logger.info("receipt item schema is ready")

    def clean(self):
        with self._conn.cursor() as cur:
            cur.execute(query=CLEAN_SCHEMA_SQL)
        self._conn.commit()
        logger.info("receipt item schema cleaned")

    def create(self, receipt_uuid: UUID4, item: ReceiptItem):
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
            raise ReceiptItemCreateError("insert items err: %s" % e)
        else:
            self._conn.commit()
            logger.info("receipt item created: receipt_uuid=%s, uuid=%s" % (receipt_uuid, item.uuid))
        return None

    def create_many(self, receipt_uuid: UUID4, items: t.List[ReceiptItem]):
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
            raise ReceiptItemCreateError("insert items err: %s" % e)
        else:
            self._conn.commit()
            logger.info(
                "receipt items created: receipt_uuid=%s, items_count=%d" % (receipt_uuid, len(items))
            )
        return None

    def update(self, receipt_uuid: UUID4, item: ReceiptItem):
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
            raise ReceiptItemUpdateError("upsert item err: %s" % e)
        else:
            self._conn.commit()
            logger.info("receipt item updated: receipt_uuid=%s, uuid=%s" % (receipt_uuid, item.uuid))
        return None

    def update_many(self, receipt_uuid: UUID4, items: t.List[ReceiptItem]):
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
            raise ReceiptItemUpdateError("upsert items err: %s" % e)
        else:
            self._conn.commit()
            logger.info(
                "receipt items updated: receipt_uuid=%s, items_count=%d" % (receipt_uuid, len(items))
            )
        return None

    def read_by_uuid(self, uuid: UUID4) -> t.Optional[ReceiptItem]:
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
            raise ReceiptItemReadError("select item err: %s" % e)

        return ReceiptItem(
            uuid=row[0],
            product=row[1],
            quantity=row[2],
            price=row[3],
            created_at=row[4]
        )

    def read_many(self, receipt_uuid: UUID4, limit: int = 100, offset: int = 0) -> t.List[ReceiptItem]:
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
                        ReceiptItem(
                            uuid=row[0],
                            product=row[1],
                            quantity=row[2],
                            price=row[3],
                            created_at=row[4],
                            split_by=[],
                        )
                    )
        except psycopg.errors.DatabaseError as e:
            raise ReceiptItemReadError("select items err: %s" % e)

        return items
