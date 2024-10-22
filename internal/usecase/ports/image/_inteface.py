from abc import ABC, abstractmethod

from internal.domain.image import Image


class ImageExtractor(ABC):
    @abstractmethod
    def extract(self, image: Image) -> str:
        raise NotImplementedError("method `extract` must be implemented")
