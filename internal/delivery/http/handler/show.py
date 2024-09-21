from flask import render_template, redirect, url_for

from internal.delivery.http.handler.session import SessionChecker
from internal.domain.receipt import ReceiptReadError
from internal.usecase.interface import IReceiptReadUC


class ShowHandler:
    def __init__(
            self,
            session: SessionChecker,
            receipt_reader_uc: IReceiptReadUC,
    ):
        self.session = session
        self.receipt_reader_uc = receipt_reader_uc

    def show(self, receipt_uuid: str):
        user = self.session.check()
        if not user:
            redirect(
                url_for('login', error="user is not authenticated")
            )

        try:
            receipt = self.receipt_reader_uc.read(receipt_uuid)
        except ReceiptReadError as err:
            return render_template(
                "receipt-err.html",
                **{"receipt_uuid": receipt_uuid, "error": err}
            )

        return render_template(
            "receipt-show.html",
            **{"receipt_uuid": receipt_uuid, "receipt": receipt}
        )
