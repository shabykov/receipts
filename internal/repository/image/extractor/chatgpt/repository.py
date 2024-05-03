import typing as t

import pydantic.errors
import requests

from internal.domain.image import (
    Image,
    ImageExtractor,
    ImageExtractError,
)
from .dto import SuccessDTO, ErrorDTO

default_url = "https://api.openai.com/v1/chat/completions"
default_role = "user"
default_model = "gpt-4-vision-preview"
default_max_tokens = 500


class Repository(ImageExtractor):
    def __init__(
            self,
            api_key: str,
            api_url: str = default_url,
    ):
        self._api_url = api_url
        self._api_key = api_key

    def extract(self, image: Image) -> t.Tuple[str, t.Optional[ImageExtractError]]:
        try:
            resp = requests.post(
                self._api_url,
                headers=headers(self._api_key),
                json=payload,
            )
        except Exception as e:
            return "", handle_err(e)

        if resp.status_code != 200:
            return "", handle_failure(resp)

        return handle_success(resp)


def handle_err(err: Exception) -> ImageExtractError:
    return ImageExtractError(
        message=str(err),
        code="requests_err"
    )


def handle_failure(resp: requests.Response) -> ImageExtractError:
    try:
        err = ErrorDTO.parse_obj(resp.json())
    except pydantic.ValidationError as err:
        return ImageExtractError(
            message="parse error_message err: %s" % str(err),
            code="error_message_validation_err",
        )

    return ImageExtractError(
        message=err.error.message,
        code=err.error.code,
    )


def handle_success(resp: requests.Response) -> t.Tuple[str, t.Optional[ImageExtractError]]:
    try:
        ans = SuccessDTO.parse_obj(resp.json())
    except pydantic.ValidationError as err:
        return "", ImageExtractError(
            message="parse success_message err: %s" % str(err),
            code="success_message_validation_err",
        )

    if len(ans.choices) < 1:
        return "", ImageExtractError(
            message="empty answer",
            code="empty_answer_err",
        )

    return ans.choices[0].message.content, None


def headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer %s" % api_key
    }


def payload(image: Image) -> dict:
    return {
        "model": default_model,
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
                            "url": "data:image/%s;base64,%s" % (image.format(), image.data())
                        }
                    }
                ]
            }
        ],
        "max_tokens": default_max_tokens
    }
