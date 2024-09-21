import typing as t
from collections import defaultdict

from internal.domain.user import ICreator, IReader, User


class Repository(ICreator, IReader):
    def __init__(self):
        self._data_by_id = defaultdict(User)
        self._data_by_username = defaultdict(User)

    def create(self, user: User) -> User:
        self._data_by_id[user.user_id] = user
        self._data_by_username[user.username] = user
        return user

    def read_by_id(self, user_id: int) -> t.Optional[User]:
        return self._data_by_id.get(user_id)

    def read_by_username(self, username: str) -> t.Optional[User]:
        return self._data_by_username.get(username)
