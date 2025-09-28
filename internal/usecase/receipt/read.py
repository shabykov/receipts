import typing as t

from internal.domain.receipt import Receipt
from internal.domain.receipt.receipt_uuid import ReceiptUUID
from internal.domain.user.id import UserId
from internal.usecase.adapters.receipt import IReader
from internal.usecase.interface import IReceiptReadUC


class ReceiptReadUseCase(IReceiptReadUC):
    def __init__(self, reader: IReader):
        self._reader = reader

    def read(self, receipt_uuid: ReceiptUUID) -> t.Optional[Receipt]:
        return self._reader.read_by_uuid(receipt_uuid)

    def read_many(self, user_id: UserId, limit: int, offset: int) -> t.List[Receipt]:
        return self._reader.read_many(user_id, limit, offset)
