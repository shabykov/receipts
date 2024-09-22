# Here are public interfaces which
# are used as entrypoints of the application
import typing as t
from abc import ABC, abstractmethod

from pydantic import UUID4

from internal.domain.image import Image
from internal.domain.receipt import Receipt
from internal.domain.split import Splits
from internal.domain.user import User


class IReceiptRecognizeUC(ABC):
    @abstractmethod
    def recognize(self, user_id: int, image: Image) -> Receipt:
        raise NotImplementedError("method `.recognize()` must be implemented")


class IReceiptReadUC(ABC):
    @abstractmethod
    def read(self, receipt_uuid: UUID4) -> t.Optional[Receipt]:
        # public read interface
        raise NotImplementedError("method `.read()` must be implemented")

    @abstractmethod
    def read_many(self, user_id: int, limit: int, offset: int) -> t.List[Receipt]:
        raise NotImplementedError("method `.read_many()` must be implemented")


class IReceiptSplitUC(ABC):
    @abstractmethod
    def get(self, receipt_uuid: UUID4) -> t.Optional[Splits]:
        # public get interface
        raise NotImplementedError("method `.get()` must be implemented")

    @abstractmethod
    def create(self, user: User, receipt: Receipt, items: t.List[str]) -> Splits:
        # public split interface
        raise NotImplementedError("method `.create()` must be implemented")


class IUserReadUC(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> t.Optional[User]:
        raise NotImplementedError("method `.get_by_id()` must be implemented")

    @abstractmethod
    def get_by_username(self, username: str) -> User:
        raise NotImplementedError("method `.get_by_username()` must be implemented")

    @abstractmethod
    def get_or_create(self, user: User) -> User:
        raise NotImplementedError("method `.get_or_create()` must be implemented")
