"""
used this example
https://medium.com/@foxmike/extracting-structured-data-from-images-using-openais-gpt-4-vision-and-jason-liu-s-instructor-ec7f54ee0a91
"""
import typing as t

import instructor
from openai import OpenAI

from internal.domain.image import (
    Image,
    ImageExtractor,
)
from internal.domain.receipt import (
    Receipt,
    Recognizer,
    ReceiptRecognizeError,
    ReceiptRecognizeErrorCode,

)
from .dto import convert, ReceiptDTO

default_role = "user"
default_model = "gpt-4"
default_content_prefix = (
    "Extract store name, store address, date, time, products (name, quantity, price), "
    "subtotal, tips and total amount from from the following receipt description json:%s"
)


class Repository(Recognizer):
    def __init__(self, client: OpenAI, extractor: ImageExtractor, model: str = default_model):
        self._client = instructor.patch(client)
        self._extractor = extractor
        self._model = model

    def recognize(self, image: Image) -> t.Tuple[Receipt, t.Optional[ReceiptRecognizeError]]:
        image_content, err = self._extractor.extract(image)
        if err is not None:
            return Receipt(), ReceiptRecognizeError(
                message="unable to extract receipt image: %s" % err.error,
                code=ReceiptRecognizeErrorCode.recognize_receipt_extractor_image_error
            )

        receipt_data = self._client.chat.completions.create(
            model=self._model,
            response_model=ReceiptDTO,
            messages=[
                make_message(image_content),
            ]
        )
        if isinstance(receipt_data, ReceiptDTO):
            return convert(receipt_data), None

        return Receipt(), ReceiptRecognizeError(
            message="unable to recognize receipt image",
            code=ReceiptRecognizeErrorCode.recognize_receipt_error
        )


def make_message(content: str) -> dict[str, str]:
    return {
        "role": default_role,
        "content": default_content_prefix % content
    }
