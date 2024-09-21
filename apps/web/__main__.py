import os
from logging import getLogger

from flask import Flask
from psycopg import connect

from apps.web.conf import init_settings
from internal.delivery.http.delivery import Delivery
from internal.delivery.http.handler.login import LoginHandler
from internal.delivery.http.handler.session import SessionChecker
from internal.delivery.http.handler.show import ShowHandler
from internal.delivery.http.handler.split import SplitHandler
from internal.repository.receipt.storage.postgres.repository import Repository as ReceiptStorage
from internal.repository.receipt_item.storage.postgres.repository import Repository as ReceiptItemStorage
from internal.repository.split.storage.memory.repository import Repository as SplitStorage
from internal.repository.user.storage.memory.repository import Repository as UserStorage
from internal.usecase.receipt.read import ReceiptReadUseCase
from internal.usecase.receipt.split import ReceiptSplitUseCase
from internal.usecase.user.read import UserReadUseCase
from pkg.auth.telegram import TelegramAuth
from pkg.log import init_logging
from pkg.session.base64 import Base64SessionManager

template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
template_dir = os.path.join(template_dir, 'templates')

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

user_storage = UserStorage()
user_uc = UserReadUseCase(
    reader=user_storage,
    creator=user_storage
)

split_storage = SplitStorage()
receipt_reader_uc = ReceiptReadUseCase(
    reader=receipt_storage,
)
session_manager = Base64SessionManager()
session_checker = SessionChecker(
    user_uc=user_uc
)
delivery = Delivery(
    login_handler=LoginHandler(
        auth=TelegramAuth(
            bot_token=settings.telegram_bot_token
        ),
        session_manager=session_manager,
        user_uc=user_uc,
    ),
    receipt_split_handler=SplitHandler(
        session=session_checker,
        receipt_split_uc=ReceiptSplitUseCase(
            user_uc=user_uc,
            receipt_uc=receipt_reader_uc,
            split_reader=split_storage,
            split_creator=split_storage,
        ),
        receipt_reader_uc=receipt_reader_uc,
    ),
    receipt_show_handler=ShowHandler(
        session=session_checker,
        receipt_reader_uc=ReceiptReadUseCase(
            reader=receipt_storage,
        ),
    ),
    session_manager=session_manager,
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
