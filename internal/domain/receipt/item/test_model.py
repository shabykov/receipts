from .model import ReceiptItem


def test_split():
    item = ReceiptItem(quantity=2)
    item.split("user1")
    item.split("user1")
    assert len(item.split_by_users) == 1
    assert "user1" in item.split_by_users

    item.split("user2")
    assert len(item.split_by_users) == 2
    assert "user2" in item.split_by_users


def test_is_splittable():
    item = ReceiptItem(quantity=2)
    assert item.is_splittable() is True

    item.split("user1")
    assert item.is_splittable() is True

    item.split("user2")
    assert item.is_splittable() is False
