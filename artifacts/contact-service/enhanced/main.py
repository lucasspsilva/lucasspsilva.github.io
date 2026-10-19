from getpass import getpass

from contacts.auth import ROLE_PERMISSIONS, SecureContactService, UserService
from contacts.contact_service import MongoContactService
from contacts.database import get_database
from contacts.errors import AuthenticationError, DatabaseError

# These are the errors a user can cause, so the menu just prints them
# instead of crashing the program
USER_ERRORS = (ValueError, PermissionError, DatabaseError)


def display_menu(user):
    """Displays the available contact service options."""
    print("\n==============================")
    print("       CONTACT SERVICE")
    print("==============================")
    print(f"Logged in as {user.username} ({user.role})")
    print("1. Add contact")
    print("2. View contact")
    print("3. List all contacts")
    print("4. Update contact")
    print("5. Delete contact")
    print("6. Add user (admin only)")
    print("7. Exit")


def add_contact(service):
    """Gets contact information from the user and adds a contact."""
    print("\n--- Add Contact ---")

    # Same idea as update: tell a viewer right away instead of after
    # they type everything in
    if not service.user.can("add"):
        print("Error: You are not allowed to add contacts.")
        return

    first_name = input("First name: ")
    last_name = input("Last name: ")
    phone = input("Phone: ")
    address = input("Address: ")

    try:
        # The ID is picked automatically by the service
        contact = service.create(first_name, last_name, phone, address)
        print(f"Contact added successfully. Contact ID: {contact.contact_id}")

    except USER_ERRORS as error:
        print(f"Error: {error}")


def view_contact(service):
    """Displays a contact using its ID."""
    print("\n--- View Contact ---")

    contact_id = input("Contact ID: ")

    try:
        contact = service.get(contact_id)

        print("\nContact Information")
        print(f"ID: {contact.contact_id}")
        print(f"First name: {contact.first_name}")
        print(f"Last name: {contact.last_name}")
        print(f"Phone: {contact.phone}")
        print(f"Address: {contact.address}")

    except USER_ERRORS as error:
        print(f"Error: {error}")


def list_contacts(service):
    """Displays every contact in a simple table."""
    print("\n--- All Contacts ---")

    try:
        contacts = service.list_all()
    except USER_ERRORS as error:
        print(f"Error: {error}")
        return

    if not contacts:
        print("No contacts yet.")
        return

    # The widths match the max lengths from the Contact rules
    # (10 for names and phone, 30 for address) so the columns line up
    print(f"{'ID':<10} {'First':<10} {'Last':<10} {'Phone':<10} Address")
    print("-" * 72)
    for contact in contacts:
        print(
            f"{contact.contact_id:<10} {contact.first_name:<10} "
            f"{contact.last_name:<10} {contact.phone:<10} {contact.address}"
        )

    print(f"\n{len(contacts)} contact(s) total.")


def update_contact(service):
    """Updates information for an existing contact."""
    print("\n--- Update Contact ---")

    contact_id = input("Contact ID: ")

    try:
        # Checking the permission up front so a viewer isn't asked for
        # new values just to get denied at the end
        if not service.user.can("update"):
            raise PermissionError("You are not allowed to update contacts")

        service.get(contact_id)

        print("\nWhat would you like to update?")
        print("1. Name")
        print("2. Phone")
        print("3. Address")

        choice = input("Select an option: ")

        if choice == "1":
            first_name = input("First name: ")
            last_name = input("Last name: ")

            service.update(
                contact_id,
                first_name=first_name,
                last_name=last_name
            )

        elif choice == "2":
            phone = input("Phone: ")
            service.update(contact_id, phone=phone)

        elif choice == "3":
            address = input("Address: ")
            service.update(contact_id, address=address)

        else:
            print("Invalid option.")
            return

        print("Contact updated successfully.")

    except USER_ERRORS as error:
        print(f"Error: {error}")


def delete_contact(service):
    """Deletes a contact using its ID."""
    print("\n--- Delete Contact ---")

    contact_id = input("Contact ID: ")

    try:
        service.delete(contact_id)
        print("Contact deleted successfully.")

    except USER_ERRORS as error:
        print(f"Error: {error}")


def add_user(users, current_user):
    """Lets an admin create a new user account."""
    print("\n--- Add User ---")

    if not current_user.can("manage_users"):
        print("Error: Only admins can add users.")
        return

    username = input("Username: ")
    password = getpass("Password: ")
    role = input(f"Role ({', '.join(ROLE_PERMISSIONS)}): ").strip().lower()

    try:
        users.register(username, password, role)
        print("User added successfully.")

    except USER_ERRORS as error:
        print(f"Error: {error}")


def create_first_admin(users):
    """Makes the first admin account when the database has no users yet."""
    print("\nNo users found. Let's create the first admin account.")

    while True:
        username = input("Admin username: ")
        password = getpass("Admin password: ")

        try:
            return users.register(username, password, "admin")
        except ValueError as error:
            print(f"Error: {error}")


def log_in(users):
    """Asks for a username and password, with a few attempts allowed."""
    for _ in range(3):
        username = input("\nUsername: ")
        password = getpass("Password: ")

        try:
            return users.login(username, password)
        except AuthenticationError as error:
            print(f"Error: {error}")

    print("Too many failed attempts.")
    return None


def main():
    """Runs the contact service application."""
    try:
        database = get_database()
        users = UserService(database["users"])

        user = log_in(users) if users.has_users() else create_first_admin(users)

    except DatabaseError as error:
        print(f"Error: {error}")
        return

    if user is None:
        return

    # Every contact action goes through the permission check for this user
    service = SecureContactService(MongoContactService(database["contacts"]), user)

    while True:
        display_menu(user)

        choice = input("Select an option: ")

        if choice == "1":
            add_contact(service)

        elif choice == "2":
            view_contact(service)

        elif choice == "3":
            list_contacts(service)

        elif choice == "4":
            update_contact(service)

        elif choice == "5":
            delete_contact(service)

        elif choice == "6":
            add_user(users, user)

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    # Ctrl+C or a closed input shouldn't dump a traceback on the user
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
