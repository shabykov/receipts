import typing as t
from logging import getLogger

import psycopg
from pydantic import UUID4

from internal.domain.receipt.item import ReceiptItem, Split
from internal.domain.receipt.item import (
    ReceiptItemCreateError,
    ReceiptItemUpdateError,
    ReceiptItemReadError,
)
from internal.usecase.adapters.receipt.item import (
    ICreator,
    IUpdater,
    IReader,
)
from internal.usecase.adapters.receipt.item.split import (
    IUpdater as ISplitUpdater
)

logger = getLogger("receipt_item.storage.postgres")

CREATE_RECEIPT_ITEM_SQL = b"""
    CREATE TABLE IF NOT EXISTS tbl_receipt_item (
        receipt_uuid   text NOT NULL,
        uuid           varchar(255) PRIMARY KEY,
        product        text,
        quantity       integer,
        price          numeric(6),
        created_at     timestamp without time zone,
        UNIQUE(receipt_uuid, product)
    );
"""

CLEAN_RECEIPT_ITEM_SQL = b"""
    truncate table tbl_receipt_item;
"""

INSERT_RECEIPT_ITEM_SQL = b"""
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

UPSERT_RECEIPT_ITEM_SQL = b"""
    INSERT INTO tbl_receipt_item (
        receipt_uuid,
        uuid,
        product,
        quantity,
        price
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT(uuid)
    DO UPDATE SET
        product = EXCLUDED.product, 
        quantity = EXCLUDED.quantity,
        price = EXCLUDED.price;
"""

SELECT_RECEIPT_ITEM_SQL = b"""
    SELECT
        uuid, 
        product, 
        quantity, 
        price,
        created_at
    FROM tbl_receipt_item 
    WHERE uuid = %(uuid)s;
"""

SELECT_RECEIPT_ITEMS_SQL = b"""
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

CREATE_RECEIPT_ITEM_SPLIT_SQL = b"""
    CREATE TABLE IF NOT EXISTS tbl_receipt_item_split (
        uuid           varchar(255) PRIMARY KEY,
        username       text,
        quantity       integer,
        UNIQUE(uuid, username)
    );
"""

CLEAN_RECEIPT_ITEM_SPLIT_SQL = b"""
    truncate table tbl_receipt_item_split;
"""

UPSERT_RECEIPT_ITEM_SPLIT_SQL = b"""
    INSERT INTO tbl_receipt_item_split (
        uuid,
        username,
        quantity
    )
    VALUES (%s, %s, %s)
    ON CONFLICT(uuid, username)
    DO UPDATE SET
        quantity = EXCLUDED.quantity;
"""

SELECT_RECEIPT_ITEM_SPLIT_SQL = b"""
    SELECT
        uuid, 
        username,
        quantity
    FROM tbl_receipt_item_split 
    WHERE receipt_uuid=%(receipt_uuid)s
    ORDER BY created_at
    LIMIT %(limit)s
    OFFSET %(offset)s;
"""


class Repository(ICreator, IUpdater, IReader, ISplitUpdater):
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn
        self.init_schema()

    def init_schema(self):
        with self._conn.cursor() as cur:
            cur.execute(query=CREATE_RECEIPT_ITEM_SQL)
            cur.execute(query=CREATE_RECEIPT_ITEM_SPLIT_SQL)
        self._conn.commit()
        logger.info("receipt item schema is ready")

    def clean(self):
        with self._conn.cursor() as cur:
            cur.execute(query=CLEAN_RECEIPT_ITEM_SQL)
            cur.execute(query=CLEAN_RECEIPT_ITEM_SPLIT_SQL)
        self._conn.commit()
        logger.info("receipt item schema cleaned")

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
                            item.price,
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
                        )
                    )
        except psycopg.errors.DatabaseError as e:
            raise ReceiptItemReadError("select items err: %s" % e)

        return items

    def upsert_splits(self, items: t.List[Split]):
        try:
            with self._conn.cursor() as cur:
                cur.executemany(
                    query=UPSERT_RECEIPT_ITEM_SPLIT_SQL,
                    params_seq=[
                        (
                            item.uuid,
                            item.username,
                            item.quantity
                        ) for item in items
                    ]
                )
        except psycopg.errors.DatabaseError as e:
            self._conn.rollback()
            raise ReceiptItemUpdateError("upsert items splits err: %s" % e)
        else:
            self._conn.commit()
            logger.info(
                "receipt items split updated: items_count=%d" % len(items)
            )

        return None
