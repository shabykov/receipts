import os
from flask import Flask
from psycopg import connect
from logging import getLogger

from pkg.log import init_logging
from internal.delivery.http.delivery import Delivery
from internal.delivery.http.handler.show import ShowHandler
from internal.delivery.http.handler.share import ShareHandler
from internal.repository.receipt.storage.postgres.repository import Repository as ReceiptStorage
from internal.repository.receipt_item.storage.postgres.repository import Repository as ReceiptItemStorage
from internal.usecase.receipt.read import ReceiptReadUseCase
from internal.usecase.receipt.share import ReceiptShareUseCase

from apps.web.conf import init_settings

template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
template_dir = os.path.join(template_dir, 'templates')

app = Flask(__name__, template_folder="../../internal/delivery/http/handler/templates")

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
    receipt_share_handler=ShareHandler(
        receipt_share_uc=ReceiptShareUseCase(
            updater=receipt_storage,
        ),
        receipt_reader_uc=ReceiptReadUseCase(
            reader=receipt_storage,
        ),
    ),
    receipt_show_handler=ShowHandler(
        receipt_reader_uc=ReceiptReadUseCase(
            reader=receipt_storage,
        ),
    ),
    flask_app=app,
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

    logger.info("start web web")

    web_app.start()
