import typing as t

from pydantic import BaseModel

from internal.domain.receipt import Receipt, Item, new


class ProductDTO(BaseModel):
    name: str
    quantity: int
    price: float


class ReceiptDTO(BaseModel):
    store_name: str
    store_addr: str
    date: str
    time: str
    products: t.List[ProductDTO]
    subtotal: float
    tips: float
    total: float


def convert(data: ReceiptDTO) -> Receipt:
    return new(
        store_name=data.store_name,
        store_addr=data.store_addr,
        time=data.time,
        date=data.date,
        items=convert_items(data.items),
        tips=data.tips,
        subtotal=data.subtotal,
        total=data.total
    )


def convert_items(products: t.List[ProductDTO]) -> t.List[Item]:
    items = []
    for p in products:
        items.append(
            Item(
                product=p.name,
                quantity=p.quantity,
                price=p.price,
            )
        )
    return items
