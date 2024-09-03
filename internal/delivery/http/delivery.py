from flask import Flask, request
from pydantic import BaseModel, Field

from .handler.show import ShowHandler
from .handler.share import ShareHandler


class QueryParams(BaseModel):
    limit: int = Field(
        default=100
    )
    offset: int = Field(
        default=0
    )


class Delivery:
    def __init__(
            self,
            receipt_show_handler: ShowHandler,
            receipt_share_handler: ShareHandler,
            flask_app: Flask,
            host: str,
            port: int = 8080,
    ):
        self.receipt_show_handler = receipt_show_handler
        self.receipt_share_handler = receipt_share_handler
        self.flask = flask_app
        self.host = host
        self.port = port
        self.init_handlers()

    def start(self):
        self.flask.run(host=self.host, port=self.port, debug=True)

    def init_handlers(self):
        @self.flask.route("/receipts/<receipt_uuid>/show", methods=['GET'])
        def show(receipt_uuid: str):
            return self.receipt_show_handler.handle(receipt_uuid)

        @self.flask.route("/receipts/<receipt_uuid>/share", methods=['GET', 'POST'])
        def share(receipt_uuid: str):
            return self.receipt_share_handler.handle(receipt_uuid, request=request)
