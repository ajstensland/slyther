from Crypto.PublicKey import RSA
from os import makedirs
from os.path import exists, isfile
from src.ui import *
from time import sleep
from random import random


DIR = "data/keys/"
PUBLIC_PATH = "data/keys/public.pem"
PRIVATE_PATH = "data/keys/private.pem"


def load_keys(password):
    """
    Loads and returns keys from default paths.
    
    Args:
        password: The password to decrypt the private key file.

    Returns:
        A tuple of (public key, private key), where both keys are 
        Crypto.PublicKey.RSA.RsaKeys.
    """
    try:
        with open(PRIVATE_PATH, "rb") as private_file:
            private = RSA.import_key(private_file.read(),
                                              passphrase=password)

        with open(PUBLIC_PATH, "rb") as public_file:
            public = RSA.import_key(public_file.read())

    except FileNotFoundError:
        print_red("Error: No keys found.")
        exit()
    except OSError:
        print_red("Error: Keys inaccessible.")
        exit()

    return public, private


def create_password():
    """Prompts the user to create and confirm a password, and returns the password."""
    password1 = getpass_handled("Password: ")
    password2 = getpass_handled("Confirm password: ")
    while password1 != password2:
        print_red("Your passwords do not match. Please try again:")
        password1 = getpass_handled("Password: ")
        password2 = getpass_handled("Confirm password: ")

    return password1


def create_keys():
    """Generates and returns a Crypto.PublicKey.RSA.RsaKey pair (in a tuple)"""
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    return private_key, public_key


def save_keys(private, public, password):
    """
    Saves RSA keys to their default paths.

    Args:
        private: The private key to save.
        public: The public key to save.
        password: The password to encrypt the private key with.
    """
    encrypted_private = private.export_key(passphrase=password,
                                           pkcs=8,
                                           protection="scryptAndAES128-CBC")

    if not exists(DIR):
        makedirs(DIR)

    try:
        with open(PRIVATE_PATH, "wb") as private_file:
            private_file.write(encrypted_private)
    except OSError:
        print_red("Error: Private key file inaccessible.")

    try:
        with open(PUBLIC_PATH, "wb") as public_file:
            public_file.write(public.export_key())
    except OSError:
        print_red("Error: Public key file inaccessible.")


def create_account():
    """
    Walks a user through the process of creating an account.
    
    Gets a user password, creates an RSA key pair, and saves them.
    """
    print("Welcome to slyther! Enter a password for your new account to begin...")
    password = create_password()
    private, public = create_keys()
    save_keys(private, public, password)
    print_green("Account created!\n")


def login():
    """Prompts a user for their password, and returns a tuple of their keys upon success."""
    if not isfile(PRIVATE_PATH) or not isfile(PUBLIC_PATH):
        create_account()
    
    print("Please log in...")
    password = getpass_handled("Password: ")
    
    public = ""
    private = ""
    while True:
        try:
            public, private = load_keys(password)
        except ValueError:
            sleep(random() * 2)
            print_red("\nInvalid password. Please try again.")
            password = getpass_handled("Password: ")
            continue
        break

    print_green("Login successful.\n")
    return public, private

