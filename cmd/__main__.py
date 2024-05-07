from openai import OpenAI
from telebot import TeleBot

from internal.delivery.telegram_bot.delivery import Delivery
from internal.repository.image.extractor.chatgpt.repository import Repository as ImageExtractor
from internal.repository.receipt.recognizer.chatgpt.repository import Repository as ReceiptRecognizer
from internal.usecase.receipt.recognizer import UseCase

from .config import init_settings


class App:
    def __init__(self, telegram_bot_listener: Delivery):
        self.telegram_bot_listener = telegram_bot_listener


if __name__ == "__main__":
    sett = init_settings()

    telegram_bot = TeleBot(
        token=sett.telegram_bot_token.get_secret_value()
    )
    openai_client = OpenAI(
        api_key=sett.openai_api_key.get_secret_value()
    )
    image_extractor = ImageExtractor(
        api_key=sett.openai_api_key.get_secret_value(),
    )
    receipt_recognizer = ReceiptRecognizer(
        client=openai_client,
        extractor=image_extractor,
    )
    app = App(
        telegram_bot_listener=Delivery(
            bot=telegram_bot,
            receipt_recognizer_uc=UseCase(
                recognizer=receipt_recognizer
            )
        )
    )
    app.telegram_bot_listener.start()
