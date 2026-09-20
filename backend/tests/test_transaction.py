import pytest

from app.db.transaction import transaction


class FakeSession:

    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def test_transaction_commits_on_success():
    db = FakeSession()

    with transaction(db):
        pass

    assert db.committed is True
    assert db.rolled_back is False


def test_transaction_rolls_back_on_failure():
    db = FakeSession()

    with pytest.raises(RuntimeError):
        with transaction(db):
            raise RuntimeError("database operation failed")

    assert db.committed is False
    assert db.rolled_back is True
