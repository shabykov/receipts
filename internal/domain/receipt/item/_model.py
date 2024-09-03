import uuid
from datetime import datetime
from pydantic import BaseModel, Field, UUID4

from pkg.datetime.now import now


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


def new(product: str, quantity: int, price: float) -> ReceiptItem:
    return ReceiptItem(
        product=product,
        quantity=quantity,
        price=price,
    )
