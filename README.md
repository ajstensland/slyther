# slyther
Slyther is an encrypted peer-to-peer messaging platform written in Python. Slyther employs the [pycryptodome](https://github.com/Legrandin/pycryptodome) library for its cryptographical needs.

Created as a project-based learning venture because I wanted to design a protocol and to learn how to use sockets and encryption.

## Quickstart

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Start server in one terminal
./slyther-server

# Start client in another terminal
./slyther
```

## Disclaimer
I make no claims regarding the security of this program. While it is encrypted, I may have made some errors blatant to the average cryptanalyst. Pycryptodome may also have vulnerabilities I am unaware of. **Do not trust this program with anything remotely important.** No personal information, no credit cards, no SSNs. I am not responsible for damages incurred by the improper usage of slyther or slyther-server.

**If you notice that I'm making a severe mistake** with the security of this program, **please let me know**. This has been purely a learning experience for me, and if you can provide more lessons for me to learn about this topic, please let me know!

## Protocol
Given that Alice (A) wants to send Bob (B) a message through slyther, three steps take place. Slyther uses a mixture of RSA with OAEP and AES-128-EAX to encrypt messages, and SHA512 hashes (with RSA) for digital signatures.

1. **Public Key Exchange**
    1. Alice sends Bob her public key (plaintext, since public keys are not secret)
    1. Bob checks this public key against a fingerprint shared over a trusted channel (fingerprints not yet implemented)
    1. Given that Alice's key is trusted, Bob sends his public key to Alice (again, in plaintext)
1. **Session Key Creation and Delivery**
    1. Alice then creates a 128-bit AES session key for her message
    1. Alice encrypts this key with Bob's public key and sends the RSA-encrypted key to Bob
    1. Alice signs the SHA512 hash of the key
    1. Alice encrypts this signature with the AES key and sends the AES-encrypted signature to Bob
1. **Message Delivery**
    1. Alice encrypts her message with the AES key and sends the encrypted message to Bob
    1. Alice signs the SHA512 hash of her message, encrypts it with the AES key, and sends it to Bob

## Acknowledgements

Big thanks to Hedde van der Heide and Adam Rosenfield for their [StackOverflow answer](https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data) on sending and receiving large messages over sockets
