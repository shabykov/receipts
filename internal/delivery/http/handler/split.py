import typing as t

from flask import Request, render_template, redirect, url_for
from pydantic import BaseModel, ValidationError, UUID4

from internal.domain.receipt import ReceiptReadError
from internal.domain.receipt.item import ReceiptItemSplitError
from internal.usecase.interface import IReceiptReadUC, IReceiptSplitUC, IUserSessionUC


class SplitHandler:
    def __init__(
            self,
            user_session_uc: IUserSessionUC,
            receipt_read_us: IReceiptReadUC,
            receipt_split_uc: IReceiptSplitUC,
    ):
        self.user_session_uc = user_session_uc
        self.receipt_read_us = receipt_read_us
        self.receipt_split_uc = receipt_split_uc

    def split(self, receipt_uuid: str, request: Request):
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
            receipt = self.receipt_read_us.read(receipt_uuid)
        except ReceiptReadError as err:
            return render_template(
                "receipt-split.html",
                **{"receipt": None, "error": err}
            )

        if request.method == "POST":
            # TODO: validate CSRF token, validate input
            param, err = validate(request)
            if err != "":
                return render_template(
                    "receipt-split.html",
                    **{"receipt": None, "err": err}
                )

            try:
                self.receipt_split_uc.split(
                    user,
                    receipt,
                    param.receipt_items,
                )
            except ReceiptItemSplitError as err:
                return render_template(
                    "receipt-split.html",
                    **{"receipt": None, "error": err}
                )

        return render_template(
            "receipt-split.html",
            **{"receipt": receipt, "error": None}
        )


class Body(BaseModel):
    receipt_items: t.List[UUID4]


def validate(request: Request) -> (t.Optional[Body], str):
    receipt_items = request.form.getlist('receipt_items')
    if not receipt_items:
        return None, "incorrect receipt_items"

    try:
        body = Body(
            receipt_items=receipt_items
        )
    except ValidationError as err:
        return None, str(err)

    return body, ""
