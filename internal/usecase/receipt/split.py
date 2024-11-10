import typing as t
from logging import getLogger

from internal.domain.receipt import Receipt
from internal.domain.user import User
from internal.usecase.interface import (
    IUserReadUC,
    IReceiptSplitUC,
)
from internal.usecase.ports.receipt.item import IUpdater

logger = getLogger("receipt.split")


class ReceiptSplitUseCase(IReceiptSplitUC):
    def __init__(
            self,
            user_uc: IUserReadUC,
            receipt_item_updater: IUpdater,
    ):
        self._user_uc = user_uc
        self._receipt_item_updater = receipt_item_updater

    def split(self, with_user: User, receipt: Receipt, receipt_items: t.List[str]):
        # slit receipt
        receipt.split(with_user.username, receipt_items)

        # save receipt items
        self._receipt_item_updater.update_many(receipt.uuid, receipt.items)
        return receipt
