import base64

from pydantic import BaseModel

from internal.domain.image.inteface import Image


class ImageBase64(Image, BaseModel):
    content: bytes
    format: str

    def url(self) -> str:
        return "data:image/%s;base64,%s" % (self.format, self.data())

    def data(self) -> str:
        return base64.b64encode(self.content).decode('utf-8')
