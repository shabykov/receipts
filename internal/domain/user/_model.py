import uuid
from datetime import datetime

from pydantic import BaseModel, Field, UUID4

from pkg.datetime.now import now


class User(BaseModel):
    uuid: UUID4 = Field(
        default_factory=uuid.uuid4
    )
    telegram_user_id: int = Field(
        default=0
    )
    username: str = Field(
        default="unknown"
    )
    created_at: datetime = Field(
        default_factory=now
    )
