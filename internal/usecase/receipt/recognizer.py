import typing as t
from logging import getLogger

from internal.domain.image import Image
from internal.domain.receipt import (
    Receipt,
    ReceiptRecognizeError,
    Recognizer,
    Creator,
)
from internal.usecase.usecase import ReceiptRecognizer

logger = getLogger("receipt.recognizer")


class UseCase(ReceiptRecognizer):
    def __init__(self, recognizer: Recognizer, creator: Creator):
        self._recognizer = recognizer
        self._creator = creator

    def recognize(self, user_id: int, image: Image) -> t.Tuple[Receipt, t.Optional[ReceiptRecognizeError]]:
        receipt, err = self._recognizer.recognize(image)
        if err is not None:
            logger.error(
                "unable to recognize receipt: user_id=%d, err=%s" % (user_id, err)
            )
            return receipt, err

        if receipt.is_valid():
            receipt.set_user_id(user_id)
            self._creator.create(receipt)
            logger.info(
                "receipt successfully recognized: user_id=%d, image_url=%s" % (user_id, image.url())
            )
            return receipt, None

        logger.warning(
            "recognized receipt is invalid: user_id=%d, image_url=%s" % (user_id, image.url())
        )
        return receipt, None
