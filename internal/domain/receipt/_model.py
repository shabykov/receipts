import typing as t
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, UUID4

from internal.domain.receipt.item import ReceiptItem
from pkg.datetime import now


class Receipt(BaseModel):
    user_id: int = Field(
        default=0
    )
    uuid: UUID4 = Field(
        default_factory=uuid.uuid4
    )
    store_name: str = Field(
        default="unknown"
    )
    store_addr: str = Field(
        default="unknown"
    )
    date: str = Field(
        default="unknown"
    )
    time: str = Field(
        default="unknown"
    )
    items: t.List[ReceiptItem] = Field(
        default=[]
    )
    subtotal: float = Field(
        default=0
    )
    tips: float = Field(
        default=0
    )
    total: float = Field(
        default=0
    )
    created_at: datetime = Field(
        default_factory=now
    )
    is_splitd: bool = Field(
        default=False
    )

    def set_user_id(self, user_id: int):
        self.user_id = user_id

    def is_valid(self) -> bool:
        # required condition to valid receipt
        return len(self.items) > 0 and self.total > 0


def new(
        store_name: str,
        store_addr: str,
        time: str,
        date: str,
        items: t.List[ReceiptItem],
        tips: float,
        subtotal: float,
        total: float) -> Receipt:
    return Receipt(
        store_name=store_name,
        store_addr=store_addr,
        time=time,
        date=date,
        items=items,
        tips=tips,
        subtotal=subtotal,
        total=total,
    )