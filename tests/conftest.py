
import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def temporary_database(tmp_path, monkeypatch):
    import database

    test_db = tmp_path / "test_bean_brew.db"

    monkeypatch.setattr(database, "DB_PATH", test_db)

    database.init_db()

    yield
