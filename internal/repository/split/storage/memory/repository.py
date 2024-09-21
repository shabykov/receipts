import typing as t
from collections import defaultdict

from pydantic import UUID4

from internal.domain.split import IReader, ICreator, Split


class Repository(IReader, ICreator):
    def __init__(self):
        self._data = defaultdict(list)

    def read_many(self, receipt_id: UUID4) -> t.List[Split]:
        return self._data.get(receipt_id)

    def create(self, splits: t.List[Split]):
        for split in splits:
            self._data[split.receipt.uuid].append(split)
