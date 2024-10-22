from abc import ABC, abstractmethod


class Image(ABC):
    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError("method `.url()` must be implemented")

    @abstractmethod
    def data(self) -> str:
        raise NotImplementedError("method `.string()` must be implemented")


