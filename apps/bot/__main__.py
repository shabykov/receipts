from openai import OpenAI
from psycopg import connect
from telebot import TeleBot
from logging import getLogger

from pkg.log import init_logging
from internal.delivery.telegram_bot.delivery import Delivery
from internal.repository.receipt.recognizer.ollama.chat import OllamaChat
# from internal.repository.receipt.recognizer.openai.chat_v2 import OpenIAChatV2
from internal.repository.receipt.storage.postgres.repository import Repository as ReceiptStorage
from internal.repository.receipt_item.storage.postgres.repository import Repository as ReceiptItemStorage
from internal.usecase.receipt.recognize import ReceiptRecognizeUseCase

from apps.bot.conf import init_settings

settings = init_settings()

init_logging()

logger = getLogger("telegram_bot")

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
receipt_recognizer = OllamaChat(
    model=settings.ollama_model
)
receipt_item_storage = ReceiptItemStorage(
    conn=postgresql_conn
)
receipt_storage = ReceiptStorage(
    conn=postgresql_conn,
    item_repo=receipt_item_storage,
)

delivery = Delivery(
    bot=telegram_bot,
    url=settings.url,
    receipt_recognizer_uc=ReceiptRecognizeUseCase(
        recognizer=receipt_recognizer,
        creator=receipt_storage,
    )
)


class App:
    def __init__(self, telegram_bot_listener: Delivery):
        self.telegram_bot_listener = telegram_bot_listener

    def start(self):
        self.telegram_bot_listener.start()


if __name__ == "__main__":
    telegram_bot_app = App(telegram_bot_listener=delivery)

    logger.info("start telegram bot")

    telegram_bot_app.start()
