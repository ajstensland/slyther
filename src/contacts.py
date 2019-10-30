import json
from os.path import exists
from os import makedirs
from src.ui import *
from src.socks import encrypt_aes, encrypt_rsa, decrypt_aes, decrypt_rsa
from Crypto.Random import get_random_bytes

CONTACTS_DIR = "data/contacts/"
CONTACTS_PATH = "data/contacts/contacts.json"

def load_contacts(private):
    """
    Decrypts and loads the contacts dictionary from the CONTACTS_PATH.

    Args:
        private: The user's private RSA key.
    
    Returns:
        A dictionary of contacts, in the format:
        { 
            id:     { 
                        "name": <name>,
                        "ip": <ip>,
                        "fingerprint": <fingerprint>,
                        "messages": {   "time": <time>,
                                        "recieved": <bool>
                                        "contents": <text> 
                                    }
                    }
        }
    """
    try:
        with open(CONTACTS_DIR + "enc.key", "rb") as key_file:
            encrypted_key = key_file.read()

        with open(CONTACTS_PATH, "rb") as contacts_file:
            encrypted_contacts = contacts_file.read()
    except FileNotFoundError:
        return {}
    except OSError:
        if not exists(CONTACTS_DIR):
            makedirs(CONTACTS_DIR)
        else:
            print_red("Error: Contacts data not accessible.")
        return {}

    key = decrypt_rsa(encrypted_key, private)
    
    contacts_string = decrypt_aes(encrypted_contacts, key).decode()
    return json.loads(contacts_string)



def save_contacts(contacts, private):
    """
    Saves the contacts dictionary to the CONTACTS_PATH.

    Args:
        contacts: The contacts dictionary to save.
    """
    key = get_random_bytes(16) 
    contacts_string = json.dumps(contacts)

    encrypted_contacts = encrypt_aes(contacts_string.encode(), key)
    encrypted_key = encrypt_rsa(key, private)

    try:
        with open(CONTACTS_DIR + "enc.key", "wb") as key_file:
            key_file.write(encrypted_key)

        with open(CONTACTS_PATH, "wb") as contacts_file:
            contacts_file.write(encrypted_contacts)
    except OSError:
        if not exists(CONTACTS_DIR):
            makedirs(CONTACTS_DIR)
            with open(CONTACTS_DIR + "enc.key", "wb") as key_file:
                key_file.write(encrypted_key)
            with open(CONTACTS_PATH, "wb") as contacts_file:
                contacts_file.write(encrypted_contacts)
        else:
            print_red("Error: Contacts file not accessible.")


def display_contact(contact_id, contacts):
    """
    Displays information about a given contact.

    Args:
        name: The name of the contact to display.
        contacts: The contacts dictionary to read from.
    """
    print_green(contacts[contact_id]["name"])
    print("IP:", contacts[contact_id]["ip"])
    print("Fingerprint:", contacts[contact_id]["fingerprint"])
    print()


def display_convo(contact):
    print_bar("CONVERSATION")
    for message in contact["messages"]:
        print("{} {}: {}".format(message["time"], contact["name"] if message["recieved"] else "me", message["contents"]))
    print()


def display_messages(contacts):
    for contact_id in contacts:
        contact = contacts[contact_id]
        if contact["messages"]:
            message = contact["messages"][-1]["contents"]
            trimmed_msg = message if len(message) < 20 else (message[:27] + "...")
            timestamp = contact["messages"][-1]["time"]
            print("{:10s}  >  {:30s}  <  {}".format(contact["name"], trimmed_msg, timestamp))
        else:
            print("{:10s}  >  {:^30s}  <".format(contact["name"], "-- No messages --"))
    print()

