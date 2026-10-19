from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId


class AnimalShelter:
    def __init__(self, username=None, password=None, host="localhost", port=27017):
        "Initialize the mongo connection"

        USER = username
        PASS = password
        HOST = host
        PORT = port
        DB = "aac"
        COL = "animals"

        # My local MongoDB does not use a username and password, so we only
        # add them to the connection string if they were passed in
        if USER and PASS:
            uri = f"mongodb://{USER}:{PASS}@{HOST}:{PORT}/"
        else:
            uri = f"mongodb://{HOST}:{PORT}/"
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.database = self.client[DB]
        self.collection = self.database[COL]
        
    def create(self, data):
        """
        Inserts data into the database

        Parameters
        ----------
        data : Dict
        """
        if data is None:
            raise Exception("Nothing to save, because data parameter is empty")

        # Ensures that our data is a dictionary
        if not isinstance(data, dict):
            raise Exception("Data parameter must be a dict")

        inserted_data = self.database.animals.insert_one(data)
        # Return the data just in case we need to work with the cursor
        return inserted_data

    def read(self, data):
        """
        Reads data from the database

        Parameters
        ----------
        data : Dict
        """
        if data is None:
            raise Exception("Nothing to read, because data parameter is empty")

        # Ensures that our data is a dictionary
        if not isinstance(data, dict):
            raise Exception("Data parameter must be a dict")

        result = list(self.database.animals.find(data))
        # Return the data so we can work with the cursor on whatever function we use it afterwards
        return result

    def update(self, data, update_data, many=False):
        """
        Updates document(s) in the database.

        Parameters
        ----------
        data : Dict
            The filter used to match documents to update.
        update_data : Dict
            The fields to update or a valid MongoDB update document.
        many : bool
            If True, updates all matching documents; otherwise updates one. Defaults to False.
        """
        if data is None:
            raise Exception(
                "Nothing to update, because filter (data) parameter is empty"
            )
        if update_data is None:
            raise Exception("Nothing to update, because update_data parameter is empty")

        if not isinstance(data, dict):
            raise Exception("Filter (data) parameter must be a dict")
        if not isinstance(update_data, dict):
            raise Exception("update_data parameter must be a dict")

        # If no update operator is provided, assume a $set update
        has_operator = any(k.startswith("$") for k in update_data.keys())
        update_doc = update_data if has_operator else {"$set": update_data}

        if many:
            result = self.database.animals.update_many(data, update_doc)
        else:
            result = self.database.animals.update_one(data, update_doc)
        return result

    def delete(self, data, many=False):
        """
        Deletes document(s) from the database.

        Parameters
        ----------
        data : Dict
            The filter used to match documents to delete.
        many : bool
            If True, deletes all matching documents; otherwise deletes one. Defaults to False.
        """
        if data is None:
            raise Exception(
                "Nothing to delete, because filter (data) parameter is empty"
            )
        if not isinstance(data, dict):
            raise Exception("Filter (data) parameter must be a dict")

        if many:
            result = self.database.animals.delete_many(data)
        else:
            result = self.database.animals.delete_one(data)
        return result
