"""
used this example
https://cookbook.openai.com/examples/data_extraction_transformation
"""

from logging import getLogger

import instructor
from openai import OpenAI

from internal.domain.image import Image
from internal.domain.receipt import (
    Receipt,
    ReceiptRecognizeError,
)
from internal.usecase.adapters.receipt import IRecognizer
from .dto import convert, ReceiptDTO

logger = getLogger("receipt.recognizer.catgpt")

default_role = "user"
default_model = "gpt-4o"
default_content_prefix = (
    "Extract store name, store address, date, time, products (name, quantity, price), "
    "subtotal, tips and total amount from from the following receipt description json:%s"
)

system_role = "system"
system_prompt = """
    You are an OCR-like data extraction tool that extracts stores/restaurants receipt data from image.
   
    1. Please extract the data in this receipt, grouping data according to theme/sub groups, and then output into JSON.

    2. Please keep the keys and values of the JSON in the original language. 

    3. The type of data you might encounter in the receipt includes but is not limited to: product information, 
    price information, quantity information, total price information, store name information, 
    taxes, and total charges etc. 

    4. If the page contains no charge data, please output an empty JSON object and don't make up any data.

    5. If there are blank data fields in the receipt, please include them as "null" values in the JSON object.
    
    6. If there are tables in the receipt, capture all of the rows and columns in the JSON object. 
    Even if a column is blank, include it as a key in the JSON object with a null value.
    
    7. If a row is blank denote missing fields with "null" values. 
    
    8. Don't interpolate or make up data.

    9. Please maintain the table structure of the charges, i.e. capture all of the rows and columns in the JSON object.

    """


class OpenIAChatV2(IRecognizer):
    def __init__(self, client: OpenAI, model: str = default_model):
        self._client = instructor.patch(client)
        self._model = model

    def recognize(self, image: Image) -> Receipt:
        receipt_data = self._client.chat.completions.create(
            model=self._model,
            response_model=ReceiptDTO,
            messages=make_messages(image),
            temperature=0.0,
        )
        if isinstance(receipt_data, ReceiptDTO):
            logger.info("receipt successfully recognized: receipt_data=%s" % receipt_data)

            return convert(receipt_data)

        raise ReceiptRecognizeError("unable to recognize receipt image")


def make_messages(image: Image) -> list[dict[str, str]]:
    return [
        {
            "role": system_role,
            "content": system_prompt
        },
        {
            "role": default_role,
            "content": [
                {
                    "type": "text",
                    "text": default_content_prefix
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image.url().string(),
                        "detail": "high"
                    }
                }
            ]
        }
    ]
