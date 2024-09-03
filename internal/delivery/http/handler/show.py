from flask import render_template

from internal.usecase.interface import IReceiptRead


class ShowHandler:
    def __init__(
            self,
            receipt_reader_uc: IReceiptRead,
    ):
        self.receipt_reader_uc = receipt_reader_uc

    def handle(self, receipt_uuid: str) -> str:
        receipt, err = self.receipt_reader_uc.read(receipt_uuid)
        if err is not None:
            return render_template(
                "receipt-err.html",
                **{"receipt_uuid": receipt_uuid, "error": err}
            )

        return render_template(
            "receipt-show.html",
            **{"receipt_uuid": receipt_uuid, "receipt": receipt}
        )
