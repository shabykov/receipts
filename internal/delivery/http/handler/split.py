import typing as t

from flask import Request, render_template, redirect, url_for
from pydantic import ValidationError

from internal.domain.receipt import ReceiptReadError
from internal.domain.receipt.item import ReceiptItemSplitError, Choice
from internal.domain.receipt.uuid import ReceiptUUID
from internal.domain.user import User
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
        # user = self.user_session_uc.check()
        # if not user:
        #     return redirect(
        #         url_for(
        #             endpoint='login',
        #             receipt_uuid=receipt_uuid,
        #             error="user is not authenticated"
        #         )
        #     )

        try:
            receipt = self.receipt_read_us.read(
                ReceiptUUID(receipt_uuid)
            )
        except ReceiptReadError as err:
            return render_template(
                "receipt-split.html",
                **{"receipt": None, "user": user, "error": err}
            )

        if request.method == "POST":
            try:
                choices = validate(request, user)
            except ValidationError as err:
                return render_template(
                    "receipt-split.html",
                    **{"receipt": receipt, "user": user, "err": err}
                )
            try:
                self.receipt_split_uc.split(
                    receipt,
                    choices=choices,
                )
            except ReceiptItemSplitError as err:
                return render_template(
                    "receipt-split.html",
                    **{"receipt": receipt, "user": user, "error": err}
                )

        return render_template(
            "receipt-split.html",
            **{"receipt": receipt, "user": user, "error": None}
        )


def validate(request: Request, user: User) -> t.List[Choice]:
    return [
        Choice(
            uuid=uuid,
            quantity=int(quantity),
            username=user.username.string(),
        )
        for uuid, quantity in request.form.items() if int(quantity) > 0
    ]
