import typing as t
from abc import ABC, abstractmethod

from pydantic import UUID4
from internal.domain.image import Image
from internal.domain.receipt import Receipt


class ICreator(ABC):
    @abstractmethod
    def create(self, receipt: Receipt):
        raise NotImplementedError("method `.create()` must be implemented")


class IUpdater(ABC):
    @abstractmethod
    def update(self, receipt: Receipt):
        raise NotImplementedError("method `.update()` must be implemented")


class IReader(ABC):
    @abstractmethod
    def read_by_uuid(self, uuid: UUID4) -> t.Optional[Receipt]:
        raise NotImplementedError("method `.read_by_uuid()` must be implemented")

    @abstractmethod
    def read_many(self, user_id: int, limit: int, offset: int) -> t.List[Receipt]:
        raise NotImplementedError("method `.read_many()` must be implemented")


class IRecognizer(ABC):
    @abstractmethod
    def recognize(self, image: Image) -> Receipt:
        raise NotImplementedError("method `.recognize()` must be implemented")
