from openai import OpenAI
from psycopg import connect
from telebot import TeleBot
from logging import getLogger

from app.config import init_settings
from app.log import init_logging
from internal.delivery.telegram_bot.delivery import Delivery
from internal.repository.image.extractor.chatgpt.repository import Repository as ImageExtractor
from internal.repository.receipt.recognizer.chatgpt.repository import Repository as ReceiptRecognizer
from internal.repository.receipt.storage.postgres.repository import Repository as ReceiptStorage
from internal.repository.receipt_item.storage.postgres.repository import Repository as ReceiptItemStorage
from internal.usecase.receipt.recognizer import UseCase


class App:
    def __init__(self, telegram_bot_listener: Delivery):
        self.telegram_bot_listener = telegram_bot_listener

    def start(self):
        self.telegram_bot_listener.start()


if __name__ == "__main__":
    settings = init_settings()

    init_logging(settings.logging_level)

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

    app = App(
        telegram_bot_listener=Delivery(
            bot=telegram_bot,
            receipt_recognizer_uc=UseCase(
                recognizer=receipt_recognizer,
                creator=receipt_storage,
            )
        )
    )

    logger.info("start app")

    app.start()
