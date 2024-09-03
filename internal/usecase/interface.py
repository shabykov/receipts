import typing as t
from abc import ABC, abstractmethod

from pydantic import UUID4

from internal.domain.image import Image
from internal.domain.receipt import Receipt
from internal.domain.user import User


class IReceiptRecognize(ABC):
    @abstractmethod
    def recognize(self, user_id: int, image: Image) -> Receipt:
        raise NotImplementedError("method `.recognize()` must be implemented")


class IReceiptRead(ABC):
    @abstractmethod
    def read(self, receipt_uuid: UUID4) -> t.Optional[Receipt]:
        # public read interface
        raise NotImplementedError("method `.read()` must be implemented")

    @abstractmethod
    def read_many(self, user_id: int, limit: int, offset: int) -> t.List[Receipt]:
        raise NotImplementedError("method `.read_many()` must be implemented")


class IReceiptShare(ABC):
    @abstractmethod
    def share(self, receipt: Receipt, with_user: User):
        # public share interface
        raise NotImplementedError("method `.share()` must be implemented")
