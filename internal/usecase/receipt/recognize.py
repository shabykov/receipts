from logging import getLogger

from internal.domain.image import Image
from internal.domain.receipt import Receipt
from internal.usecase.interface import IReceiptRecognizeUC
from internal.usecase.ports.receipt import ICreator, IRecognizer

logger = getLogger("receipt.recognizer")


class ReceiptRecognizeUseCase(IReceiptRecognizeUC):
    def __init__(self, recognizer: IRecognizer, creator: ICreator):
        self._recognizer = recognizer
        self._creator = creator

    def recognize(self, user_id: int, image: Image) -> Receipt:
        receipt = self._recognizer.recognize(image)
        if receipt.is_valid():
            receipt.set_user_id(user_id)
            self._creator.create(receipt)
            logger.info(
                "receipt successfully recognized: user_id=%d, image_url=%s" % (user_id, image.url())
            )
            return receipt

        logger.warning(
            "recognized receipt is invalid: user_id=%d, image_url=%s" % (user_id, image.url())
        )
        return receipt
