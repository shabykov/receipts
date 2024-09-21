from datetime import datetime

from pydantic import BaseModel, Field

from pkg.datetime import now


class User(BaseModel):
    user_id: int = Field(
        default=0
    )
    username: str = Field(
        default="unknown"
    )
    created_at: datetime = Field(
        default_factory=now
    )

    def id(self) -> str:
        return str(self.user_id)


def new(user_id: int, username: str):
    return User(user_id=user_id, username=username)


def new_user_by_username(username: str) -> User:
    return User(username=username)


def new_unknown_user() -> User:
    return new_user_by_username("unknown")
