from telebot import TeleBot
from telebot.types import Message

from internal.domain.image import Image
from internal.domain.image.base64 import ImageBase64


def convert(bot: TeleBot, message: Message) -> Image:
    file_info = bot.get_file(message.photo[-1].file_id)

    return ImageBase64(
        content=bot.download_file(file_info.file_path),
        format="jpg"
    )
