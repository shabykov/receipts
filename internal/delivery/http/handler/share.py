from flask import Request, render_template

from internal.domain.user import User
from internal.usecase.interface import IReceiptShare, IReceiptRead


class ShareHandler:
    def __init__(
            self,
            receipt_share_uc: IReceiptShare,
            receipt_reader_uc: IReceiptRead,
    ):
        self.receipt_share_uc = receipt_share_uc
        self.receipt_reader_uc = receipt_reader_uc

    def handle(self, receipt_uuid: str, request: Request) -> str:
        receipt, err = self.receipt_reader_uc.read(receipt_uuid)
        if err is not None:
            return render_template(
                "receipt-err.html",
                **{"receipt_uuid": receipt_uuid, "error": err}
            )

        if request.method == "POST":
            username = request.form.get("username")
            if not username:
                return render_template(
                    "receipt-err.html",
                    **{"receipt_uuid": receipt_uuid, "error": err}
                )

            err = self.receipt_share_uc.share(
                receipt,
                with_user=User(
                    username=username,
                )
            )
            if err is not None:
                return render_template(
                    "receipt-err.html",
                    **{"receipt_uuid": receipt_uuid, "error": err}
                )

        return render_template(
            "receipt-share.html",
            **{"receipt_uuid": receipt_uuid, "receipt": receipt}
        )
