import typing as t

from flask import Request, render_template, redirect, url_for
from pydantic import BaseModel, ValidationError

from internal.domain.receipt.split import SplitReadError, SplitCreateError
from internal.usecase.interface import IReceiptSplitUC, IUserSessionUC


class SplitHandler:
    def __init__(
            self,
            user_session_uc: IUserSessionUC,
            receipt_split_uc: IReceiptSplitUC,
    ):
        self.user_session_uc = user_session_uc
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

        if request.method == "POST":
            # TODO: validate CSRF token, validate input
            param, err = validate(request)
            if err != "":
                return render_template(
                    "receipt-split.html",
                    **{"receipt": None, "err": err}
                )

            try:
                receipt = self.receipt_split_uc.create(
                    user,
                    receipt_uuid,
                    param.receipt_items,
                )

            except SplitCreateError as err:
                return render_template(
                    "receipt-split.html",
                    **{"receipt": None, "error": err}
                )
        else:
            try:
                receipt = self.receipt_split_uc.get(receipt_uuid)
            except SplitReadError as err:
                return render_template(
                    "receipt-split.html",
                    **{"receipt": None, "error": err}
                )

        return render_template(
            "receipt-split.html",
            **{"receipt": receipt, "error": None}
        )


class Body(BaseModel):
    receipt_items: t.List[str]


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
