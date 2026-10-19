from unittest.mock import MagicMock

import mongomock
import pytest
from pymongo.errors import ServerSelectionTimeoutError

from contacts.contact import Contact
from contacts.contact_service import MongoContactService
from contacts.errors import DatabaseError


# mongomock acts like a real MongoDB collection but lives in memory,
# so these tests don't need a database server running
@pytest.fixture
def collection():
    return mongomock.MongoClient().db.contacts


@pytest.fixture
def service(collection):
    return MongoContactService(collection)


@pytest.fixture
def contact():
    return Contact("001", "Lucas", "Silva", "1234567890", "123 Main Street")


def test_add_and_get_contact(service, contact):
    service.add(contact)

    result = service.get("001")

    assert result.contact_id == "001"
    assert result.first_name == "Lucas"
    assert result.last_name == "Silva"
    assert result.phone == "1234567890"
    assert result.address == "123 Main Street"


def test_contact_is_saved_in_collection(service, collection, contact):
    service.add(contact)

    assert collection.find_one({"_id": "001"})["first_name"] == "Lucas"


def test_data_persists_across_service_instances(collection, contact):
    # A new service on the same collection should still see the contact,
    # which is the whole point of using a database
    MongoContactService(collection).add(contact)

    assert MongoContactService(collection).get("001").first_name == "Lucas"


def test_duplicate_contact_id(service, contact):
    service.add(contact)

    with pytest.raises(ValueError, match="already exists"):
        service.add(Contact("001", "John", "Doe", "0987654321", "456 New Street"))


def test_null_contact(service):
    with pytest.raises(ValueError):
        service.add(None)


def test_get_missing_contact(service):
    with pytest.raises(ValueError):
        service.get("999")


def test_get_rejects_query_objects(service, contact):
    service.add(contact)

    with pytest.raises(ValueError):
        service.get({"$ne": ""})


def test_delete_contact(service, contact):
    service.add(contact)

    service.delete("001")

    with pytest.raises(ValueError):
        service.get("001")


def test_delete_missing_contact(service):
    with pytest.raises(ValueError):
        service.delete("999")


def test_update_contact(service, contact):
    service.add(contact)

    service.update("001", first_name="John", last_name="Doe", phone="0987654321")

    result = service.get("001")
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.phone == "0987654321"
    assert result.address == "123 Main Street"


def test_update_with_invalid_value_is_not_saved(service, contact):
    service.add(contact)

    with pytest.raises(ValueError):
        service.update("001", phone="abc")

    assert service.get("001").phone == "1234567890"


def test_update_invalid_field(service, contact):
    service.add(contact)

    with pytest.raises(ValueError):
        service.update("001", email="test@test.com")


def test_update_cannot_skip_validation(service, contact):
    service.add(contact)

    with pytest.raises(ValueError):
        service.update("001", _phone="bad")


def test_update_missing_contact(service):
    with pytest.raises(ValueError):
        service.update("999", first_name="John")


# For the failure tests I use a MagicMock that raises the same error
# pymongo would raise if the server went down
@pytest.fixture
def broken_service():
    broken = MagicMock()
    error = ServerSelectionTimeoutError("server is down")
    broken.insert_one.side_effect = error
    broken.find_one.side_effect = error
    broken.delete_one.side_effect = error
    broken.update_one.side_effect = error
    return MongoContactService(broken)


def test_add_database_failure(broken_service, contact):
    with pytest.raises(DatabaseError):
        broken_service.add(contact)


def test_get_database_failure(broken_service):
    with pytest.raises(DatabaseError):
        broken_service.get("001")


def test_delete_database_failure(broken_service):
    with pytest.raises(DatabaseError):
        broken_service.delete("001")


def test_update_database_failure(contact):
    collection = MagicMock()
    collection.find_one.return_value = contact.to_document()
    collection.update_one.side_effect = ServerSelectionTimeoutError("server is down")

    with pytest.raises(DatabaseError):
        MongoContactService(collection).update("001", first_name="John")


def test_create_gives_automatic_ids(service):
    first = service.create("Lucas", "Silva", "1234567890", "123 Main Street")
    second = service.create("John", "Doe", "0987654321", "456 New Street")

    assert first.contact_id == "1"
    assert second.contact_id == "2"
    assert service.get("2").first_name == "John"


def test_ids_keep_counting_after_restart(collection):
    MongoContactService(collection).create("Lucas", "Silva", "1234567890", "123 Main St")

    # A brand new service should pick up where the last one left off
    contact = MongoContactService(collection).create("John", "Doe", "0987654321", "456 New St")

    assert contact.contact_id == "2"


def test_create_skips_ids_already_taken(service):
    service.add(Contact("1", "Lucas", "Silva", "1234567890", "123 Main Street"))

    contact = service.create("John", "Doe", "0987654321", "456 New Street")

    assert contact.contact_id == "2"


def test_create_invalid_input_saves_nothing(service, collection):
    with pytest.raises(ValueError):
        service.create("Lucas", "Silva", "bad phone", "123 Main Street")

    assert collection.count_documents({}) == 0


def test_create_counter_failure(contact):
    counters = MagicMock()
    counters.find_one_and_update.side_effect = ServerSelectionTimeoutError("server is down")

    with pytest.raises(DatabaseError):
        MongoContactService(MagicMock(), counters).create("Lucas", "Silva", "1234567890", "123 Main St")


def test_list_all_empty(service):
    assert service.list_all() == []


def test_list_all_sorted_by_id(service):
    # Making 11 contacts so there's a "10" and "11" to check they come after "2"
    for _ in range(11):
        service.create("Lucas", "Silva", "1234567890", "123 Main Street")

    ids = [contact.contact_id for contact in service.list_all()]

    assert ids == [str(number) for number in range(1, 12)]


def test_list_all_database_failure(broken_service):
    broken_service.collection.find.side_effect = ServerSelectionTimeoutError("server is down")

    with pytest.raises(DatabaseError):
        broken_service.list_all()
