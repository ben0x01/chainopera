import hashlib
import base64
import os



def generate_code_verifier():
    """Generates a 'code_verifier' which is a random string using cryptographic random function."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")


def generate_code_challenge():
    """Generates a 'code_challenge' using the S256 method."""
    verifier = generate_code_verifier()
    sha256_hash = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(sha256_hash).decode("utf-8").rstrip("=")