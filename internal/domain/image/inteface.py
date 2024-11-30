from abc import ABC, abstractmethod

from internal.domain.image.url import URL


class Image(ABC):
    @abstractmethod
    def url(self) -> URL:
        raise NotImplementedError("method `.url()` must be implemented")

    @abstractmethod
    def data(self) -> str:
        raise NotImplementedError("method `.string()` must be implemented")


