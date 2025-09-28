import typing as t

from internal.domain.user import User
from internal.domain.user.id import UserId
from internal.usecase.ports.user import IReader, ICreator
from internal.usecase.interface import IUserReadUC


class UserReadUseCase(IUserReadUC):
    def __init__(self, reader: IReader, creator: ICreator):
        self._reader = reader
        self._creator = creator

    def get_by_id(self, user_id: UserId) -> t.Optional[User]:
        return self._reader.read_by_id(user_id)

    def get_or_create(self, user: User) -> User:
        exist = self._reader.read_by_id(user.user_id)
        if exist:
            return exist

        return self._creator.create(user)
