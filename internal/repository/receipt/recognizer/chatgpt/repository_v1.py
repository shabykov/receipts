"""
used this example
https://medium.com/@foxmike/extracting-structured-data-from-images-using-openais-gpt-4-vision-and-jason-liu-s-instructor-ec7f54ee0a91
"""
import typing as t
from logging import getLogger

import instructor
from openai import OpenAI

from internal.domain.image import (
    Image,
    ImageExtractor,
    ImageExtractError
)
from internal.domain.receipt import (
    Receipt,
    IRecognizer,
    ReceiptRecognizeError,
)
from .dto import convert, ReceiptDTO

logger = getLogger("receipt.recognizer.catgpt")

default_role = "user"
default_model = "gpt-4"
default_content_prefix = (
    "Extract store name, store address, date, time, products (name, quantity, price), "
    "subtotal, tips and total amount from from the following receipt description json:%s"
)


class Repository(IRecognizer):
    def __init__(self, client: OpenAI, extractor: ImageExtractor, model: str = default_model):
        self._client = instructor.patch(client)
        self._extractor = extractor
        self._model = model

    def recognize(self, image: Image) -> Receipt:
        try:
            image_content = self._extractor.extract(image)
        except ImageExtractError as err:
            raise ReceiptRecognizeError("unable to extract receipt image: %s" % err)

        receipt_data = self._client.chat.completions.create(
            model=self._model,
            response_model=ReceiptDTO,
            messages=[
                make_message(image_content),
            ]
        )
        if isinstance(receipt_data, ReceiptDTO):
            logger.info("receipt successfully recognized: receipt_data=%s" % receipt_data)

            return convert(receipt_data)

        raise ReceiptRecognizeError("unable to recognize receipt image")


def make_message(content: str) -> dict[str, str]:
    return {
        "role": default_role,
        "content": default_content_prefix % content
    }
