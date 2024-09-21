import typing as t
from internal.domain.user import (
    User,
    IReader,
    ICreator,
    new_user_by_username,
)
from internal.usecase.interface import IUserReadUC


class UserReadUseCase(IUserReadUC):
    def __init__(self, reader: IReader, creator: ICreator):
        self._reader = reader
        self._creator = creator

    def get_by_id(self, user_id: int) -> t.Optional[User]:
        return self._reader.read_by_id(user_id)

    def get_by_username(self, username: str) -> User:
        user = self._reader.read_by_username(username)
        if user is not None:
            return user

        return self._creator.create(
            new_user_by_username(username)
        )

    def get_or_create(self, user: User) -> User:
        exist = self._reader.read_by_id(user.user_id)
        if exist:
            return exist

        return self._creator.create(user)
