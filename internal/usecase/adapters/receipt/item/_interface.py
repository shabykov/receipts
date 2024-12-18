import typing as t
from abc import ABC, abstractmethod


from internal.domain.receipt.uuid import ReceiptUUID
from internal.domain.receipt.item import ReceiptItem


class ICreator(ABC):
    @abstractmethod
    def create_many(self, receipt_uuid: str, items: t.List[ReceiptItem]):
        raise NotImplementedError("method `.create_many()` must be implemented")


class IUpdater(ABC):
    @abstractmethod
    def update_many(self, receipt_uuid: ReceiptUUID, items: t.List[ReceiptItem]):
        raise NotImplementedError("method `.update_many()` must be implemented")


class IReader(ABC):
    @abstractmethod
    def read_by_receipt_uuid(self, receipt_uuid: ReceiptUUID) -> t.List[ReceiptItem]:
        raise NotImplementedError("method `.read_many()` must be implemented")
