import typing as t
from flask import Flask
from flask_pydantic import validate
from pydantic import BaseModel, Field

from internal.usecase.usecase import ReceiptUpdater, ReceiptReader
from internal.domain.receipt.model import Receipt


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
            receipt_updater_uc: ReceiptUpdater,
            receipt_reader_uc: ReceiptReader,
            flask: Flask,
            host: str,
            port: int = 8080,
    ):
        self.receipt_updater_uc = receipt_updater_uc
        self.receipt_reader_uc = receipt_reader_uc
        self.flask = flask
        self.host = host
        self.port = port
        self.init_handlers()

    def start(self):
        self.flask.run(host=self.host, port=self.port)

    def init_handlers(self):
        @self.flask.route("/receipts", methods=["PUT"])
        @validate(on_success_status=202)
        def update_receipt(body: Receipt):
            return self.receipt_updater_uc.update(body)

        @self.flask.route("/receipts/<receipt_uuid>/", methods=["GET"])
        @validate(on_success_status=200)
        def read_one_receipt(receipt_uuid: str):
            return self.receipt_reader_uc.read(receipt_uuid)

        @self.flask.route("/receipts/<user_id>/", methods=["GET"])
        @validate(on_success_status=200)
        def read_many_receipts(user_id: int, query: QueryParams):
            return self.receipt_reader_uc.read_many(user_id, query.limit, query.offset)
