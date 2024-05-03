import typing as t
from abc import ABC, abstractmethod

from internal.domain.image import Image
from internal.domain.receipt import Receipt, ReceiptRecognizeError


class ReceiptRecognizer(ABC):
    @abstractmethod
    def recognize(self, image: Image) -> t.Tuple[Receipt, t.Optional[ReceiptRecognizeError]]:
        raise NotImplementedError("method `.recognize()` must be implemented")


class ReceiptUpdater(ABC):
    @abstractmethod
    def update(self, receipt: Receipt) -> Receipt:
        raise NotImplementedError("method `.update()` must be implemented")
