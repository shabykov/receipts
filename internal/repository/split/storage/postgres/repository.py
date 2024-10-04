import typing as t

import psycopg
from pydantic import UUID4

from internal.domain.receipt import Receipt
from internal.domain.receipt.split import ICreator, IReader, Split, SplitCreateError, SplitReadError
from internal.domain.user import User

CREATE_SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS tbl_split (
        username  varchar(255),
        receipt_uuid varchar(255),
        receipt_item_uuid varchar(255),
        created_at timestamp without time zone,
        UNIQUE(username, receipt_uuid, receipt_item_uuid)
    );
"""

INSERT_SQL = """
    INSERT INTO tbl_split (
        username,
        receipt_uuid,
        receipt_item_uuid,
        created_at
    )
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (username, receipt_uuid, receipt_item_uuid)
    DO NOTHING;
"""

SELECT_ITEMS_SQL = """
    SELECT
        username,
        receipt_uuid,
        receipt_item_uuid,
        created_at
    FROM tbl_split
    WHERE receipt_uuid=%(receipt_uuid)s;
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
                            username=row[0],
                            receipt_uuid=row[1],
                            receipt_item_id=row[2],
                            created_at=row[3],
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
                            split.username,
                            split.receipt_uuid,
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
