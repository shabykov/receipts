from abc import ABC, abstractmethod

from internal.domain.sharing._model import Sharing


class ICreator(ABC):
    @abstractmethod
    def create(self, sharing: Sharing) -> Sharing:
        raise NotImplementedError("method `.create()` must be implemented")
