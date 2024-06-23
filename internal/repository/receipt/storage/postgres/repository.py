import typing as t
from logging import getLogger

import psycopg
from pydantic import UUID4

from internal.domain.receipt import (
    Receipt,
    Creator,
    Updater,
    Reader,
    ReceiptReadError,
    ReceiptCreateError,
    ReceiptUpdateError,
)
from internal.repository.receipt_item.storage.postgres.repository import (
    Repository as ItemRepository
)

logger = getLogger("receipt.storge.postgres")

CREATE_SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS tbl_receipt (
        user_id    integer NOT NULL,
        uuid       varchar(255) PRIMARY KEY,
        store_name varchar(300),
        store_addr varchar(300),
        date       varchar(100),
        time       varchar(100),
        subtotal   double precision,
        tips       double precision,
        total      double precision,
        created_at timestamp without time zone
    );
"""

CLEAN_SCHEMA_SQL = """
    truncate table tbl_receipt;
"""

INSERT_RECEIPT_SQL = """
    INSERT INTO tbl_receipt (
        user_id, 
        uuid,
        store_name, 
        store_addr, 
        date, 
        time, 
        subtotal, 
        tips, 
        total, 
        created_at
    )
    VALUES (
        %(user_id)s, 
        %(uuid)s, 
        %(store_name)s, 
        %(store_addr)s,
        %(date)s,
        %(time)s,
        %(subtotal)s,
        %(tips)s,
        %(total)s,
        %(created_at)s
    ) ON CONFLICT (uuid) DO NOTHING;
"""

UPSERT_RECEIPT_SQL = """
    INSERT INTO tbl_receipt (
        user_id, 
        uuid,
        store_name, 
        store_addr, 
        date, 
        time, 
        subtotal, 
        tips, 
        total
    )
    VALUES (
        %(user_id)s, 
        %(uuid)s, 
        %(store_name)s, 
        %(store_addr)s,
        %(date)s,
        %(time)s,
        %(subtotal)s,
        %(tips)s,
        %(total)s
    )
    ON CONFLICT(uuid)
    DO UPDATE SET
        store_name = EXCLUDED.store_name, 
        store_addr = EXCLUDED.store_addr,
        date = EXCLUDED.date,
        time = EXCLUDED.time,
        subtotal = EXCLUDED.subtotal,
        tips = EXCLUDED.tips,
        total = EXCLUDED.total;
"""

SELECT_RECEIPT_SQL = """
    SELECT
        user_id, 
        uuid,
        store_name, 
        store_addr, 
        date, 
        time, 
        subtotal, 
        tips, 
        total, 
        created_at
    FROM tbl_receipt 
    WHERE uuid = %(uuid)s;
"""


class Repository(Creator, Updater, Reader):
    def __init__(self, conn: psycopg.Connection, item_repo: ItemRepository):
        self._conn = conn
        self._item_repo = item_repo

    def init_schema(self):
        with self._conn.cursor() as cur:
            cur.execute(query=CREATE_SCHEMA_SQL)
        self._conn.commit()
        logger.info("receipt schema is ready")

    def clean(self):
        with self._conn.cursor() as cur:
            cur.execute(query=CLEAN_SCHEMA_SQL)
        self._conn.commit()
        logger.info("receipt schema cleaned")

    def create(self, receipt: Receipt) -> t.Optional[ReceiptCreateError]:
        err = self._item_repo.create_many(receipt.uuid, receipt.items)
        if err is not None:
            return ReceiptCreateError(
                message="receipt items create err: %s" % err,
                code="item_creator_error"
            )

        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    query=INSERT_RECEIPT_SQL,
                    params={
                        'user_id': receipt.user_id,
                        'uuid': receipt.uuid,
                        'store_name': receipt.store_name,
                        'store_addr': receipt.store_addr,
                        'date': receipt.date,
                        'time': receipt.time,
                        'subtotal': receipt.subtotal,
                        'tips': receipt.tips,
                        'total': receipt.total,
                        'created_at': receipt.created_at
                    }
                )

        except psycopg.errors.DatabaseError as e:

            self._conn.rollback()

            return ReceiptCreateError(
                message="insert receipt err: %s" % e,
                code="database_error"
            )

        else:
            self._conn.commit()
            logger.info("receipt created: receipt_uuid=%s" % receipt.uuid)

        return None

    def update(self, receipt: Receipt) -> t.Optional[ReceiptUpdateError]:
        err = self._item_repo.update_many(receipt.uuid, receipt.items)
        if err is not None:
            return ReceiptUpdateError(
                message="receipt items update err: %s" % err,
                code="item_creator_error"
            )

        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    query=UPSERT_RECEIPT_SQL,
                    params={
                        'user_id': receipt.user_id,
                        'uuid': receipt.uuid,
                        'store_name': receipt.store_name,
                        'store_addr': receipt.store_addr,
                        'date': receipt.date,
                        'time': receipt.time,
                        'subtotal': receipt.subtotal,
                        'tips': receipt.tips,
                        'total': receipt.total
                    }
                )
        except psycopg.errors.DatabaseError as e:

            self._conn.rollback()

            return ReceiptUpdateError(
                message="insert receipt err: %s" % e,
                code="database_error"
            )

        else:
            self._conn.commit()
            logger.info("receipt updated: receipt_uuid=%s" % receipt.uuid)

        return None

    def read_by_uuid(self, uuid: UUID4) -> t.Tuple[t.Optional[Receipt], t.Optional[ReceiptReadError]]:
        items, err = self._item_repo.read_many(uuid, 100, 0)
        if err is not None:
            return None, ReceiptReadError(
                message="read receipt items err: %s" % err,
                code="database_error"
            )

        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    SELECT_RECEIPT_SQL,
                    params={
                        "uuid": str(uuid)
                    }
                )

                row = cur.fetchone()
        except psycopg.errors.DatabaseError as e:
            return None, ReceiptReadError(
                message="select receipt err: %s" % e,
                code="database_error"
            )

        ret = Receipt(
            user_id=row[0],
            uuid=row[1],
            store_name=row[2],
            store_addr=row[3],
            date=row[4],
            time=row[5],
            subtotal=row[6],
            tips=row[7],
            total=row[8],
            created_at=row[9]
        )
        ret.items = items
        return ret, None

    def read_many(self, user_id: int, limit: int, offset: int) -> t.Tuple[t.List[Receipt], t.Optional[ReceiptReadError]]:
        pass
