from logging import getLogger

from internal.domain.receipt import Receipt
from internal.domain.sharing import (
    new_sharing,
    ICreator as ISharingCreator,
)
from internal.domain.user import (
    User,
    IReader as IUserReader,
    ICreator as IUserCreator
)
from internal.usecase.interface import IReceiptShare

logger = getLogger("receipt.share")


class ReceiptShareUseCase(IReceiptShare):
    def __init__(
            self,
            user_reader: IUserReader,
            user_creator: IUserCreator,
            sharing_creator: ISharingCreator,
    ):
        self._user_reader = user_reader
        self._user_creator = user_creator
        self._sharing_creator = sharing_creator

    def share(self, receipt: Receipt, with_user: User):
        # read or create user by share username
        user = self._user_reader.read_by_username(with_user.username)
        if not user:
            user = self._user_creator.create(with_user)

        # create sharing item
        return self._sharing_creator.create(
            new_sharing(receipt, user),
        )
