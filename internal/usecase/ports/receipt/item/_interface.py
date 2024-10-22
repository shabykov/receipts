import typing as t
from abc import ABC, abstractmethod


from pydantic import UUID4
from internal.domain.receipt.item import ReceiptItem


class ICreator(ABC):
    @abstractmethod
    def create(self, receipt_uuid: str, item: ReceiptItem):
        raise NotImplementedError("method `.create()` must be implemented")

    @abstractmethod
    def create_many(self, receipt_uuid: str, items: t.List[ReceiptItem]):
        raise NotImplementedError("method `.create_many()` must be implemented")


class IUpdater(ABC):
    @abstractmethod
    def update(self, receipt_uuid: UUID4, item: ReceiptItem):
        raise NotImplementedError("method `.update()` must be implemented")

    @abstractmethod
    def update_many(self, receipt_uuid: UUID4, items: t.List[ReceiptItem]):
        raise NotImplementedError("method `.update_many()` must be implemented")


class IReader(ABC):
    @abstractmethod
    def read_by_uuid(self, uuid: UUID4) -> t.Optional[ReceiptItem]:
        raise NotImplementedError("method `.read_by_uuid()` must be implemented")

    @abstractmethod
    def read_many(self, receipt_uuid: UUID4, limit: int, offset: int) -> t.List[ReceiptItem]:
        raise NotImplementedError("method `.read_many()` must be implemented")
