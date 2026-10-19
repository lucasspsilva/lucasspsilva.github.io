from unittest.mock import patch

import pytest
from pymongo.errors import ServerSelectionTimeoutError

from contacts import database
from contacts.errors import DatabaseError


# load_dotenv is patched out so a real .env file on my machine
# doesn't change what these tests see
@pytest.fixture(autouse=True)
def no_dotenv():
    with patch.object(database, "load_dotenv"):
        yield


def test_missing_uri(monkeypatch):
    monkeypatch.delenv("MONGO_URI", raising=False)

    with pytest.raises(DatabaseError, match="MONGO_URI"):
        database.get_database()


def test_server_down(monkeypatch):
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017")

    with patch.object(database, "MongoClient") as client:
        client.return_value.admin.command.side_effect = ServerSelectionTimeoutError("down")

        with pytest.raises(DatabaseError, match="Could not connect"):
            database.get_database()


def test_uses_database_name_from_env(monkeypatch):
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGO_DB_NAME", "my_test_db")

    with patch.object(database, "MongoClient") as client:
        database.get_database()

        client.return_value.__getitem__.assert_called_with("my_test_db")
