from datetime import datetime

from pydantic import BaseModel, Field

from internal.domain.user.id import UserId
from internal.domain.user.username import Username

from pkg.datetime import now


class User(BaseModel):
    user_id: UserId = Field(
        default=0
    )
    username: Username = Field(
        default="unknown"
    )
    created_at: datetime = Field(
        default_factory=now
    )

    def id(self) -> str:
        return str(self.user_id)


def new(user_id: UserId, username: Username):
    return User(user_id=user_id, username=username)


def new_user_by_username(username: Username) -> User:
    return User(username=username)


def new_unknown_user() -> User:
    return new_user_by_username(Username("unknown"))
