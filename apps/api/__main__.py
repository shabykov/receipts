from logging import getLogger

from flasgger import Swagger, swag_from
from flask import Flask
from flask_restful import Api
from openai import OpenAI
from psycopg import connect

from apps.web.conf import init_settings
from internal.delivery.api.delivery import Delivery
from internal.repository.receipt.recognizer.openai.chat_v2 import OpenIAChatV2
from internal.repository.receipt.storage.postgres.repository import Repository as ReceiptStorage
from internal.repository.receipt_item.storage.postgres.repository import Repository as ReceiptItemStorage
from internal.usecase.receipt.read import ReceiptReadUseCase
from internal.usecase.receipt.recognize import ReceiptRecognizeUseCase
from pkg.log import init_logging

app = Flask(__name__)

swagger = Swagger(app)

api = Api(app, prefix='/api')

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
receipt_reader_uc = ReceiptReadUseCase(
    reader=receipt_storage,
)
openai_client = OpenAI(
    api_key=settings.openai_api_key.get_secret_value()
)
receipt_recognizer = OpenIAChatV2(
    openai_client,
    model=settings.openai_model
)
receipt_recognizer_uc = ReceiptRecognizeUseCase(
    recognizer=receipt_recognizer,
    creator=receipt_storage,
)
delivery = Delivery(
    receipt_reader_uc,
    receipt_recognizer_uc,
    flask_app=app,
    flask_api=api,
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

    logger.info("start rest api")

    web_app.start()
