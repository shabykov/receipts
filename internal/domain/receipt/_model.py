import typing as t
import uuid
from collections import defaultdict
from datetime import datetime

from pydantic import BaseModel, Field, UUID4

from internal.domain.receipt.item import ReceiptItem
from internal.domain.receipt.split import Split, SplitCreateError
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

    def set_splits(self, splits: t.List[Split]):

        # agg users by receipt_item_id
        items = defaultdict(list)
        for split in splits:
            items[split.receipt_item_id].append(split.username)

        # set users by receipt_item_id
        for receipt_item in self.items:
            receipt_item.split_by = items.get(receipt_item.uuid, [])

    def split_by(self, username: str, splits: t.List[str]):

        # agg users by receipt_item_id
        items = defaultdict(list)
        for split_item_id in splits:
            items[split_item_id].append(username)

        for item in self.items:
            # check is item splitable
            if item.quantity < (len(item.split_by) + len(items[str(item.uuid)])):
                raise SplitCreateError(
                    "Item {} has already splited by {}".format(
                        item.product,
                        ", ".join(item.split_by)
                    )
                )
            item.split_by.append(username)


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
