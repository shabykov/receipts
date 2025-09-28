from logging import getLogger

import pydantic.errors
import requests

from internal.domain.image import (
    Image,
    ImageExtractError,
)
from internal.usecase.ports.image import ImageExtractor
from .dto import SuccessDTO, ErrorDTO

logger = getLogger("image.extractor.chatgpt")

default_url = "https://api.openai.com/v1/chat/completions"
default_role = "user"
default_model = "gpt-4-vision-preview"
default_max_tokens = 500


class Repository(ImageExtractor):
    def __init__(
            self,
            api_key: str,
            api_url: str = default_url,
            model: str = default_model,
    ):
        self._api_url = api_url
        self._api_key = api_key
        self._model = model

    def extract(self, image: Image) -> str:
        try:
            resp = requests.post(
                self._api_url,
                headers=headers(self._api_key),
                json=payload(image, self._model),
            )
        except Exception as e:
            raise ImageExtractError(str(e))

        if resp.status_code != 200:
            handle_failure(resp)

        return handle_success(resp)


def handle_err(err: Exception) -> ImageExtractError:
    raise ImageExtractError(str(err))


def handle_failure(resp: requests.Response):
    try:
        err = ErrorDTO.parse_obj(resp.json())
    except pydantic.ValidationError as err:
        raise ImageExtractError("parse error_message err: %s" % str(err))

    return ImageExtractError(err.error.message)


def handle_success(resp: requests.Response) -> str:
    try:
        ans = SuccessDTO.parse_obj(resp.json())
    except pydantic.ValidationError as err:
        raise ImageExtractError("parse success_message err: %s" % str(err))

    if len(ans.choices) < 1:
        raise ImageExtractError("empty answer")

    return ans.choices[0].message.content


def headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer %s" % api_key
    }


def payload(image: Image, model: str) -> dict:
    return {
        "model": model,
        "messages": [
            {
                "role": default_role,
                "content": [
                    {
                        "type": "text",
                        "text": "Extract text from this image/receipt"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image.url().string()
                        }
                    }
                ]
            }
        ],
        "max_tokens": default_max_tokens
    }
