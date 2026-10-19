package ContactService;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ContactServiceTest {

    private ContactService contactService;

    @BeforeEach
    public void setup() {
        contactService = new ContactService();
    }

    @Test
    public void testAddSingleContact() {
        Contact contact = new Contact("1234", "Lucas", "Silva", "1234567890", "123 First St");
        contactService.addContact(contact);
        assertInstanceOf(Contact.class, contactService.getContact("1234"));
    }

    @Test
    public void testAddDuplicateContactId() {
        Contact contact1 = new Contact("1234", "Lucas", "Silva", "1234567890", "123 First St");
        Contact contact2 = new Contact("1234", "John", "Doe", "7896543210", "123 Second St");
        contactService.addContact(contact1);
        assertThrows(IllegalArgumentException.class, () -> contactService.addContact(contact2));
    }

    @Test
    public void testAddMultipleContacts() {
        Contact contact1 = new Contact("1234", "Lucas", "Silva", "1234567890", "123 First St");
        Contact contact2 = new Contact("4567", "John", "Doe", "9876543210", "123 Second St");
        contactService.addContact(contact1);
        contactService.addContact(contact2);
        assertInstanceOf(Contact.class, contactService.getContact("1234"));
        assertInstanceOf(Contact.class, contactService.getContact("4567"));
    }

    @Test
    public void testAddNullContact() {
        assertThrows(IllegalArgumentException.class, () -> contactService.addContact(null));
    }

    @Test
    public void testRemoveContact() {
        Contact contact = new Contact("1234", "Lucas", "Silva", "1234567890", "123 First St");
        contactService.addContact(contact);
        contactService.deleteContact("1234");
        assertThrows(IllegalArgumentException.class, () -> contactService.getContact("1234"));
    }

    @Test
    public void testUpdateContact() {
        Contact contact = new Contact("1234", "Lucas", "Silva", "1234567890", "123 First St");
        contactService.addContact(contact);
        contactService.updateContactName("1234", "John", "Doe");
        contactService.updateContactPhone("1234", "9876543210");
        contactService.updateContactAddress("1234", "123 Second St");
        assertEquals("John", contactService.getContact("1234").getFirstName());
        assertEquals("Doe", contactService.getContact("1234").getLastName());
        assertEquals("9876543210", contactService.getContact("1234").getPhone());
        assertEquals("123 Second St", contactService.getContact("1234").getAddress());
    }

}