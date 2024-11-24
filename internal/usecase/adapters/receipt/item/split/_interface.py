import typing as t
from abc import ABC, abstractmethod

from internal.domain.receipt.item import Split


class IUpdater(ABC):

    @abstractmethod
    def upsert_splits(self, items: t.List[Split]):
        raise NotImplementedError("method `.update_many()` must be implemented")
