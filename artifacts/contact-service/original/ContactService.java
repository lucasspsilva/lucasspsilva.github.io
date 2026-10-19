package ContactService;

import java.util.HashMap;
import java.util.Map;

public class ContactService {
    private final Map<String, Contact> contactMap = new HashMap<>();

    public void addContact(Contact contact) {
        if (contact == null) {
            throw new IllegalArgumentException("Contact cannot be null");
        }
        if (contactMap.containsKey(contact.getContactId())) {
            throw new IllegalArgumentException("Contact with this ID already exists");
        }
        contactMap.put(contact.getContactId(), contact);
    }

    public Contact getContact(String contactId) {
        Contact contact = contactMap.get(contactId);
        if (contact == null) {
            throw new IllegalArgumentException("Contact with this ID does not exist");
        }
        return contact;
    }

    public void deleteContact(String contactId) {
        Contact contact = getContact(contactId);
        contactMap.remove(contact.getContactId());
    }

    public void updateContactName(String contactId, String firstName, String lastName) {
        Contact contact = getContact(contactId);
        contact.setFirstName(firstName);
        contact.setLastName(lastName);
    }

    public void updateContactPhone(String contactId, String phoneNumber) {
        Contact contact = getContact(contactId);
        contact.setPhone(phoneNumber);
    }

    public void updateContactAddress(String contactId, String address) {
        Contact contact = getContact(contactId);
        contact.setAddress(address);
    }
}
