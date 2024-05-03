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

    def recognize(self, image: Image) -> t.Tuple[Receipt, t.Optional[ReceiptRecognizeError]]:
        receipt, err = self._recognizer.recognize(image)
        if err is not None:
            return receipt, err

        self._creator.create(receipt)

        return receipt, None
