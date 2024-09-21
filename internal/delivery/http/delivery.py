from flask import Flask, request
from pydantic import BaseModel, Field

from pkg.session import SessionManager
from .handler.login import LoginHandler
from .handler.show import ShowHandler
from .handler.split import SplitHandler


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
            login_handler: LoginHandler,
            receipt_show_handler: ShowHandler,
            receipt_split_handler: SplitHandler,
            session_manager: SessionManager,
            flask_app: Flask,
            host: str,
            port: int = 8080,
    ):
        self.login_handler = login_handler
        self.receipt_show_handler = receipt_show_handler
        self.receipt_split_handler = receipt_split_handler
        self.session_manager = session_manager
        self.flask = flask_app
        self.host = host
        self.port = port
        self.init_handlers()

    def start(self):
        self.flask.run(host=self.host, port=self.port, debug=True)

    def init_handlers(self):
        @self.flask.route('/login')
        def login():
            return self.login_handler.login(request)

        @self.flask.route('/telegram_login_callback', methods=['GET'])
        def telegram_login_callback():
            return self.login_handler.telegram_login_callback(
                request
            )

        @self.flask.route("/receipts/<receipt_uuid>/show", methods=['GET'])
        def show(receipt_uuid: str):
            return self.receipt_show_handler.show(
                receipt_uuid,
            )

        @self.flask.route("/receipts/<receipt_uuid>/split", methods=['GET', 'POST'])
        def split(receipt_uuid: str):
            return self.receipt_split_handler.split(
                receipt_uuid,
                request=request
            )
