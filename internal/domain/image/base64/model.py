import base64

from pydantic import BaseModel

from internal.domain.image.inteface import Image


class ImageBase64(Image, BaseModel):
    content: bytes
    format: str

    def format(self) -> str:
        return self.format

    def data(self) -> str:
        return base64.b64encode(self.content).decode('utf-8')
