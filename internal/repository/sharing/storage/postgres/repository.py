import psycopg

from internal.domain.sharing import ICreator, Sharing


class Repository(ICreator):
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn

    def create(self, sharing: Sharing) -> Sharing:
        return sharing
