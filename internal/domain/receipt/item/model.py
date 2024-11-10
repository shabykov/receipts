import typing as t
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, UUID4

from internal.domain.receipt.item import ReceiptItemSplitError
from pkg.datetime import now


class ReceiptItem(BaseModel):
    uuid: UUID4 = Field(
        default_factory=uuid.uuid4
    )
    product: str = Field(
        default="unknown"
    )
    quantity: int = Field(
        default=0
    )
    price: float = Field(
        default=0
    )
    created_at: datetime = Field(
        default_factory=now
    )
    split_by_users: t.Set[str] = Field(
        default_factory=set,
    )

    def split(self, username: str):
        if len(self.split_by_users) == self.quantity:
            raise ReceiptItemSplitError("receipt item has already splited")

        self.split_by_users.add(username)

    def is_splittable(self) -> bool:
        if len(self.split_by_users) == self.quantity:
            return False

        return True


def new(product: str, quantity: int, price: float) -> ReceiptItem:
    return ReceiptItem(
        product=product,
        quantity=quantity,
        price=price,
    )


def convert_to_uuid(values: t.List[str]) -> t.List[UUID4]:
    return [
        UUID4(v) for v in values
    ]


def empty_items() -> t.List[UUID4]:
    return []
