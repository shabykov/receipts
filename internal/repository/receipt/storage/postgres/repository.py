import typing as t
from logging import getLogger

import psycopg
from pydantic import UUID4

from internal.domain.receipt import (
    Receipt,
    ReceiptReadError,
    ReceiptCreateError,
    ReceiptUpdateError,
)
from internal.domain.receipt.item import (
    ReceiptItemCreateError,
    ReceiptItemReadError,
    ReceiptItemUpdateError,
)
from internal.repository.receipt_item.storage.postgres.repository import (
    Repository as ItemRepository
)
from internal.usecase.adapters.receipt import (
    ICreator,
    IUpdater,
    IReader,
)

logger = getLogger("receipt.storge.postgres")

CREATE_SCHEMA_SQL = b"""
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

CLEAN_SCHEMA_SQL = b"""
    truncate table tbl_receipt;
"""

INSERT_RECEIPT_SQL = b"""
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

UPSERT_RECEIPT_SQL = b"""
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

SELECT_RECEIPT_SQL = b"""
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


class Repository(ICreator, IUpdater, IReader):
    def __init__(self, conn: psycopg.Connection, item_repo: ItemRepository):
        self._conn = conn
        self._item_repo = item_repo
        self.init_schema()

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

    def create(self, receipt: Receipt):
        try:
            self._item_repo.create_many(receipt.uuid, receipt.items)
        except ReceiptItemCreateError as err:
            raise ReceiptCreateError("receipt items create err: %s" % err)

        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    query=INSERT_RECEIPT_SQL,
                    params={
                        'user_id': receipt.user_id.int(),
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

            raise ReceiptCreateError("insert receipt err: %s" % e)

        else:
            self._conn.commit()
            logger.info("receipt created: receipt_uuid=%s" % receipt.uuid)

        return None

    def update(self, receipt: Receipt):
        try:
            self._item_repo.update_many(receipt.uuid, receipt.items)
        except ReceiptItemUpdateError as err:
            raise ReceiptUpdateError("receipt items update err: %s" % err)

        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    query=UPSERT_RECEIPT_SQL,
                    params={
                        'user_id': receipt.user_id.int(),
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

            raise ReceiptUpdateError("insert receipt err: %s" % e)

        else:
            self._conn.commit()
            logger.info("receipt updated: receipt_uuid=%s" % receipt.uuid)

        return None

    def read_by_uuid(self, uuid: UUID4) -> t.Optional[Receipt]:
        try:
            items = self._item_repo.read_by_receipt_uuid(uuid)
        except ReceiptItemReadError as err:
            raise ReceiptReadError("read receipt items err: %s" % err)

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
            raise ReceiptReadError("select receipt err: %s" % e)

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
        return ret

    def read_many(self, user_id: int, limit: int, offset: int) -> t.List[Receipt]:
        return []
