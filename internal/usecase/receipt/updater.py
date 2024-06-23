import typing as t
from internal.domain.receipt import Receipt, Updater, ReceiptUpdateError
from internal.usecase.usecase import ReceiptUpdater


class UseCase(ReceiptUpdater):
    def __init__(self, updater: Updater):
        self._updater = updater

    def update(self, receipt: Receipt) -> t.Optional[ReceiptUpdateError]:
        return self._updater.update(receipt)
