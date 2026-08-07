import hashlib
import secrets
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')
_active_tokens = set()

def _load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def _save_settings(data):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password):
    settings = _load_settings()
    stored = settings.get('admin_password_hash', hash_password('admin'))
    return hash_password(password) == stored

def create_token():
    token = secrets.token_hex(32)
    _active_tokens.add(token)
    return token

def verify_token(token):
    return token in _active_tokens

def revoke_token(token):
    _active_tokens.discard(token)

def change_password(new_password):
    settings = _load_settings()
    settings['admin_password_hash'] = hash_password(new_password)
    _save_settings(settings)

def get_telegram_config():
    settings = _load_settings()
    return settings.get('telegram_bot_token', ''), settings.get('telegram_chat_id', '')

def save_telegram_config(bot_token, chat_id):
    settings = _load_settings()
    settings['telegram_bot_token'] = bot_token
    settings['telegram_chat_id'] = chat_id
    _save_settings(settings)
