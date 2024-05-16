import typing as t
from abc import ABC, abstractmethod

from internal.domain.image import Image
from internal.domain.receipt.error import (
    ReceiptRecognizeError,
    ReceiptCreateError,
    ReceiptUpdateError,
    ReceiptReadError,
)
from internal.domain.receipt.model import Receipt, UUID4


class Creator(ABC):
    @abstractmethod
    def create(self, receipt: Receipt) -> t.Optional[ReceiptCreateError]:
        raise NotImplementedError("method `.create()` must be implemented")


class Updater(ABC):
    @abstractmethod
    def update(self, receipt: Receipt) -> t.Optional[ReceiptUpdateError]:
        raise NotImplementedError("method `.update()` must be implemented")


class Reader(ABC):
    @abstractmethod
    def read_by_uuid(self, uuid: UUID4) -> t.Tuple[t.Optional[Receipt], t.Optional[ReceiptReadError]]:
        raise NotImplementedError("method `.read_by_uuid()` must be implemented")

    @abstractmethod
    def read_many(self, limit: int, offset: int) -> t.Tuple[t.List[Receipt], t.Optional[ReceiptReadError]]:
        raise NotImplementedError("method `.read_many()` must be implemented")


class Recognizer(ABC):
    @abstractmethod
    def recognize(self, image: Image) -> t.Tuple[Receipt, t.Optional[ReceiptRecognizeError]]:
        raise NotImplementedError("method `.recognize()` must be implemented")
