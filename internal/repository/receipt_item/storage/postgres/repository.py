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
from internal.usecase.ports.receipt.item import (
    ICreator,
    IUpdater,
    IReader,
)

logger = getLogger("receipt_item.storage.postgres")

CREATE_RECEIPT_ITEM_SQL = b"""
    CREATE TABLE IF NOT EXISTS tbl_receipt_item (
        receipt_uuid        text NOT NULL,
        uuid                varchar(255) PRIMARY KEY,
        product             text,
        quantity            integer,
        price               numeric(6),
        split_error_message text,
        created_at          timestamp without time zone,
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
        created_at,
        split_error_message
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s) 
    ON CONFLICT (receipt_uuid, product) 
    DO NOTHING;
"""

UPSERT_RECEIPT_ITEM_SQL = b"""
    INSERT INTO tbl_receipt_item (
        receipt_uuid,
        uuid,
        product,
        quantity,
        price,
        split_error_message
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT(uuid)
    DO UPDATE SET
        product = EXCLUDED.product, 
        quantity = EXCLUDED.quantity,
        split_error_message = EXCLUDED.split_error_message,
        price = EXCLUDED.price;
"""

SELECT_RECEIPT_ITEM_SQL = b"""
    SELECT
        i.uuid, 
        i.product, 
        i.quantity, 
        i.price, 
        i.created_at, 
        i.split_error_message,
        json_agg(json_build_object('username', s.username, 'quantity', s.quantity))
    FROM tbl_receipt_item as i
    LEFT JOIN tbl_receipt_item_split as s
    ON (i.uuid = s.uuid)
    WHERE i.uuid = %(uuid)s
    GROUP BY i.uuid;
"""

SELECT_RECEIPT_ITEMS_SQL = b"""
    SELECT
        i.uuid, 
        i.product, 
        i.quantity, 
        i.price, 
        i.created_at,
        i.split_error_message,
        json_agg(json_build_object('username', s.username, 'quantity', s.quantity))
    FROM tbl_receipt_item as i
    LEFT JOIN tbl_receipt_item_split as s
    ON (i.uuid = s.uuid)
    WHERE i.receipt_uuid=%(receipt_uuid)s
    GROUP BY i.uuid;
"""

CREATE_RECEIPT_ITEM_SPLIT_SQL = b"""
    CREATE TABLE IF NOT EXISTS tbl_receipt_item_split (
        uuid           varchar(255),
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


class Repository(ICreator, IUpdater, IReader):
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

    def create_many(self, receipt_uuid: UUID4, receipt_items: t.List[ReceiptItem]):
        try:
            with self._conn.cursor() as cur:
                cur.executemany(
                    query=UPSERT_RECEIPT_ITEM_SPLIT_SQL,
                    params_seq=[
                        (
                            receipt_item.uuid,
                            split.username,
                            split.quantity
                        ) for receipt_item in receipt_items for split in receipt_item.splits
                    ]
                )
                cur.executemany(
                    query=INSERT_RECEIPT_ITEM_SQL,
                    params_seq=[
                        (
                            receipt_uuid,
                            item.uuid,
                            item.product,
                            item.quantity,
                            item.price,
                            item.created_at,
                            item.split_error_message
                        ) for item in receipt_items
                    ]
                )
        except psycopg.errors.DatabaseError as e:
            self._conn.rollback()
            raise ReceiptItemCreateError("insert receipt_items err: %s" % e)
        else:
            self._conn.commit()
            logger.info(
                "receipt receipt_items created: receipt_uuid=%s, items_count=%d" % (receipt_uuid, len(receipt_items))
            )
        return None

    def update_many(self, receipt_uuid: UUID4, receipt_items: t.List[ReceiptItem]):
        try:
            with self._conn.cursor() as cur:
                cur.executemany(
                    query=UPSERT_RECEIPT_ITEM_SPLIT_SQL,
                    params_seq=[
                        (
                            receipt_item.uuid,
                            split.username,
                            split.quantity
                        ) for receipt_item in receipt_items for split in receipt_item.splits
                    ]
                )
                cur.executemany(
                    query=UPSERT_RECEIPT_ITEM_SQL,
                    params_seq=[
                        (
                            receipt_uuid,
                            item.uuid,
                            item.product,
                            item.quantity,
                            item.price,
                            item.split_error_message
                        ) for item in receipt_items
                    ]
                )
        except psycopg.errors.DatabaseError as e:
            self._conn.rollback()
            raise ReceiptItemUpdateError("upsert receipt_items err: %s" % e)
        else:
            self._conn.commit()
            logger.info(
                "receipt receipt_items updated: receipt_uuid=%s, items_count=%d" % (receipt_uuid, len(receipt_items))
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
            created_at=row[4],
            split_error_message=row[5] if row[5] else "",
            splits=parse_splits(row[6])
        )

    def read_by_receipt_uuid(self, receipt_uuid: UUID4) -> t.List[ReceiptItem]:
        receipt_items = []
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    SELECT_RECEIPT_ITEMS_SQL,
                    params={
                        "receipt_uuid": str(receipt_uuid),
                    }
                )
                for row in cur:
                    receipt_items.append(
                        ReceiptItem(
                            uuid=row[0],
                            product=row[1],
                            quantity=row[2],
                            price=row[3],
                            created_at=row[4],
                            split_error_message=row[5] if row[5] else "",
                            splits=parse_splits(row[6])
                        )
                    )
        except psycopg.errors.DatabaseError as e:
            raise ReceiptItemReadError("select receipt_items err: %s" % e)

        return receipt_items


def parse_splits(data) -> t.Set[Split]:
    ret = set()
    for ob in data:
        if ob and ob.get("username") and ob.get('quantity'):
            ret.add(
                Split(username=ob['username'], quantity=ob['quantity'])
            )

    return ret
