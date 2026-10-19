from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from .contact import Contact
from .errors import DatabaseError

# contact_id is left out on purpose since it's the key and shouldn't change
UPDATABLE_FIELDS = {"first_name", "last_name", "phone", "address"}


def check_fields(changes):
    for field in changes:
        if field not in UPDATABLE_FIELDS:
            raise ValueError(f"Invalid contact field: {field}")


def sort_by_id(contacts):
    # The IDs are strings, so a normal sort would put "10" before "2".
    # Sorting by length first fixes that for the numbered IDs.
    return sorted(contacts, key=lambda contact: (len(contact.contact_id), contact.contact_id))


class ContactService:
    """Manages contacts for the application (stored in memory)."""

    def __init__(self):
        self.contacts: dict[str, Contact] = {}
        self.last_id = 0

    def next_id(self):
        self.last_id += 1
        return str(self.last_id)

    def create(self, first_name, last_name, phone, address):
        """Creates a contact with an automatic ID and returns it."""
        # Building the contact with a placeholder ID first so bad input
        # gets rejected before an ID is used up
        contact = Contact("0", first_name, last_name, phone, address)

        # Skip over any IDs that are already taken (for example a contact
        # that was added by hand with add())
        while True:
            contact.contact_id = self.next_id()
            try:
                self.add(contact)
                return contact
            except ValueError as error:
                if "already exists" not in str(error):
                    raise

    def add(self, contact):
        """Adds a new contact."""
        if contact is None:
            raise ValueError("Contact cannot be None.")

        if contact.contact_id in self.contacts:
            raise ValueError("A contact with this ID already exists.")

        self.contacts[contact.contact_id] = contact

    def get(self, contact_id):
        """Returns a contact by ID."""
        try:
            return self.contacts[contact_id]
        except (KeyError, TypeError):
            raise ValueError("Contact with this ID does not exist")

    def delete(self, contact_id):
        """Deletes a contact by ID."""
        if contact_id not in self.contacts:
            raise ValueError("Contact with this ID does not exist")

        del self.contacts[contact_id]

    def list_all(self):
        """Returns every contact, sorted by ID."""
        return sort_by_id(self.contacts.values())

    def update(self, contact_id, **changes):
        """Updates the provided fields of an existing contact."""
        check_fields(changes)
        contact = self.get(contact_id)

        # Try the changes on a copy first so one bad value doesn't leave
        # the real contact half updated
        copy = Contact.from_document(contact.to_document())
        for field, value in changes.items():
            setattr(copy, field, value)

        for field, value in changes.items():
            setattr(contact, field, value)


class MongoContactService(ContactService):
    """Same as ContactService, but the contacts are saved in a MongoDB collection."""

    def __init__(self, collection, counters=None):
        self.collection = collection
        # The last used ID is kept in its own collection so it survives restarts
        self.counters = counters if counters is not None else collection.database["counters"]

    def next_id(self):
        # $inc is atomic, so two people adding at the same time never get the same ID
        try:
            counter = self.counters.find_one_and_update(
                {"_id": "contact_id"},
                {"$inc": {"value": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        except PyMongoError as error:
            raise DatabaseError(f"Could not create a contact ID: {error}") from error

        return str(counter["value"])

    def add(self, contact):
        if contact is None:
            raise ValueError("Contact cannot be None.")

        try:
            self.collection.insert_one(contact.to_document())
        except DuplicateKeyError:
            raise ValueError("A contact with this ID already exists.")
        except PyMongoError as error:
            raise DatabaseError(f"Could not save contact: {error}") from error

    def get(self, contact_id):
        # Only plain strings are allowed so nobody can sneak in a query
        # like {"$ne": ""} instead of an ID
        if not isinstance(contact_id, str):
            raise ValueError("Contact with this ID does not exist")

        try:
            document = self.collection.find_one({"_id": contact_id})
        except PyMongoError as error:
            raise DatabaseError(f"Could not load contact: {error}") from error

        if document is None:
            raise ValueError("Contact with this ID does not exist")

        return Contact.from_document(document)

    def list_all(self):
        try:
            documents = list(self.collection.find())
        except PyMongoError as error:
            raise DatabaseError(f"Could not load contacts: {error}") from error

        return sort_by_id(Contact.from_document(document) for document in documents)

    def delete(self, contact_id):
        if not isinstance(contact_id, str):
            raise ValueError("Contact with this ID does not exist")

        try:
            result = self.collection.delete_one({"_id": contact_id})
        except PyMongoError as error:
            raise DatabaseError(f"Could not delete contact: {error}") from error

        if result.deleted_count == 0:
            raise ValueError("Contact with this ID does not exist")

    def update(self, contact_id, **changes):
        check_fields(changes)
        contact = self.get(contact_id)

        # The Contact setters do the validation, so nothing invalid
        # gets written to the database
        for field, value in changes.items():
            setattr(contact, field, value)

        new_values = {field: getattr(contact, field) for field in changes}

        try:
            self.collection.update_one({"_id": contact_id}, {"$set": new_values})
        except PyMongoError as error:
            raise DatabaseError(f"Could not update contact: {error}") from error
