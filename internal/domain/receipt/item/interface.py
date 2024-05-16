import typing as t
from abc import ABC, abstractmethod

from .error import ReceiptItemCreateError, ReceiptItemUpdateError, ReceiptItemReadError
from .model import Item, UUID4


class Creator(ABC):
    @abstractmethod
    def create(self, receipt_uuid: str, item: Item) -> t.Optional[ReceiptItemCreateError]:
        raise NotImplementedError("method `.create()` must be implemented")

    @abstractmethod
    def create_many(self, receipt_uuid: str, items: t.List[Item]) -> t.Optional[ReceiptItemCreateError]:
        raise NotImplementedError("method `.create_many()` must be implemented")


class Updater(ABC):
    @abstractmethod
    def update(self, receipt_uuid: UUID4, item: Item) -> t.Optional[ReceiptItemUpdateError]:
        raise NotImplementedError("method `.update()` must be implemented")

    @abstractmethod
    def update_many(self, receipt_uuid: UUID4, items: t.List[Item]) -> t.Optional[ReceiptItemUpdateError]:
        raise NotImplementedError("method `.update_many()` must be implemented")


class Reader(ABC):
    @abstractmethod
    def read_by_uuid(self, uuid: UUID4) -> t.Tuple[
        t.Optional[Item], t.Optional[ReceiptItemReadError]
    ]:
        raise NotImplementedError("method `.read_by_uuid()` must be implemented")

    @abstractmethod
    def read_many(self, receipt_uuid: UUID4, limit: int, offset: int) -> t.Tuple[
        t.List[Item], t.Optional[ReceiptItemReadError]
    ]:
        raise NotImplementedError("method `.read_many()` must be implemented")
