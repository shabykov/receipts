import typing as t
from abc import ABC, abstractmethod

from internal.domain.user._model import User


class ICreator(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        raise NotImplementedError("method `.create()` must be implemented")


class IReader(ABC):
    @abstractmethod
    def read_by_username(self, username: str) -> t.Optional[User]:
        raise NotImplementedError("method `.read_by_username()` must be implemented")
