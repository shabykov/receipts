from pydantic import BaseModel


class ReceiptItemCreateError(BaseModel):
    message: str
    code: str


class ReceiptItemUpdateError(BaseModel):
    message: str
    code: str


class ReceiptItemReadError(BaseModel):
    message: str
    code: str
