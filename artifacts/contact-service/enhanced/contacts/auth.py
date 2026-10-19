import hashlib
import hmac
import re
import secrets

from pymongo.errors import DuplicateKeyError, PyMongoError

from .errors import AuthenticationError, DatabaseError

# What each role is allowed to do with contacts
ROLE_PERMISSIONS = {
    "admin": {"add", "view", "update", "delete", "manage_users"},
    "editor": {"add", "view", "update"},
    "viewer": {"view"},
}

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,20}$")
MIN_PASSWORD_LENGTH = 8
HASH_ITERATIONS = 600_000


def hash_password(password, salt=None):
    """Hashes a password with PBKDF2 so the real password is never stored."""
    # A random salt means two users with the same password still get different hashes
    if salt is None:
        salt = secrets.token_bytes(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, HASH_ITERATIONS)
    return salt.hex(), hashed.hex()


def verify_password(password, salt_hex, hash_hex):
    _, new_hash = hash_password(password, bytes.fromhex(salt_hex))
    # compare_digest takes the same time no matter where the strings differ,
    # so it doesn't leak hints about the hash
    return hmac.compare_digest(new_hash, hash_hex)


class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

    def can(self, action):
        return action in ROLE_PERMISSIONS.get(self.role, set())


class UserService:
    """Handles registering and logging in users stored in MongoDB."""

    def __init__(self, collection):
        self.collection = collection

    def has_users(self):
        try:
            return self.collection.find_one({}) is not None
        except PyMongoError as error:
            raise DatabaseError(f"Could not read users: {error}") from error

    def register(self, username, password, role="viewer"):
        if not isinstance(username, str) or not USERNAME_PATTERN.match(username):
            raise ValueError("Username must be 3-20 letters, numbers, or underscores")
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
        if role not in ROLE_PERMISSIONS:
            raise ValueError(f"Role must be one of: {', '.join(ROLE_PERMISSIONS)}")

        salt, hashed = hash_password(password)

        try:
            self.collection.insert_one(
                {"_id": username, "salt": salt, "password_hash": hashed, "role": role}
            )
        except DuplicateKeyError:
            raise ValueError("That username is already taken")
        except PyMongoError as error:
            raise DatabaseError(f"Could not save user: {error}") from error

        return User(username, role)

    def login(self, username, password):
        if not isinstance(username, str) or not isinstance(password, str):
            raise AuthenticationError("Invalid username or password")

        try:
            document = self.collection.find_one({"_id": username})
        except PyMongoError as error:
            raise DatabaseError(f"Could not read users: {error}") from error

        # Same message for a wrong username and a wrong password so nobody
        # can use the login to figure out which usernames exist
        if document is None or not verify_password(
            password, document["salt"], document["password_hash"]
        ):
            raise AuthenticationError("Invalid username or password")

        return User(document["_id"], document["role"])


class SecureContactService:
    """Wraps a contact service and checks the user's role before every action."""

    def __init__(self, service, user):
        self.service = service
        self.user = user

    def _require(self, action):
        if not self.user.can(action):
            raise PermissionError(
                f"User '{self.user.username}' ({self.user.role}) is not allowed to {action} contacts"
            )

    def create(self, first_name, last_name, phone, address):
        self._require("add")
        return self.service.create(first_name, last_name, phone, address)

    def add(self, contact):
        self._require("add")
        self.service.add(contact)

    def get(self, contact_id):
        self._require("view")
        return self.service.get(contact_id)

    def list_all(self):
        self._require("view")
        return self.service.list_all()

    def update(self, contact_id, **changes):
        self._require("update")
        self.service.update(contact_id, **changes)

    def delete(self, contact_id):
        self._require("delete")
        self.service.delete(contact_id)
