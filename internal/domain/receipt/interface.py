import typing as t
from abc import ABC, abstractmethod

from internal.domain.image import Image
from internal.domain.receipt.error import ReceiptRecognizeError
from internal.domain.receipt.model import Receipt, UUID4



class Creator(ABC):
    @abstractmethod
    def create(self, receipt: Receipt):
        raise NotImplementedError("method `.create()` must be implemented")


class Updater(ABC):
    @abstractmethod
    def update(self, receipt: Receipt):
        raise NotImplementedError("method `.update()` must be implemented")


class Reader(ABC):
    @abstractmethod
    def read_by_uuid(self, uuid: UUID4) -> Receipt:
        raise NotImplementedError("method `.read_by_uuid()` must be implemented")

    @abstractmethod
    def read_list(self, limit: int, offset: int) -> t.List[Receipt]:
        raise NotImplementedError("method `.read_list()` must be implemented")


class Recognizer(ABC):
    @abstractmethod
    def recognize(self, image: Image) -> t.Tuple[Receipt, t.Optional[ReceiptRecognizeError]]:
        raise NotImplementedError("method `.recognize()` must be implemented")
