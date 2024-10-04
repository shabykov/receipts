import typing as t
from datetime import datetime

from pydantic import BaseModel, Field, UUID4

from pkg.datetime import now


class Split(BaseModel):
    # who
    username: str

    # what
    receipt_uuid: UUID4

    # which of items
    receipt_item_id: UUID4

    # when
    created_at: datetime = Field(
        default_factory=now
    )


def new_split(username: str, receipt_id: UUID4, receipt_item_id: str) -> Split:
    split = Split(
        username=username,
        receipt_uuid=receipt_id,
        receipt_item_id=receipt_item_id
    )

    return split


def new_splits(username: str, receipt_id: UUID4, items: t.List[str]) -> t.List[Split]:
    return [
        new_split(username, receipt_id, receipt_item_id) for receipt_item_id in items
    ]
