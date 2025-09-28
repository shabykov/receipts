from werkzeug.datastructures.file_storage import FileStorage

from internal.domain.image import Image
from internal.domain.image.base64 import ImageBase64


def convert(file: FileStorage) -> Image:
    content = file.read()
    fmt = file.filename.rsplit('.', 1)[1].lower()
    return ImageBase64(content=content, format=fmt)
