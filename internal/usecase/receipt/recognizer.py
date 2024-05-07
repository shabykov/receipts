import typing as t

from internal.domain.image import Image
from internal.domain.receipt import (
    Receipt,
    ReceiptRecognizeError,
    Recognizer,
    Creator,
)
from internal.usecase.usecase import ReceiptRecognizer


class UseCase(ReceiptRecognizer):
    def __init__(self, recognizer: Recognizer, creator: Creator):
        self._recognizer = recognizer
        self._creator = creator

    def recognize(self, user_id: int, image: Image) -> t.Tuple[Receipt, t.Optional[ReceiptRecognizeError]]:
        receipt, err = self._recognizer.recognize(image)
        if err is not None:
            return receipt, err

        if receipt.is_valid():
            receipt.set_user_id(user_id)
            self._creator.create(receipt)

        return receipt, None
