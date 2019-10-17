import socket
import struct
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


PORT = 5300


def transmit(contact, message, public, private):
    """
    Sends a message to the provided contact.

    Args:
        contact: The contact information of the recipient in the format:
            { "ip": <ip>, "fingerprint": <fingerprint>, "messages": <messages>}
            For more detail, see load_contacts() in src/contacts.py.
        message: The message (in bytes) to send.
        public: The user's public RSA key.
        private: The user's private RSA key.

    Raises:
        socket.error: Client server not accessible.
        socket.timeout: Connection timed out.
    """
    contact_addr = (contact["ip"], PORT)

    with socket.create_connection(contact_addr, 15) as sock:
        # Exchanging public keys
        send(sock, public.export_key())
        client_public = RSA.import_key(recieve(sock))

        # Creating and sending session key
        session = get_random_bytes(16)
        send_session(sock, session, client_public, private)

        # Sending message
        send_aes(sock, message, session, private)


def send(sock, message):
    """
    Prefixes a message with its size and sends it to be recieved by recvall().
    
    Args:
        sock: The socket from which to send.
        message: The data to send.
    """
    packed = struct.pack("h", len(message)) + message
    sock.sendall(packed)


def recieve(sock):
    """
    Recieves and returns a message sent from send().

    Args:
        sock: The sock from which to recieve.
    """
    # Get the length of the message
    message_len_raw = recvall(sock, 2)
    if not message_len_raw:
        raise socket.error("Connection lost")
    message_len = struct.unpack("=h", message_len_raw)[0]

    # Return the rest of the message
    return recvall(sock, message_len)


def recvall(sock, num_bytes):
    """
    Recieves a size-prefixed message from the send() function above.
    Thanks to Adam Rosenfield and Hedde van der Heide for the elegant solution.

    Args:
        sock: The socket to receive from.

    Returns:
        The complete message received by the socket, or None if no data is received.
    """
    recieved = bytes()
    while len(recieved) < num_bytes:
        data = sock.recv(num_bytes - len(recieved))
        if not data:
            return None
        recieved += data

    return recieved


def encrypt_rsa(message, key):
    """
    Encrypts a message with the provided RSA key.

    Args:
        message: The message (in bytes) to encrypt.
        key: The Crypto.PublicKey.RSA.RsaKey with which to encrypt.

    Returns:
        The encrypted message in bytes.
    """
    cipher = PKCS1_OAEP.new(key)
    return cipher.encrypt(message)

def decrypt_rsa(message, key):
    """
    Decrypts a message with the provided RSA key.

    Args:
        message: The message (in bytes) to decrypt.
        key: The Crypto.PublicKey.RSA.RsaKey with which to decrypt.

    Returns:
        The decrypted message in bytes.
    """
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(message)


def encrypt_aes(message, key):
    """
    Encrypts a message with the provided AES key.

    Args:
        message: The message (in bytes) to encrypt.
        key: The AES key (in bytes) with which to decrypt.

    Returns:
        The encrypted message in bytes, where the first 16 bytesare the nonce, 
        the second 16 are the tag, and the rest are the ciphertext:

             Nonce          Tag         Ciphertext
        [-----16-----][-----16-----][-------n-------]
    """
    aes_cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = aes_cipher.encrypt_and_digest(message)
    total = bytearray(aes_cipher.nonce)
    total.extend(bytes(tag))
    total.extend(bytes(ciphertext))
    return bytes(total)


def decrypt_aes(message, key):
    """
    Decrypts a message with the provided AES key.

    Args:
        message: The message (in bytes, as formatted by encrypt_aes()) to decrypt.
        key: The AES key (in bytes) with which to decrypt.

    Returns:
        The decrypted message in bytes.
    """
    nonce = message[:16]
    tag = message[16:32]
    ciphertext = message[32:]
    aes_cipher = AES.new(key, AES.MODE_EAX, nonce)
    return aes_cipher.decrypt_and_verify(ciphertext, tag)    


def send_session(sock, session, client_public, private):
    """
    Sends an AES session key over hybrid RSA/AES through a socket.

    Sends the RSA-encrypted session key, then sends the AES-encrypted signature 
    of the key.

    Args:
        sock: The socket connected to the client.
        session: The AES session key (in bytes) to send.
        client_public: The client's public RSA key (as a Crypto.PublicKey.RSA.RsaKey).
        private: The private RSA key of the sender (as a Crypto.PublicKey.RSA.RsaKey).
    """
    encrypted_session = encrypt_rsa(session, client_public)
    signature = sign(session, private)
    encrypted_signature = encrypt_aes(signature, session)
    send(sock, encrypted_session)
    send(sock, encrypted_signature)


def recieve_session(sock, client_public, private):
    """
    Recieves an AES session key over hybrid RSA/AES through a socket.
    
    For further description see send_session().

    Args:
        sock: The socket connected to the sender.
        client_public: The sender's public RSA key (as a Crypto.PublicKey.RSA.RsaKey).
        private: The private RSA key of the reciever (as a Crypto.PublicKey.RSA.RsaKey).
    """
    encrypted_session = recieve(sock)
    session_key = decrypt_rsa(encrypted_session, private)

    encrypted_signature = recieve(sock)
    signature = decrypt_aes(encrypted_signature, session_key)
    verify(session_key, signature, client_public)
    
    return session_key


def send_aes(sock, message, session_key, private):
    """
    Encrypts the message with AES and sends it as well as its signature through a socket.

    Args:
        sock: The socket connected to the client.
        message: The message (in bytes) to send.
        client_public: The client's public RSA key (as a Crypto.PublicKey.RSA.RsaKey).
        private: The private RSA key of the sender (as a Crypto.PublicKey.RSA.RsaKey).
    """
    encrypted_message = encrypt_aes(message, session_key)
    signature = sign(message, private)
    encrypted_signature = encrypt_aes(signature, session_key)
    send(sock, encrypted_message)
    send(sock, encrypted_signature)


def recieve_aes(sock, client_public, key):
    """
    Decrypts and verifies a message sent through a socket by send_aes().

    Args:
        sock: The socket connected to the sender.
        client_public: The sender's public RSA key (as a Crypto.PublicKey.RSA.RsaKey).
        private: The private RSA key of the reciever (as a Crypto.PublicKey.RSA.RsaKey).
    """
    encrypted_message = recieve(sock)
    message = decrypt_aes(encrypted_message, key)

    encrypted_signature = recieve(sock)
    signature = decrypt_aes(encrypted_signature, key)
    verify(message, signature, client_public)
    
    return message


def sign(message, key):
    """
    Returns a signature of a message given an RSA key.

    Args:
        message: The message (in bytes) to sign.
        key: The Crypto.PublicKey.RSA.RsaKey with which to sign the message.

    Returns:
        A signature (in bytes) of the message.
    """
    hasher = SHA256.new()
    hasher.update(message)
    signer = pkcs1_15.new(key)
    return signer.sign(hasher)

def verify(message, signature, key):
    """
    Verifies a signature, throwing an error if it is invalid.

    Args:
        message: The plaintext message (in bytes) signed by the signature.
        signature: The signature produced by sign() to verify.
        key: The opposing key of the Crypto.PublicKey.RSA.RsaKey used to 
            sign the message.

    Raises:
        ValueError: Invalid signature.
    """
    verifier = pkcs1_15.new(key)
    hasher = SHA256.new(message)
    verifier.verify(hasher, signature)

