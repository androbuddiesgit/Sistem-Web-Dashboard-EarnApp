import os
import base64
from cryptography.fernet import Fernet

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY_FILE = os.path.join(BASE_DIR, '.fernet_key')

def _get_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as f:
        f.write(key)
    return key

def encrypt_value(value):
    if not value:
        return value
    f = Fernet(_get_or_create_key())
    return f.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value):
    if not encrypted_value:
        return encrypted_value
    try:
        f = Fernet(_get_or_create_key())
        return f.decrypt(encrypted_value.encode()).decode()
    except Exception:
        return encrypted_value  # Return as-is if not encrypted (backward compat)
