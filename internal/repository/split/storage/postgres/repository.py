import typing as t

import psycopg
from pydantic import UUID4

from internal.domain.receipt import Receipt
from internal.domain.split import ICreator, IReader, Split, SplitCreateError, SplitReadError
from internal.domain.user import User

CREATE_SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS tbl_split (
        user_id  integer,
        receipt_uuid varchar(255),
        receipt_item_uuid varchar(255),
        created_at timestamp without time zone,
        UNIQUE(user_id, receipt_uuid, receipt_item_uuid)
    );
"""

INSERT_SQL = """
    INSERT INTO tbl_split (
        user_id,
        receipt_uuid,
        receipt_item_uuid,
        created_at
    )
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (user_id, receipt_uuid, receipt_item_uuid)
    DO NOTHING;
"""

SELECT_ITEMS_SQL = """
    SELECT
        u.user_id,
        u.username,
        u.created_at,
        r.user_id,
        r.uuid,
        r.store_name,
        r.store_addr,
        r.date,
        r.time,
        r.subtotal,
        r.tips,
        r.total,
        r.created_at,
        s.receipt_item_uuid,
        s.created_at
    FROM tbl_split as s
    JOIN tbl_user as u ON (u.user_id = s.user_id)
    JOIN tbl_receipt as r ON (r.uuid = s.receipt_uuid)
    WHERE s.receipt_uuid=%(receipt_uuid)s;
"""


class Repository(ICreator, IReader):
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn
        self.init_schema()

    def init_schema(self):
        with self._conn.cursor() as cur:
            cur.execute(query=CREATE_SCHEMA_SQL)
        self._conn.commit()

    def read_many(self, receipt_uuid: UUID4) -> t.List[Split]:
        items = []
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    SELECT_ITEMS_SQL,
                    params={
                        "receipt_uuid": str(receipt_uuid),
                    }
                )

                for row in cur:
                    items.append(
                        Split(
                            user=User(
                                user_id=row[0],
                                username=row[1],
                                created_at=row[2],
                            ),
                            receipt=Receipt(
                                user_id=row[3],
                                uuid=row[4],
                                store_name=row[5],
                                store_addr=row[6],
                                date=row[7],
                                time=row[8],
                                subtotal=row[9],
                                tips=row[10],
                                total=row[11],
                                created_at=row[12],
                                items=[],
                            ),
                            receipt_item_id=row[13],
                            created_at=row[14],
                        )
                    )
        except psycopg.errors.DatabaseError as e:
            raise SplitReadError("select items err: %s" % e)

        return items

    def create(self, splits: t.List[Split]) -> t.List[Split]:
        try:
            with self._conn.cursor() as cur:
                cur.executemany(
                    query=INSERT_SQL,
                    params_seq=[
                        (
                            split.user.user_id,
                            split.receipt.uuid,
                            split.receipt_item_id,
                            split.created_at
                        ) for split in splits
                    ]
                )
        except psycopg.errors.DatabaseError as e:
            self._conn.rollback()
            raise SplitCreateError("insert items err: %s" % e)
        else:
            self._conn.commit()

        return splits
