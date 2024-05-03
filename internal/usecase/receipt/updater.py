from internal.domain.receipt import Receipt, Updater
from internal.usecase.usecase import ReceiptUpdater


class UseCase(ReceiptUpdater):
    def __init__(self, updater: Updater):
        self._updater = updater

    def update(self, receipt: Receipt):
        self._updater.update(receipt)
