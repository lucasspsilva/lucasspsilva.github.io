# Contact Service

This started out as my final project for CS 320, a contact manager written in Java. For CS 499 I've been reworking it. In the first enhancement I rewrote it in Python, and in the second one I moved the storage over to MongoDB and added user logins.

## The original project

The CS 320 version let you add, update, look up, and delete contacts. Each contact has:

- a contact ID
- a first name
- a last name
- a phone number
- an address

There were rules for every field. The ID and both names can't be empty or longer than 10 characters, the phone number has to be exactly 10 digits, and the address can't be empty or longer than 30 characters. I kept all of those rules in both enhancements.

## Enhancement 1: Java to Python

I didn't want to just translate the Java code line by line, so I rewrote it the way you'd normally write it in Python. There's a `Contact` class and a `ContactService` class, and the contacts are kept in a dictionary. I also added a menu so you can actually use it from the terminal. Bad input or a duplicate ID gives you an error message instead of crashing the program, and I redid the tests in pytest.

## Enhancement 2: MongoDB

The biggest problem with the first version was that everything disappeared as soon as you closed the program. So for this enhancement I swapped the dictionary out for a MongoDB database.

Contacts are saved in a `contacts` collection, and the contact ID is used as the document's `_id`. That means MongoDB refuses duplicate IDs on its own, so I don't have to check for them separately.

You don't type in IDs anymore, either. New contacts just get the next number (1, 2, 3, and so on). The last number used is saved in a `counters` collection, so the numbering picks up where it left off after a restart. The increment happens in one atomic step, so two people adding a contact at the same time can't end up with the same ID. I did think about using MongoDB's built-in ObjectId instead, but those are 24 characters long and the original rules only allow 10. They'd also be really annoying to type into a menu. MongoDB doesn't have an auto-increment like SQL does, so a counter document is the usual workaround.

Since the data sticks around now, it made sense to add logins. Users are saved in a `users` collection. Passwords are never stored as plain text. They're hashed with PBKDF2-SHA256 and a random salt using Python's built-in `hashlib`, so I didn't need an extra package for it. Every user has one of three roles:

| Role   | Add | View | Update | Delete | Add users |
|--------|-----|------|--------|--------|-----------|
| admin  | yes | yes  | yes    | yes    | yes       |
| editor | yes | yes  | yes    | no     | no        |
| viewer | no  | yes  | no     | no     | no        |

I also tightened up a few other things:

- Every field has to be an actual string and follow the CS 320 rules. This matters a lot more now that there's a database behind it. If someone passed something like `{"$ne": ""}` as an ID, it could turn into a query injection, so only plain strings ever get sent to the database.
- Updates can only change the name, phone number, and address. The ID can't be changed.
- If MongoDB is down or a query fails, you get a short error message instead of a stack trace.
- The connection string goes in a `.env` file that's kept out of git, so no credentials end up in the code.

While I was working on this I also found a few bugs in my old Python code. `main.py` couldn't even run because its imports were wrong. The tests imported everything correctly, so I never noticed. And `update()` would let you write straight to a private attribute like `_phone`, which skipped the validation completely. Both of those are fixed now. Updates are also all-or-nothing, so a bad phone number won't leave a contact half updated.

The original in-memory `ContactService` is still there and works exactly like it did before. `MongoContactService` has the same methods, so the rest of the code works with either one.

## Project structure

```
Refactored/
├── contacts/
│   ├── __init__.py
│   ├── auth.py               # users, password hashing, roles
│   ├── contact.py
│   ├── contact_service.py    # in-memory and MongoDB services
│   ├── database.py           # MongoDB connection from .env
│   └── errors.py
├── tests/
│   ├── test_auth.py
│   ├── test_contact.py
│   ├── test_contact_service.py
│   ├── test_database.py
│   └── test_mongo_contact_service.py
├── .env.example
├── main.py
└── requirements.txt
```

## What you need

- Python 3.14 or newer (I built and tested it on 3.14)
- MongoDB. A local install of MongoDB Community Server works, and so does a free MongoDB Atlas cluster.
- The packages in `requirements.txt`: pymongo, python-dotenv, pytest, and mongomock

## Setting it up

1. If you don't have Python yet, download it from python.org. You can check that it's installed with:

   ```
   python --version
   ```

2. Open a terminal in the project folder:

   ```
   cd path/to/Refactored
   ```

3. Create a virtual environment so the packages don't mix with your other Python projects:

   ```
   python -m venv .venv
   ```

   Then activate it. In PowerShell:

   ```
   .venv\Scripts\Activate.ps1
   ```

   In Command Prompt:

   ```
   .venv\Scripts\activate
   ```

   On macOS or Linux:

   ```
   source .venv/bin/activate
   ```

   You'll see `(.venv)` at the start of the prompt once it's active.

4. Install the packages:

   ```
   pip install -r requirements.txt
   ```

5. Get MongoDB running. You can install Community Server locally (it runs on `localhost:27017` by default), or you can create a free cluster on Atlas and copy its connection string.

6. Make your own `.env` file from the example. On Windows:

   ```
   copy .env.example .env
   ```

   On macOS or Linux:

   ```
   cp .env.example .env
   ```

   Then open `.env` and fill it in. `MONGO_URI` is the only one you have to set. `MONGO_DB_NAME` defaults to `contact_service`, and `MONGO_TIMEOUT_MS` (how long to wait for the server before giving up) defaults to 5000. If you set any of these as regular environment variables, those win over the `.env` file.

## Running it

From the project folder:

```
python main.py
```

The first time you run it on an empty database, it asks you to create an admin account. After that you log in with your username and password, and you get 3 tries.

From the menu you can add, view, update, and delete contacts, list all of them in a table sorted by ID, and add new users if you're an admin. When you add a contact, it tells you which ID it got.

If it can't connect to MongoDB, it'll tell you and close instead of crashing.

## Running the tests

With the virtual environment active, run this from the project folder:

```
python -m pytest
```

You don't need MongoDB running for the tests. They use mongomock, which fakes a MongoDB database in memory, and `unittest.mock` to pretend the server is down.

Here's what each test file covers:

- `test_contact.py` checks the `Contact` class and its validation rules.
- `test_contact_service.py` covers the original in-memory `ContactService`: adding, getting, updating, and deleting contacts, plus rejecting duplicate IDs.
- `test_mongo_contact_service.py` covers the same things for the MongoDB version. It also tests automatic IDs (including after a restart), listing contacts, injection attempts, and what happens when the database fails.
- `test_auth.py` covers registering users, logging in, password hashing, and what each role is allowed to do.
- `test_database.py` checks the connection settings and what happens when the server can't be reached.

If everything's set up right, all the tests should pass.

## Why this is in my CS 499 portfolio

What I really wanted to show with this artifact is that I can go back to something I already built, figure out what's wrong or missing, and improve it without breaking what it was supposed to do. Along the way it also shows object-oriented programming in Python, working with a database, writing tests, handling errors, and some basic security.
