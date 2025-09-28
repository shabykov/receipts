import typing as t
from logging import getLogger

from internal.domain.receipt import Receipt
from internal.domain.receipt.item import Choice
from internal.usecase.ports.receipt.item import IUpdater
from internal.usecase.interface import (
    IUserReadUC,
    IReceiptSplitUC,
)

logger = getLogger("receipt.split")


class ReceiptSplitUseCase(IReceiptSplitUC):
    def __init__(
            self,
            user_uc: IUserReadUC,
            receipt_item_updater: IUpdater,
    ):
        self._user_uc = user_uc
        self._receipt_item_updater = receipt_item_updater

    def split(self, receipt: Receipt, choices: t.List[Choice]):
        # split receipt items
        self._receipt_item_updater.update_many(
            receipt.uuid,
            receipt.split(choices)
        )
