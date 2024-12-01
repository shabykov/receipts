import typing as t
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, UUID4

from pkg.datetime import now


class Choice(BaseModel):
    uuid: UUID4
    username: str
    quantity: int = Field(
        default=1
    )

    def __hash__(self):
        return hash(self.uuid)

    def __str__(self):
        return self.uuid

    def __eq__(self, other):
        return str(self) == str(other)


class Split(BaseModel):
    username: str
    quantity: int = Field(
        default=1
    )

    def uuid(self) -> UUID4:
        return self._uuid

    def __hash__(self):
        return hash(self.username)

    def __str__(self):
        return self.username

    def __eq__(self, other):
        return str(self) == str(other)


class ReceiptItem(BaseModel):
    uuid: UUID4 = Field(
        default_factory=uuid.uuid4
    )
    product: t.Optional[str] = Field(
        default="unknown"
    )
    quantity: t.Optional[int] = Field(
        default=0
    )
    price: t.Optional[float] = Field(
        default=0
    )
    created_at: datetime = Field(
        default_factory=now
    )
    splits: t.Set[Split] = Field(
        default_factory=set
    )
    split_error_message: str = Field(
        default=""
    )

    def splits_as_json(self) -> t.List[str]:
        return [s.model_dump_json() for s in self.splits]

    def price_per_quantity(self) -> float:
        return self.price / self.quantity

    def price_per_user(self, username: str) -> float:
        return self.price / self.quantity * self._user_quantity(username)

    def _user_quantity(self, username: str) -> int:
        return sum([split.quantity for split in self.splits if split.username == username])

    def split(self, choice: Choice) -> bool:
        if choice.quantity > self.quantity:
            self.split_error_message = "choice quantity is > itme quantity"
            return False

        if len(self.splits) == self.quantity:
            self.split_error_message = "item has already splitted"
            return False

        if (sum([s.quantity for s in self.splits]) + choice.quantity) > self.quantity:
            self.split_error_message = "item can't be splitted"
            return False

        self.splits.add(
            Split(
                username=choice.username,
                quantity=choice.quantity
            )
        )
        return True

    def is_splittable(self) -> bool:
        if len(self.splits) == self.quantity:
            return False

        if sum([split.quantity for split in self.splits]) >= self.quantity:
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
