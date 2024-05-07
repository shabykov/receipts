import os
import os.path as path
import typing as t

import pandas as pd
from pydantic import UUID4

from internal.domain.receipt import (
    Receipt,
    Creator,
    Updater,
    Reader,
)

DIR = os.path.dirname(os.path.realpath(__file__))


class Repository(Creator, Updater, Reader):

    def __init__(self, receipts_file: str = "receipts.csv", items_path: str = "items.csv"):
        self._receipts_path = path.join(DIR, receipts_file)
        self._items_path = path.join(DIR, items_path)

    def create(self, receipt: Receipt):
        self._save_receipt(receipt)

    def update(self, receipt: Receipt):
        pass

    def read_by_uuid(self, uuid: UUID4) -> Receipt:
        pass

    def read_list(self, limit: int, offset: int) -> t.List[Receipt]:
        pass

    def _save_receipt(self, receipt: Receipt):
        self._save_receipt_items(receipt)
        row = receipt.dict()
        row.pop("items")

        df = pd.DataFrame(data=row)
        receipt_df = open_receipt_df(self._receipts_path)
        pd.concat(
            [df, receipt_df],
            ignore_index=True
        ).to_csv(self._receipts_path)

    def _save_receipt_items(self, receipt: Receipt):
        rows = []
        for item in receipt.items:
            row = item.dict()
            row["receipt_uuid"] = receipt.uuid
            rows.append(row)

        df = pd.DataFrame(data=rows)
        items_df = open_items_df(self._items_path)
        pd.concat(
            [df, items_df],
            ignore_index=True
        ).to_csv(self._items_path)


def open_receipt_df(receipts_path) -> pd.DataFrame:
    if path.exists(receipts_path):
        df = pd.read_csv(receipts_path)
    else:
        df = pd.DataFrame(
            columns=[
                'user_id',
                'uuid',
                'store_name',
                'store_addr',
                'date',
                'time',
                'subtotal',
                'tips',
                'total',
                'created_at'
            ]
        )

    return df


def open_items_df(items_path: str) -> pd.DataFrame:
    if path.exists(items_path):
        df = pd.read_csv(items_path)
    else:
        df = pd.DataFrame(
            columns=[
                'product',
                'quantity',
                'price',
                'rating',
                'receipt_uuid',
            ]
        )
    return df
