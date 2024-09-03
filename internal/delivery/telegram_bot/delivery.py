from telebot import TeleBot
from telebot.types import Message

from internal.domain.receipt import ReceiptRecognizeError
from internal.usecase.interface import IReceiptRecognizeUC
from .photo.converter import convert


class Delivery:
    def __init__(
            self,
            bot: TeleBot,
            receipt_recognizer_uc: IReceiptRecognizeUC
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

        @self.bot.message_handler(content_types=['photo', 'image'])
        def image(message: Message):
            self.handle_receipt(message)

    def handle_help(self, message: Message):
        self.bot.send_message(
            message.chat.id,
            text='Did someone call for help?'
        )

    def handle_start(self, message: Message):
        self.bot.send_message(
            message.chat.id,
            text="To start just send photo of your /receipt"
        )

    def handle_text(self, message: Message):
        self.bot.reply_to(
            message,
            text="I cant help you with text requests"
        )

    def handle_receipt(self, message: Message):
        try:
            receipt = self.receipt_recognizer_uc.recognize(
                message.from_user.id,
                convert(self.bot, message)
            )
        except ReceiptRecognizeError as err:
            return self.bot.reply_to(
                message,
                text=str(err),
            )
        except Exception as err:
            return self.bot.reply_to(
                message,
                text="unknown err: %s" % str(err),
            )

        return self.bot.reply_to(
            message,
            text=f"http://localhost:8080/receipts/{receipt.uuid}/show",
        )
