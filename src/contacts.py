import json
from os.path import exists
from os import makedirs
from src.ui import *

CONTACTS_DIR = "data/contacts/"
CONTACTS_PATH = "data/contacts/contacts.json"

def load_contacts():
    """
    Loads the contacts dictionary from the CONTACTS_PATH.

    Returns:
        A dictionary of contacts, in the format:
        { 
            "name": { 
                        "ip": <ip>,
                        "fingerprint": <fingerprint>,
                        "messages": {   "time": <time>,
                                        "to": <name>,
                                        "from": <name/ip>,
                                        "contents": <text> 
                                    }
                    }
        }
    """
    try:
        with open(CONTACTS_PATH, "r") as contacts_file:
            return json.load(contacts_file)
    except FileNotFoundError:
        return {}
    except OSError:
        if not exists(CONTACTS_DIR):
            makedirs(CONTACTS_DIR)
        else:
            print_red("Error: Contacts file not accessible.")
        return {}


def save_contacts(contacts):
    """
    Saves the contacts dictionary to the CONTACTS_PATH.

    Args:
        contacts: The contacts dictionary to save.
    """
    try:
        with open(CONTACTS_PATH, "w") as contacts_file:
            json.dump(contacts, contacts_file)
    except OSError:
        if not exists(CONTACTS_DIR):
            makedirs(CONTACTS_DIR)
        else:
            print_red("Error: Contacts file not accessible.")


def get_recipient(contacts):
    """
    Prompts a user for a contact. If a valid one is not provided, the user may 
    create a new one.
    
    Args:
        contacts: The contacts dictionary to select from."""
    while True:
        recipient = input_handled("To: ")

        if recipient in contacts:
            return recipient
        else:
            if confirm("Contact not recognized. Make new contact? (Y/n) "):
                return new_contact()


def new_contact():
    """
    Walks a user through the process of creating a new contact.

    Returns:
        The name of the contact created (used in get_recipient()).
    """
    contacts = load_contacts()
    print("Enter the information for your new contact...")
    name = input_handled("Name: ")
    ip = get_ip()
    fingerprint = input_default("Fingerprint", None)

    if name not in contacts:
        contacts[name] = {"ip": ip, "fingerprint": fingerprint, "messages": []}
        print_green("Contact added.\n")
    else:
        print_yellow("\n--- Warning: Contact exists ---")
        print_yellow("Existing Contact:")
        display_contact(name, contacts)

        print_yellow("\nNew Contact:")
        print_green(name)
        print("IP:", ip)
        print("Fingerprint:", fingerprint)

        if confirm("\nUpdate contact information for {}? (Y/n) ".format(name)):
            contacts[name]["ip"] = ip
            contacts[name]["fingerprint"] = fingerprint
            print_green("Contact updated.\n")
        else:
            print_green("Contact update cancelled.\n")

    save_contacts(contacts)
    return name


def display_contact(name, contacts):
    """
    Displays information about a given contact.

    Args:
        name: The name of the contact to display.
        contacts: The contacts dictionary to read from.
    """
    print_green(name)
    print("IP:", contacts[name]["ip"])
    print("Fingerprint:", contacts[name]["fingerprint"])
    print()

