from logging import getLogger

from flask import Flask
from psycopg import connect

from apps.web.conf import init_settings
from internal.delivery.http.delivery import Delivery
from internal.delivery.http.handler.login import LoginHandler
from internal.delivery.http.handler.show import ShowHandler
from internal.delivery.http.handler.split import SplitHandler
from internal.repository.receipt.storage.postgres.repository import Repository as ReceiptStorage
from internal.repository.receipt_item.storage.postgres.repository import Repository as ReceiptItemStorage
from internal.repository.user.storage.postgres.repository import Repository as UserStorage
from internal.usecase.receipt.read import ReceiptReadUseCase
from internal.usecase.receipt.split import ReceiptSplitUseCase
from internal.usecase.user.read import UserReadUseCase
from internal.usecase.user.session import UserSessionUseCase
from pkg.auth.telegram import TelegramAuth
from pkg.log import init_logging

app = Flask(__name__, template_folder="../../internal/delivery/http/handler/templates")

init_logging()

settings = init_settings()

app.secret_key = settings.secret_key.get_secret_value()

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

user_storage = UserStorage(
    conn=postgresql_conn
)
user_uc = UserReadUseCase(
    reader=user_storage,
    creator=user_storage
)
receipt_reader_uc = ReceiptReadUseCase(
    reader=receipt_storage,
)
user_session_uc = UserSessionUseCase(
    user_uc=user_uc
)
delivery = Delivery(
    login_handler=LoginHandler(
        url=settings.url,
        bot_name=settings.bot_name,
        auth=TelegramAuth(
            bot_token=settings.telegram_bot_token
        ),
        user_uc=user_uc,
    ),
    receipt_split_handler=SplitHandler(
        user_session_uc=user_session_uc,
        receipt_read_us=receipt_reader_uc,
        receipt_split_uc=ReceiptSplitUseCase(
            user_uc=user_uc,
            receipt_item_updater=receipt_item_storage,
        ),
    ),
    receipt_show_handler=ShowHandler(
        user_session_uc=user_session_uc,
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
