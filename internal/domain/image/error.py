from pydantic import BaseModel


class ImageExtractError(BaseModel):
    message: str
    code: str
