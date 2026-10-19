class DatabaseError(Exception):
    """Raised when something goes wrong talking to MongoDB."""


class AuthenticationError(Exception):
    """Raised when a username or password is wrong."""
