from telebot import TeleBot
from telebot.types import Message

from internal.usecase.usecase import (
    ReceiptRecognizer,
)
from .photo.converter import convert


class Delivery:
    def __init__(
            self,
            bot: TeleBot,
            receipt_recognizer_uc: ReceiptRecognizer
    ):
        self.bot = bot
        self.receipt_recognizer_uc = receipt_recognizer_uc
        self.init_handlers()

    def start(self):
        self.bot.infinity_polling()

    def init_handlers(self):
        @self.bot.message_handler(regexp='help')
        def command_help(message):
            self.handle_help(message)

        @self.bot.message_handler(commands=['start'])
        def start(message: Message):
            self.handle_start(message)

        @self.bot.message_handler(content_types=['text'])
        def text(message: Message):
            self.handle_text(message)

        @self.bot.message_handler(content_types=['photo', 'image'])
        def image(message: Message):
            self.handle_image(message)

        @self.bot.message_handler(
            func=lambda message: message.document.mime_type == 'image/jpg',
            content_types=['document'],
        )
        def document(message: Message):
            self.handle_image_document(message)

    def handle_help(self, message: Message):
        self.bot.send_message(
            message.chat.id,
            text='Did someone call for help?'
        )

    def handle_start(self, message: Message):
        self.bot.send_message(
            message.chat.id,
            text="To start just senf photo of your receipt"
        )

    def handle_text(self, message: Message):
        self.bot.reply_to(
            message,
            text="I cant help you with text requests"
        )

    def handle_image(self, message: Message):
        receipt, err = self.receipt_recognizer_uc.recognize(
            convert(self.bot, message)
        )
        if err is not None:
            return self.bot.reply_to(
                message,
                text=err.message
            )
        return self.bot.reply_to(
            message,
            text=receipt.json()
        )

    def handle_image_document(self, message: Message):
        receipt, err = self.receipt_recognizer_uc.recognize(
            convert(self.bot, message)
        )
        if err is not None:
            return self.bot.reply_to(
                message,
                text=err.message
            )
        return self.bot.reply_to(
            message,
            text=receipt.json()
        )
