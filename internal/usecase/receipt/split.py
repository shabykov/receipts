import typing as t
from logging import getLogger

from pydantic import UUID4

from internal.domain.receipt import Receipt
from internal.domain.receipt.split import new_splits
from internal.domain.user import User
from internal.usecase.interface import (
    IUserReadUC,
    IReceiptReadUC,
    IReceiptSplitUC,
)
from internal.usecase.ports.receipt.split import (
    IReader,
    ICreator,
)

logger = getLogger("receipt.split")


class ReceiptSplitUseCase(IReceiptSplitUC):
    def __init__(
            self,
            user_uc: IUserReadUC,
            receipt_uc: IReceiptReadUC,
            split_reader: IReader,
            split_creator: ICreator,
    ):
        self._user_uc = user_uc
        self._receipt_uc = receipt_uc
        self._split_reader = split_reader
        self._split_creator = split_creator

    def get(self, receipt_uuid: UUID4) -> Receipt:
        # read receipt
        receipt = self._receipt_uc.read(receipt_uuid)

        # read receipt splits
        splits = self._split_reader.read_many(receipt_uuid)

        # set receipt splits
        receipt.set_splits(splits)

        return receipt

    def create(self, with_user: User, receipt_uuid: UUID4, receipt_items: t.List[str]) -> Receipt:
        # read already split receipt
        receipt = self.get(receipt_uuid)

        # slit receipt
        receipt.split_by(with_user.username, receipt_items)

        # save splits
        self._split_creator.create(
            new_splits(with_user.username, receipt.uuid, receipt_items)
        )

        return receipt
