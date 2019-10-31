from Crypto.Hash import BLAKE2b
from Crypto.PublicKey import RSA
from base64 import b32encode, b32decode
from zlib import compress

def create_fingerprint(key):
    """
    Generates and returns a fingerprint for a given key.

    Args:
        key: The Crypto.PublicKey.RSA.RsaKey to fingerprint.

    Returns:
        The fingerprint of the key.
    """
    hasher = BLAKE2b.new(digest_bits=256)
    hasher.update(key.export_key())
    hash_bytes = hasher.digest()
    b32 = b32encode(hash_bytes)
    fingerprint = "-".join(b32[n:n+4].decode() for n in range(0, len(b32), 4))
    return fingerprint[:-5]
    

def verify_fingerprint(key, fingerprint):
    """
    Returns true if a key's fingerprint is equal to another fingerprint.

    Args:
        key: The Crypto.PublicKey.RSA.RsaKey to compare.
        fingerprint: The fingerprint to check against.

    Returns:
        True if the key matches the fingerprint, false otherwise.
    """
    return create_fingerprint(key) == fingerprint

