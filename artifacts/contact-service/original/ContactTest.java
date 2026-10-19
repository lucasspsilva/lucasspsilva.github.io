package ContactService;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class ContactTest {

    @Test
    public void testContactCreation() {
        Contact contact = new Contact("1234", "Lucas", "Silva", "1234567890", "123 First St");
        assertEquals("1234", contact.getContactId());
        assertEquals("Lucas", contact.getFirstName());
        assertEquals("Silva", contact.getLastName());
        assertEquals("1234567890", contact.getPhone());
        assertEquals("123 First St", contact.getAddress());
    }

    @Test
    public void testContactUpdate() {
        Contact contact = new Contact("1234", "Lucas", "Silva", "1234567890", "123 First St");
        contact.setFirstName("John");
        contact.setLastName("Doe");
        contact.setPhone("9874563210");
        contact.setAddress("123 Second St");
        assertEquals("John", contact.getFirstName());
        assertEquals("Doe", contact.getLastName());
        assertEquals("9874563210", contact.getPhone());
        assertEquals("123 Second St", contact.getAddress());
    }

    @Test
    public void testContactInvalidId() {
        // Null
        assertThrows(IllegalArgumentException.class, () -> new Contact(null, "Lucas", "Silva", "1234567890", "123 First St"));
        // Over 10 chars
        assertThrows(IllegalArgumentException.class, () -> new Contact("1234567890123", "Lucas", "Silva", "1234567890", "123 First St"));
    }

    @Test
    public void testContactInvalidFirstName() {
        // Null
        assertThrows(IllegalArgumentException.class, () -> new Contact("1234", null, "Silva", "1234567890", "123 First St"));
        // Over 10 chars
        assertThrows(IllegalArgumentException.class, () -> new Contact("1234", "12345678901023", "Silva", "1234567890", "123 First St"));
    }

    @Test
    public void testContactInvalidLastName() {
        // Null
        assertThrows(IllegalArgumentException.class, () -> new Contact("1234", "Lucas", null, "1234567890", "123 First St"));
        // Over 10 chars
        assertThrows(IllegalArgumentException.class, () -> new Contact("1234", "Lucas", "1234567890123", "1234567890", "123 First St"));
    }

    @Test
    public void testContactInvalidPhone() {
        // Null
        assertThrows(IllegalArgumentException.class, () -> new Contact("1234", "Lucas", "Silva", null, "123 First St"));
        // Over 10 digits
        assertThrows(IllegalArgumentException.class, () -> new Contact("1234", "Lucas", "Silva", "1234567890123456", "123 First St"));
        // Not a phone number
        assertThrows(IllegalArgumentException.class, () -> new Contact("1234", "Lucas", "Silva", "PhoneNumb", "123 First St"));
    }

    @Test
    public void testContactInvalidAddress() {
        // Null
        assertThrows(IllegalArgumentException.class, () -> new Contact("1234", "Lucas", "Silva", "1234567890", null));
        // Over 30 chars
        assertThrows(IllegalArgumentException.class, () -> new Contact("1234", "Lucas", "Silva", "1234567890", "123456789012345678901234567890123"));
    }
}