import typing as t
from logging import getLogger

from pydantic import UUID4

from internal.domain.split import (
    new_split,
    new_splits,
    Splits,
    IReader as ISplitReader,
    ICreator as ISplitCreator,
)
from internal.usecase.interface import (
    IUserReadUC,
    IReceiptReadUC,
    IReceiptSplitUC,
)

logger = getLogger("receipt.split")


class ReceiptSplitUseCase(IReceiptSplitUC):
    def __init__(
            self,
            user_uc: IUserReadUC,
            receipt_uc: IReceiptReadUC,
            split_reader: ISplitReader,
            split_creator: ISplitCreator,
    ):
        self._user_uc = user_uc
        self._receipt_uc = receipt_uc
        self._split_reader = split_reader
        self._split_creator = split_creator

    def get(self, receipt_uuid: UUID4) -> t.Optional[Splits]:
        splits = self._split_reader.read_many(receipt_uuid)
        if not splits:
            return None

        return new_splits(splits)

    def create(self, with_user: str, receipt_uuid: UUID4, receipt_items: t.List[str]) -> Splits:
        user = self._user_uc.get_by_username(with_user)
        receipt = self._receipt_uc.read(receipt_uuid)
        return new_splits(
            self._split_creator.create(
                [
                    new_split(user, receipt, UUID4(receipt_item))
                    for receipt_item in receipt_items
                ],
            )
        )
