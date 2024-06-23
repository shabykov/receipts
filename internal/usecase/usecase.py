import typing as t
from abc import ABC, abstractmethod

from pydantic import UUID4

from internal.domain.image import Image
from internal.domain.receipt import (
    Receipt,
    ReceiptRecognizeError,
    ReceiptUpdateError,
    ReceiptReadError,
)


class ReceiptRecognizer(ABC):
    @abstractmethod
    def recognize(self, user_id: int, image: Image) -> t.Tuple[Receipt, t.Optional[ReceiptRecognizeError]]:
        raise NotImplementedError("method `.recognize()` must be implemented")


class ReceiptUpdater(ABC):
    @abstractmethod
    def update(self, receipt: Receipt) -> t.Optional[ReceiptUpdateError]:
        raise NotImplementedError("method `.update()` must be implemented")


class ReceiptReader(ABC):
    @abstractmethod
    def read(self, receipt_uuid: UUID4) -> t.Tuple[t.Optional[Receipt], t.Optional[ReceiptReadError]]:
        raise NotImplementedError("method `.read()` must be implemented")

    @abstractmethod
    def read_many(self, user_id: int, limit: int, offset: int) -> t.Tuple[t.List[Receipt], t.Optional[ReceiptReadError]]:
        raise NotImplementedError("method `.read_many()` must be implemented")
