import typing as t

from pydantic import UUID4

from internal.domain.receipt import Receipt, Reader, ReceiptReadError
from internal.usecase.usecase import ReceiptReader


class UseCase(ReceiptReader):
    def __init__(self, reader: Reader):
        self._reader = reader

    def read(self, receipt_uuid: UUID4) -> t.Tuple[t.Optional[Receipt], t.Optional[ReceiptReadError]]:
        return self._reader.read_by_uuid(receipt_uuid)

    def read_many(self, user_id: int, limit: int, offset: int) -> t.Tuple[
        t.List[Receipt], t.Optional[ReceiptReadError]]:
        return self._reader.read_many(user_id, limit, offset)
