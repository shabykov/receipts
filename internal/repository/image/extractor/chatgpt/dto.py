from pydantic import BaseModel


class Error(BaseModel):
    code: str
    type: str
    message: str


class ErrorDTO(BaseModel):
    error: Error


class Message(BaseModel):
    content: str


class Choice(BaseModel):
    message: Message


class SuccessDTO(BaseModel):
    choices: list[Choice]
