from unittest.mock import MagicMock

import mongomock
import pytest
from pymongo.errors import ServerSelectionTimeoutError

from contacts.auth import SecureContactService, User, UserService
from contacts.contact import Contact
from contacts.contact_service import ContactService
from contacts.errors import AuthenticationError, DatabaseError


@pytest.fixture
def users():
    return UserService(mongomock.MongoClient().db.users)


@pytest.fixture
def contact():
    return Contact("001", "Lucas", "Silva", "1234567890", "123 Main Street")


def test_register_and_login(users):
    users.register("lucas", "password123", "admin")

    user = users.login("lucas", "password123")

    assert user.username == "lucas"
    assert user.role == "admin"


def test_password_is_not_stored_in_plain_text(users):
    users.register("lucas", "password123")

    stored = users.collection.find_one({"_id": "lucas"})

    assert "password123" not in stored.values()
    assert stored["password_hash"] != "password123"


def test_wrong_password(users):
    users.register("lucas", "password123")

    with pytest.raises(AuthenticationError):
        users.login("lucas", "wrongpass1")


def test_unknown_user(users):
    with pytest.raises(AuthenticationError):
        users.login("nobody", "password123")


def test_login_rejects_query_objects(users):
    users.register("lucas", "password123")

    with pytest.raises(AuthenticationError):
        users.login({"$ne": ""}, "password123")


def test_duplicate_username(users):
    users.register("lucas", "password123")

    with pytest.raises(ValueError):
        users.register("lucas", "otherpass123")


@pytest.mark.parametrize("username", ["", "ab", "has space", "a" * 21, None])
def test_invalid_username(users, username):
    with pytest.raises(ValueError):
        users.register(username, "password123")


def test_short_password(users):
    with pytest.raises(ValueError):
        users.register("lucas", "short")


def test_invalid_role(users):
    with pytest.raises(ValueError):
        users.register("lucas", "password123", "superuser")


def test_has_users(users):
    assert not users.has_users()

    users.register("lucas", "password123")

    assert users.has_users()


def test_login_database_failure():
    collection = MagicMock()
    collection.find_one.side_effect = ServerSelectionTimeoutError("server is down")

    with pytest.raises(DatabaseError):
        UserService(collection).login("lucas", "password123")


def test_admin_can_do_everything(contact):
    service = SecureContactService(ContactService(), User("boss", "admin"))

    service.add(contact)
    service.update("001", phone="0987654321")
    assert service.get("001").phone == "0987654321"
    service.delete("001")


def test_editor_cannot_delete(contact):
    service = SecureContactService(ContactService(), User("ed", "editor"))

    service.add(contact)
    service.update("001", phone="0987654321")

    with pytest.raises(PermissionError):
        service.delete("001")


def test_viewer_can_only_view(contact):
    inner = ContactService()
    inner.add(contact)
    service = SecureContactService(inner, User("viewer1", "viewer"))

    assert service.get("001").first_name == "Lucas"

    with pytest.raises(PermissionError):
        service.add(Contact("002", "John", "Doe", "0987654321", "456 New Street"))
    with pytest.raises(PermissionError):
        service.update("001", phone="0987654321")
    with pytest.raises(PermissionError):
        service.delete("001")

    # Make sure the denied actions really didn't change anything
    assert inner.get("001").phone == "1234567890"


def test_unknown_role_has_no_permissions(contact):
    service = SecureContactService(ContactService(), User("someone", "hacker"))

    with pytest.raises(PermissionError):
        service.get("001")


def test_viewer_cannot_create():
    service = SecureContactService(ContactService(), User("viewer1", "viewer"))

    with pytest.raises(PermissionError):
        service.create("Lucas", "Silva", "1234567890", "123 Main Street")


def test_editor_can_create():
    service = SecureContactService(ContactService(), User("ed", "editor"))

    contact = service.create("Lucas", "Silva", "1234567890", "123 Main Street")

    assert service.get(contact.contact_id).first_name == "Lucas"


def test_viewer_can_list(contact):
    inner = ContactService()
    inner.add(contact)
    service = SecureContactService(inner, User("viewer1", "viewer"))

    assert [c.contact_id for c in service.list_all()] == ["001"]


def test_unknown_role_cannot_list():
    service = SecureContactService(ContactService(), User("someone", "hacker"))

    with pytest.raises(PermissionError):
        service.list_all()
