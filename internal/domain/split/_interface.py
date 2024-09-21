import typing as t
from abc import ABC, abstractmethod

from pydantic import UUID4

from internal.domain.split._model import Split


class IReader(ABC):
    @abstractmethod
    def read_many(self, receipt_id: UUID4) -> t.List[Split]:
        raise NotImplementedError("method `.read_many()` must be implemented")


class ICreator(ABC):
    @abstractmethod
    def create(self, splits: t.List[Split]):
        raise NotImplementedError("method `.create()` must be implemented")
