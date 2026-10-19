import pytest

from contacts.contact import Contact
from contacts.contact_service import ContactService


@pytest.fixture
def service():
    return ContactService()


@pytest.fixture
def contact():
    return Contact(
        "001",
        "Lucas",
        "Silva",
        "1234567890",
        "123 Main Street"
    )


def test_add_contact(service, contact):
    service.add(contact)

    result = service.get("001")

    assert result is contact


def test_duplicate_contact_id(service, contact):
    service.add(contact)

    with pytest.raises(ValueError):
        service.add(contact)


def test_multiple_contacts(service):
    contact_one = Contact(
        "001",
        "Lucas",
        "Silva",
        "1234567890",
        "123 Main Street"
    )

    contact_two = Contact(
        "002",
        "John",
        "Doe",
        "0987654321",
        "456 New Street"
    )

    service.add(contact_one)
    service.add(contact_two)

    assert service.get("001") is contact_one
    assert service.get("002") is contact_two


def test_null_contact(service):
    with pytest.raises(ValueError):
        service.add(None)


def test_delete_contact(service, contact):
    service.add(contact)

    service.delete("001")

    with pytest.raises(ValueError):
        service.get("001")


def test_update_name(service, contact):
    service.add(contact)

    service.update(
        "001",
        first_name="John",
        last_name="Doe"
    )

    updated_contact = service.get("001")

    assert updated_contact.first_name == "John"
    assert updated_contact.last_name == "Doe"


def test_update_phone(service, contact):
    service.add(contact)

    service.update(
        "001",
        phone="0987654321"
    )

    assert service.get("001").phone == "0987654321"


def test_update_address(service, contact):
    service.add(contact)

    service.update(
        "001",
        address="456 New Street"
    )

    assert service.get("001").address == "456 New Street"

def test_update_invalid_value_leaves_contact_unchanged(service, contact):
    service.add(contact)

    with pytest.raises(ValueError):
        service.update("001", first_name="John", phone="bad")

    assert service.get("001").first_name == "Lucas"


def test_update_invalid_field(service, contact):
    service.add(contact)

    with pytest.raises(ValueError):
        service.update("001", _phone="bad")


def test_create_gives_automatic_ids(service):
    first = service.create("Lucas", "Silva", "1234567890", "123 Main Street")
    second = service.create("John", "Doe", "0987654321", "456 New Street")

    assert first.contact_id == "1"
    assert second.contact_id == "2"
    assert service.get("1") is first


def test_list_all(service):
    assert service.list_all() == []

    first = service.create("Lucas", "Silva", "1234567890", "123 Main Street")
    second = service.create("John", "Doe", "0987654321", "456 New Street")

    assert service.list_all() == [first, second]
