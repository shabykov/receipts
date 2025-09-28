import typing as t

import psycopg

from internal.domain.user import User, UserCreateError, UserReadError
from internal.domain.user.id import UserId
from internal.domain.user.username import Username
from internal.usecase.ports.user import IReader, ICreator

CREATE_SCHEMA_SQL = b"""
    CREATE TABLE IF NOT EXISTS tbl_user (
        user_id  integer PRIMARY KEY,
        username varchar(300) UNIQUE,
        created_at timestamp without time zone
    );
"""

INSERT_SQL = b"""
    INSERT INTO tbl_user (
        user_id, 
        username,
        created_at
    )
    VALUES (
        %(user_id)s, 
        %(username)s, 
        %(created_at)s
    ) ON CONFLICT (user_id) DO NOTHING;
"""

SELECT_BY_USER_ID_SQL = b"""
    SELECT
        user_id, 
        username,
        created_at
    FROM tbl_user 
    WHERE user_id = %(user_id)s;
"""

SELECT_BY_USERNAME_SQL = b"""
    SELECT
        user_id, 
        username,
        created_at
    FROM tbl_user 
    WHERE user_id = %(user_id)s;
"""


class Repository(IReader, ICreator):

    def __init__(self, conn: psycopg.Connection):
        self._conn = conn
        self.init_schema()

    def init_schema(self):
        with self._conn.cursor() as cur:
            cur.execute(query=CREATE_SCHEMA_SQL)
        self._conn.commit()

    def read_by_id(self, user_id: UserId) -> t.Optional[User]:
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    SELECT_BY_USER_ID_SQL,
                    params={
                        "user_id": user_id.string()
                    }
                )
                row = cur.fetchone()
        except psycopg.errors.DatabaseError as e:
            raise UserReadError("select user err: %s" % e)

        if row is None:
            return

        ret = User(
            user_id=row[0],
            username=row[1],
            created_at=row[2]
        )
        return ret

    def read_by_username(self, username: Username) -> t.Optional[User]:
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    SELECT_BY_USERNAME_SQL,
                    params={
                        "username": username.string()
                    }
                )
                row = cur.fetchone()
        except psycopg.errors.DatabaseError as e:
            raise UserReadError("select user err: %s" % e)

        if row is None:
            return

        ret = User(
            user_id=row[0],
            username=row[1],
            created_at=row[2]
        )
        return ret

    def create(self, user: User) -> User:

        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    query=INSERT_SQL,
                    params={
                        'user_id': user.user_id.int(),
                        'username': user.username.string(),
                        'created_at': user.created_at
                    }
                )

        except psycopg.errors.DatabaseError as e:

            self._conn.rollback()

            raise UserCreateError("insert user err: %s" % e)

        else:
            self._conn.commit()

        return user
