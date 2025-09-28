import typing as t

from pydantic import BaseModel, Field

from internal.domain.receipt import Receipt, ReceiptItem, new


class ReceiptItemDTO(BaseModel):
    name: t.Optional[str] = Field(
        default="unknown"
    )
    quantity: t.Optional[int] = Field(
        default=0
    )
    price: t.Optional[float] = Field(
        default=0
    )


class ReceiptDTO(BaseModel):
    store_name: t.Optional[str] = Field(
        default="unknown"
    )
    store_addr: t.Optional[str] = Field(
        default="unknown"
    )
    date: t.Optional[str] = Field(
        default="unknown"
    )
    time: t.Optional[str] = Field(
        default="unknown"
    )

    items: t.List[ReceiptItemDTO]

    subtotal: t.Optional[float] = Field(
        default=0
    )
    tips: t.Optional[float] = Field(
        default=0
    )
    total: t.Optional[float] = Field(
        default=0
    )


def convert(data: ReceiptDTO) -> Receipt:
    return new(
        store_name=data.store_name,
        store_addr=data.store_addr,
        time=data.time,
        date=data.date,
        items=convert_products(data.items),
        tips=data.tips,
        subtotal=data.subtotal,
        total=data.total

    )


def convert_products(products: t.List[ReceiptItemDTO]) -> t.List[ReceiptItem]:
    items = []
    for p in products:
        items.append(
            ReceiptItem(
                product=p.name,
                quantity=p.quantity,
                price=p.price,
            )
        )
    return items
