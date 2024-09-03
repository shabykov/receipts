import typing as t

import psycopg

from internal.domain.user import ICreator, IReader, User


class Repository(ICreator, IReader):
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn

    def create(self, user: User) -> User:
        return user

    def read_by_username(self, username: str) -> t.Optional[User]:
        return User(username=username)
