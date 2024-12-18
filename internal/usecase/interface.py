# Here are public interfaces which
# are used as entrypoints of the application
import typing as t
from abc import ABC, abstractmethod

from internal.domain.user.id import UserId
from internal.domain.image import Image
from internal.domain.receipt import Receipt
from internal.domain.receipt.uuid import ReceiptUUID
from internal.domain.receipt.item import Choice
from internal.domain.user import User


class IReceiptRecognizeUC(ABC):
    @abstractmethod
    def recognize(self, user_id: UserId, image: Image) -> Receipt:
        raise NotImplementedError("method `.recognize()` must be implemented")


class IReceiptReadUC(ABC):
    @abstractmethod
    def read(self, receipt_uuid: ReceiptUUID) -> t.Optional[Receipt]:
        # public read interface
        raise NotImplementedError("method `.read()` must be implemented")

    @abstractmethod
    def read_many(self, user_id: UserId, limit: int, offset: int) -> t.List[Receipt]:
        raise NotImplementedError("method `.read_many()` must be implemented")


class IReceiptSplitUC(ABC):

    @abstractmethod
    def split(self, receipt: Receipt, choices: t.List[Choice]):
        # public split interface
        raise NotImplementedError("method `.create()` must be implemented")


class IUserReadUC(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UserId) -> t.Optional[User]:
        raise NotImplementedError("method `.get_by_id()` must be implemented")

    @abstractmethod
    def get_or_create(self, user: User) -> User:
        raise NotImplementedError("method `.get_or_create()` must be implemented")


class IUserSessionUC(ABC):
    @abstractmethod
    def check(self) -> t.Optional[User]:
        raise NotImplementedError("method `.check()` must be implemented")
