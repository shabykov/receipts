import typing as t
from abc import ABC, abstractmethod

from .model import Item, UUID4


class Creator(ABC):
    @abstractmethod
    def create(self, item: Item):
        raise NotImplementedError("method `.create()` must be implemented")


class Updater(ABC):
    @abstractmethod
    def update(self, item: Item):
        raise NotImplementedError("method `.update()` must be implemented")


class Reader(ABC):
    @abstractmethod
    def read_by_uuid(self, uuid: UUID4) -> Item:
        raise NotImplementedError("method `.read_by_uuid()` must be implemented")

    @abstractmethod
    def read_list(self, limit: int, offset: int) -> t.List[Item]:
        raise NotImplementedError("method `.read_list()` must be implemented")
