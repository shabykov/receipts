import typing as t

from flask import Request, render_template, redirect, url_for
from pydantic import BaseModel, ValidationError

from internal.delivery.http.handler.session import SessionChecker
from internal.domain.receipt import ReceiptReadError
from internal.domain.receipt.item import convert_to_uuid
from internal.domain.split import splited_by
from internal.usecase.interface import IReceiptSplitUC, IReceiptReadUC


class SplitHandler:
    def __init__(
            self,
            session: SessionChecker,
            receipt_split_uc: IReceiptSplitUC,
            receipt_reader_uc: IReceiptReadUC,
    ):
        self.session = session
        self.receipt_split_uc = receipt_split_uc
        self.receipt_reader_uc = receipt_reader_uc

    def split(self, receipt_uuid: str, request: Request):
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
                **{"receipt": None, "error": err}
            )

        if request.method == "POST":
            # TODO: validate CSRF token, validate input
            param, err = validate(request)
            if err != "":
                return render_template(
                    "receipt-split.html",
                    **{"receipt": receipt, "err": err}
                )

            try:
                self.receipt_split_uc.create(
                    receipt_uuid,
                    convert_to_uuid(param.receipt_items),
                    param.username,
                )
            except Exception as err:
                return render_template(
                    "receipt-split.html",
                    **{"receipt": receipt, "error": err}
                )

            return render_template(
                "receipt-split.html",
                **{"receipt": receipt, "error": None}
            )

        splits = self.receipt_split_uc.get(receipt_uuid)
        if splits:
            splited_by(receipt, splits)

        return render_template(
            "receipt-split.html",
            **{"receipt": receipt, "error": None}
        )


class Body(BaseModel):
    receipt_items: str


def validate(request: Request) -> (t.Optional[Body], str):
    receipt_items = request.form.getlist('receipt_items')
    if not receipt_items:
        return None, "incorrect receipt_items"

    try:
        body = Body(
            receipt_items=request.form.getlist("receipt_items")
        )
    except ValidationError as err:
        return None, str(err)

    return body, ""
