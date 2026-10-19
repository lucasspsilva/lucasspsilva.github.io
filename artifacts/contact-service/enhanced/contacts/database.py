import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from .errors import DatabaseError


def get_database():
    """Connects to MongoDB using the settings in the environment or .env file."""
    # Loading the .env file here keeps the connection string out of the code
    load_dotenv()

    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME", "contact_service")

    if not uri:
        raise DatabaseError("MONGO_URI is not set. Copy .env.example to .env and fill it in.")

    try:
        timeout = int(os.getenv("MONGO_TIMEOUT_MS", "5000"))
        client = MongoClient(uri, serverSelectionTimeoutMS=timeout)
        # MongoClient connects lazily, so I ping it to find out right away
        # if the server is down instead of failing later in the menu
        client.admin.command("ping")
    except (PyMongoError, ValueError) as error:
        raise DatabaseError(f"Could not connect to MongoDB: {error}") from error

    return client[db_name]
