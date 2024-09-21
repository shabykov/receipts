import typing as t
from datetime import datetime

from pydantic import BaseModel, Field, UUID4

from internal.domain.receipt import Receipt
from internal.domain.user import User
from pkg.datetime import now


class Split(BaseModel):
    # who
    user: User

    # what
    receipt: Receipt

    # which of items
    receipt_item_id: UUID4

    # when
    created_at: datetime = Field(
        default_factory=now
    )


def new_split(user: User, receipt: Receipt, receipt_item_id: UUID4) -> Split:
    return Split(
        user=user,
        receipt=receipt,
        receipt_item=receipt_item_id
    )


class Splits(BaseModel):
    items: t.Dict[UUID4, Split]


def new_splits(splits: t.List[Split]) -> Splits:
    return Splits(
        items={
            split.receipt_item_id: split for split in splits
        }
    )


def splited_by(receipt: Receipt, splits: Splits):
    for receipt_item in receipt.items:
        split = splits.items.get(receipt_item.uuid)
        if split:
            receipt_item.split_by.append(split.user)
