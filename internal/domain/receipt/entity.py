import typing as t
import uuid
from collections import defaultdict
from datetime import datetime

from pydantic import BaseModel, Field, UUID4, field_serializer

from internal.domain.receipt.item import ReceiptItem, Choice
from internal.domain.user.id import UserId
from pkg.datetime import now


class Result(BaseModel):
    username: str
    amount: float
    tips: float = Field(
        default=0.0
    )


class Receipt(BaseModel):
    user_id: UserId = Field(
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
    subtotal: t.Optional[float] = Field(
        default=0
    )
    tips: t.Optional[float] = Field(
        default=0
    )
    total: t.Optional[float] = Field(
        default=0
    )
    created_at: datetime = Field(
        default_factory=now
    )

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4) -> str:
        return str(uuid)

    @field_serializer('created_at')
    def serialize_timestamp(self, dt: datetime) -> str:
        return dt.isoformat()

    def set_user_id(self, user_id: UserId):
        self.user_id = user_id

    def is_valid(self) -> bool:
        # required condition to valid receipt
        return len(self.items) > 0 and self.total > 0

    def is_splitted(self) -> bool:
        return all([item.is_splittable() for item in self.items])

    @property
    def results(self) -> t.List[Result]:

        results = defaultdict(Result)

        for item in self.items:
            for split in item.splits:
                if split.username not in results:
                    results[split.username] = Result(
                        username=split.username,
                        amount=item.price_per_user(split.username)
                    )
                else:
                    results[split.username].amount += item.price_per_user(split.username)

        return [v for v in results.values()]

    def split(self, choices: t.List[Choice]) -> t.List[ReceiptItem]:
        hs = {choice.uuid: choice for choice in choices}
        splitted = []
        for item in self.items:
            if item.uuid in hs:
                item.split(hs[item.uuid])
                splitted.append(item)
        return splitted


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
        store_name=store_name if store_name else "unknown",
        store_addr=store_addr if store_addr else "unknown",
        time=time if time else "unknown",
        date=date if date else "unknown",
        items=items,
        tips=tips if tips else 0,
        subtotal=subtotal if subtotal else 0,
        total=total if total else 0,
    )
