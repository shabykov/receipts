from flask import render_template, redirect, url_for

from internal.domain.receipt import ReceiptReadError
from internal.domain.receipt.uuid import ReceiptUUID
from internal.usecase.interface import IReceiptReadUC, IUserSessionUC


class ShowHandler:
    def __init__(
            self,
            user_session_uc: IUserSessionUC,
            receipt_reader_uc: IReceiptReadUC,
    ):
        self.user_session_uc = user_session_uc
        self.receipt_reader_uc = receipt_reader_uc

    def show(self, receipt_uuid: str):
        user = self.user_session_uc.check()
        if not user:
            return redirect(
                url_for(
                    endpoint='login',
                    receipt_uuid=receipt_uuid,
                    error="user is not authenticated"
                )
            )

        try:
            receipt = self.receipt_reader_uc.read(
                ReceiptUUID(receipt_uuid)
            )
        except ReceiptReadError as err:
            return render_template(
                "receipt-err.html",
                **{"receipt_uuid": receipt_uuid, "error": err}
            )

        return render_template(
            "receipt-show.html",
            **{"receipt_uuid": receipt_uuid, "receipt": receipt}
        )
