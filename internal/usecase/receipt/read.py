import typing as t

from pydantic import UUID4

from internal.domain.receipt import Receipt
from internal.usecase.interface import IReceiptReadUC
from internal.usecase.ports.receipt import IReader


class ReceiptReadUseCase(IReceiptReadUC):
    def __init__(self, reader: IReader):
        self._reader = reader

    def read(self, receipt_uuid: UUID4) -> t.Optional[Receipt]:
        return self._reader.read_by_uuid(receipt_uuid)

    def read_many(self, user_id: int, limit: int, offset: int) -> t.List[Receipt]:
        return self._reader.read_many(user_id, limit, offset)
