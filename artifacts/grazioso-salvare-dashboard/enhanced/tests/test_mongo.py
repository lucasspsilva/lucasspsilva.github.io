"""
Regression tests for the existing AnimalShelter CRUD module.

These tests make sure my enhancement did not break the original CRUD class.
They use a fake (mock) database instead of a real MongoDB, so they only check
that mongo.py validates the input and calls the right MongoDB methods.
"""
import os
import sys
import types
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# If pymongo is not installed, use fake modules so mongo.py can still be imported
pymongo_stub = types.ModuleType("pymongo")
pymongo_stub.MongoClient = MagicMock()
errors_stub = types.ModuleType("pymongo.errors")
errors_stub.ConnectionFailure = Exception
bson_stub = types.ModuleType("bson")
objectid_stub = types.ModuleType("bson.objectid")
objectid_stub.ObjectId = object
sys.modules.setdefault("pymongo", pymongo_stub)
sys.modules.setdefault("pymongo.errors", errors_stub)
sys.modules.setdefault("bson", bson_stub)
sys.modules.setdefault("bson.objectid", objectid_stub)

from mongo import AnimalShelter


@pytest.fixture
def shelter():
    shelter = AnimalShelter("user", "pass")
    shelter.database = MagicMock()
    return shelter


def test_create_rejects_invalid_data(shelter):
    with pytest.raises(Exception):
        shelter.create(None)
    with pytest.raises(Exception):
        shelter.create("not a dict")


def test_create_inserts_document(shelter):
    shelter.create({"name": "Rex"})
    shelter.database.animals.insert_one.assert_called_once_with({"name": "Rex"})


def test_read_returns_list(shelter):
    shelter.database.animals.find.return_value = iter([{"name": "Rex"}])
    assert shelter.read({"name": "Rex"}) == [{"name": "Rex"}]


def test_read_rejects_invalid_data(shelter):
    with pytest.raises(Exception):
        shelter.read(None)
    with pytest.raises(Exception):
        shelter.read(["not", "a", "dict"])


def test_update_wraps_plain_fields_in_set(shelter):
    shelter.update({"name": "Rex"}, {"breed": "Mix"})
    shelter.database.animals.update_one.assert_called_once_with(
        {"name": "Rex"}, {"$set": {"breed": "Mix"}})


def test_update_many_keeps_operator(shelter):
    shelter.update({"name": "Rex"}, {"$inc": {"age": 1}}, many=True)
    shelter.database.animals.update_many.assert_called_once_with(
        {"name": "Rex"}, {"$inc": {"age": 1}})


def test_update_rejects_invalid_data(shelter):
    with pytest.raises(Exception):
        shelter.update(None, {"a": 1})
    with pytest.raises(Exception):
        shelter.update({"a": 1}, None)


def test_delete_one_and_many(shelter):
    shelter.delete({"name": "Rex"})
    shelter.database.animals.delete_one.assert_called_once_with({"name": "Rex"})
    shelter.delete({"name": "Rex"}, many=True)
    shelter.database.animals.delete_many.assert_called_once_with({"name": "Rex"})


def test_delete_rejects_invalid_data(shelter):
    with pytest.raises(Exception):
        shelter.delete(None)
