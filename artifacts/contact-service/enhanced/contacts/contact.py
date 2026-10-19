class Contact:
    """Represents a contact and validates its information."""

    def __init__(self, contact_id, first_name, last_name, phone, address):
        self.contact_id = contact_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.address = address

    @property
    def contact_id(self):
        return self._contact_id

    @contact_id.setter
    def contact_id(self, value):
        # Checking the type first so things like None or a dict never make it
        # into a database query
        if not isinstance(value, str) or not value or len(value) > 10:
            raise ValueError("Contact ID cannot be empty or longer than 10 characters")
        self._contact_id = value

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        if not isinstance(value, str) or not value or len(value) > 10:
            raise ValueError(
                "First name cannot be empty or longer than 10 characters"
            )
        self._first_name = value

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        if not isinstance(value, str) or not value or len(value) > 10:
            raise ValueError(
                "Last name cannot be empty or longer than 10 characters"
            )
        self._last_name = value

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        # isdecimal instead of isdigit so characters like "²" don't count as numbers
        if not isinstance(value, str) or not value.isdecimal() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits")
        self._phone = value

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        if not isinstance(value, str) or not value or len(value) > 30:
            raise ValueError(
                "Address cannot be empty or longer than 30 characters"
            )
        self._address = value

    def to_document(self):
        """Turns the contact into a dictionary MongoDB can store."""
        # The contact ID is used as the Mongo _id, so the database itself
        # blocks duplicate IDs
        return {
            "_id": self.contact_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "address": self.address,
        }

    @classmethod
    def from_document(cls, document):
        """Builds a Contact back from a MongoDB document."""
        return cls(
            document["_id"],
            document["first_name"],
            document["last_name"],
            document["phone"],
            document["address"],
        )
