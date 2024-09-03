import uuid
from datetime import datetime

from pydantic import BaseModel, Field, UUID4

from internal.domain.receipt import Receipt
from internal.domain.user import User
from pkg.datetime.now import now


class Sharing(BaseModel):
    uuid: UUID4 = Field(
        default_factory=uuid.uuid4
    )
    receipt: Receipt
    user: User
    created_at: datetime = Field(
        default_factory=now
    )


def new_sharing(receipt: Receipt, with_user: User) -> Sharing:
    return Sharing(receipt=receipt, user=with_user)
