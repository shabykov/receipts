import typing as t

from pydantic import BaseModel, ValidationError

from internal.domain.receipt import Receipt, ReceiptItem, new


class ReceiptItemDTO(BaseModel):
    name: str
    quantity: int
    price: float


class ReceiptDTO(BaseModel):
    store_name: str
    store_addr: str
    date: str
    time: str
    items: t.List[ReceiptItemDTO]
    subtotal: float
    tips: float
    total: float


def convert(receipt_data: dict) -> Receipt:
    data = ReceiptDTO(**receipt_data)
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
