import typing as t
from abc import ABC, abstractmethod

from .error import ImageExtractError


class Image(ABC):
    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError("method `.url()` must be implemented")

    @abstractmethod
    def data(self) -> str:
        raise NotImplementedError("method `.string()` must be implemented")


class ImageExtractor(ABC):
    @abstractmethod
    def extract(self, image: Image) -> t.Tuple[str, t.Optional[ImageExtractError]]:
        raise NotImplementedError("method `extract` must be implemented")
