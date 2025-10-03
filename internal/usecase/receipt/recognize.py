from logging import getLogger

from internal.domain.user.id import UserId
from internal.domain.image import Image
from internal.domain.receipt import Receipt
from internal.usecase.interface import IReceiptRecognizeUC
from internal.usecase.adapters.receipt import ICreator, IRecognizer

logger = getLogger("receipt.recognizer")


class ReceiptRecognizeUseCase(IReceiptRecognizeUC):
    def __init__(self, recognizer: IRecognizer, creator: ICreator):
        self._recognizer = recognizer
        self._creator = creator

    def recognize(self, user_id: UserId, image: Image) -> Receipt:
        return self._recognizer.recognize(image)
