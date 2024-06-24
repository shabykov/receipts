from flask import Flask
from psycopg import connect
from logging import getLogger

from pkg.log import init_logging
from internal.delivery.http.delivery import Delivery
from internal.repository.receipt.storage.postgres.repository import Repository as ReceiptStorage
from internal.repository.receipt_item.storage.postgres.repository import Repository as ReceiptItemStorage
from internal.usecase.receipt.updater import UseCase as ReceiptUpdaterUc
from internal.usecase.receipt.reader import UseCase as ReceiptReaderUc

from apps.api.conf import init_settings

app = Flask(__name__)

init_logging()

settings = init_settings()

logger = getLogger("web_api")

logger.info("init app")

postgresql_conn = connect(
    conninfo=settings.postgresql_url.unicode_string()
)
receipt_item_storage = ReceiptItemStorage(
    conn=postgresql_conn
)
receipt_storage = ReceiptStorage(
    conn=postgresql_conn,
    item_repo=receipt_item_storage,
)

delivery = Delivery(
    receipt_updater_uc=ReceiptUpdaterUc(
        updater=receipt_storage,
    ),
    receipt_reader_uc=ReceiptReaderUc(
        reader=receipt_storage,
    ),
    flask=app,
    host=settings.web_host,
    port=settings.web_port,
)


class App:
    def __init__(self, http_listener: Delivery):
        self.http_listener = http_listener

    def start(self):
        self.http_listener.start()


if __name__ == "__main__":
    web_app = App(http_listener=delivery)

    logger.info("start web api")

    web_app.start()
