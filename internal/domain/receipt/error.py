import enum

from pydantic import BaseModel


class ReceiptRecognizeErrorCode(enum.IntEnum):
    recognize_receipt_extractor_image_error = 1
    recognize_receipt_error = 2


class ReceiptRecognizeError(BaseModel):
    message: str
    code: ReceiptRecognizeErrorCode
