import json
import os
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NODES_FILE = os.path.join(BASE_DIR, "nodes.json")
_lock = threading.Lock()

def load_nodes():
    with _lock:
        if not os.path.exists(NODES_FILE):
            return []
        try:
            with open(NODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError, FileNotFoundError):
            return []

def save_nodes(nodes):
    with _lock:
        tmp_file = NODES_FILE + ".tmp"
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(nodes, f, indent=4)
        os.replace(tmp_file, NODES_FILE)
