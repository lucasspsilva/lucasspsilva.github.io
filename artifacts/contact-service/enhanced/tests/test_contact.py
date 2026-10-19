import pytest
from contacts.contact import Contact


def test_contact_creation():
    contact = Contact(
        "001",
        "Lucas",
        "Silva",
        "1234567890",
        "123 Main Street"
    )

    assert contact.contact_id == "001"
    assert contact.first_name == "Lucas"
    assert contact.last_name == "Silva"
    assert contact.phone == "1234567890"
    assert contact.address == "123 Main Street"


def test_invalid_contact_id():
    with pytest.raises(ValueError):
        Contact(
            "12345678901",
            "Lucas",
            "Silva",
            "1234567890",
            "123 Main Street"
        )


def test_invalid_first_name():
    with pytest.raises(ValueError):
        Contact(
            "001",
            "Lucas123456",
            "Silva",
            "1234567890",
            "123 Main Street"
        )


def test_invalid_last_name():
    with pytest.raises(ValueError):
        Contact(
            "001",
            "Lucas",
            "Silva123456",
            "1234567890",
            "123 Main Street"
        )


def test_invalid_phone():
    with pytest.raises(ValueError):
        Contact(
            "001",
            "Lucas",
            "Silva",
            "123",
            "123 Main Street"
        )


def test_invalid_address():
    with pytest.raises(ValueError):
        Contact(
            "001",
            "Lucas",
            "Silva",
            "1234567890",
            "A" * 31
        )

@pytest.mark.parametrize("bad_value", [None, "", 1234567890])
def test_non_string_or_empty_values(bad_value):
    with pytest.raises(ValueError):
        Contact(bad_value, "Lucas", "Silva", "1234567890", "123 Main Street")
    with pytest.raises(ValueError):
        Contact("001", "Lucas", "Silva", bad_value, "123 Main Street")


def test_phone_with_letters():
    with pytest.raises(ValueError):
        Contact("001", "Lucas", "Silva", "12345abcde", "123 Main Street")


def test_document_round_trip():
    contact = Contact("001", "Lucas", "Silva", "1234567890", "123 Main Street")

    copy = Contact.from_document(contact.to_document())

    assert copy.to_document() == contact.to_document()
