from flask import Flask
from psycopg import connect
from logging import getLogger

from apps.log import init_logging
from apps.api.conf import init_settings
from internal.delivery.http.delivery import Delivery
from internal.repository.receipt.storage.postgres.repository import Repository as ReceiptStorage
from internal.repository.receipt_item.storage.postgres.repository import Repository as ReceiptItemStorage
from internal.usecase.receipt.updater import UseCase as ReceiptUpdaterUc
from internal.usecase.receipt.reader import UseCase as ReceiptReaderUc

flask_app = Flask(__name__)


class App:
    def __init__(self, http_listener: Delivery):
        self.http_listener = http_listener

    def start(self):
        self.http_listener.start()


if __name__ == "__main__":
    settings = init_settings()

    init_logging()

    logger = getLogger("main")
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

    app = App(
        http_listener=Delivery(
            receipt_updater_uc=ReceiptUpdaterUc(
                updater=receipt_storage,
            ),
            receipt_reader_uc=ReceiptReaderUc(
                reader=receipt_storage,
            ),
            flask=flask_app,
            host=settings.web_host,
            port=settings.web_port,
        )
    )

    logger.info("start app")

    app.start()
