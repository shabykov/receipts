from .dto import ReceiptDTO


def test_json_schema():
    got = ReceiptDTO.model_json_schema()
    assert isinstance(got, dict)
