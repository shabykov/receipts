from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from psycopg import connect
from telebot import TeleBot
from logging import getLogger
from flask import Flask

from apps.conf import init_settings
from apps.log import init_logging
from internal.delivery.http.delivery import Delivery as HttpDelivery
from internal.delivery.telegram_bot.delivery import Delivery as TelegramDelivery
from internal.repository.image.extractor.chatgpt.repository import Repository as ImageExtractor
from internal.repository.receipt.recognizer.chatgpt.repository import Repository as ReceiptRecognizer
from internal.repository.receipt.storage.postgres.repository import Repository as ReceiptStorage
from internal.repository.receipt_item.storage.postgres.repository import Repository as ReceiptItemStorage
from internal.usecase.receipt.recognizer import UseCase as ReceiptRecognizerUc
from internal.usecase.receipt.updater import UseCase as ReceiptUpdaterUc
from internal.usecase.receipt.reader import UseCase as ReceiptReaderUc


class App:
    def __init__(self, telegram_bot_listener: TelegramDelivery, http_listener: HttpDelivery):
        self.telegram_bot_listener = telegram_bot_listener
        self.http_listener = http_listener

    def start(self):
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.submit(self.http_listener.start)
            executor.submit(self.telegram_bot_listener.start)


if __name__ == "__main__":
    settings = init_settings()

    init_logging()

    logger = getLogger("main")
    logger.info("init app")

    telegram_bot = TeleBot(
        token=settings.telegram_bot_token.get_secret_value()
    )
    openai_client = OpenAI(
        api_key=settings.openai_api_key.get_secret_value()
    )
    postgresql_conn = connect(
        conninfo=settings.postgresql_url.unicode_string()
    )
    image_extractor = ImageExtractor(
        api_key=settings.openai_api_key.get_secret_value(),
    )
    receipt_recognizer = ReceiptRecognizer(
        client=openai_client,
        extractor=image_extractor
    )
    receipt_item_storage = ReceiptItemStorage(
        conn=postgresql_conn
    )
    receipt_storage = ReceiptStorage(
        conn=postgresql_conn,
        item_repo=receipt_item_storage,
    )

    flask_app = Flask(__name__)

    app = App(
        telegram_bot_listener=TelegramDelivery(
            bot=telegram_bot,
            receipt_recognizer_uc=ReceiptRecognizerUc(
                recognizer=receipt_recognizer,
                creator=receipt_storage,
            )
        ),
        http_listener=HttpDelivery(
            receipt_updater_uc=ReceiptUpdaterUc(
                updater=receipt_storage
            ),
            receipt_reader_uc=ReceiptReaderUc(
                reader=receipt_storage,
            ),
            flask=flask_app,
            host=settings.web_host,
            port=settings.web_port
        )
    )

    logger.info("start app")

    app.start()
