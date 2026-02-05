# app/state.py

import json
import os
from tempfile import NamedTemporaryFile

STATE_FILE = "data/state.json"


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    # atomic write (щоб не зіпсувати state.json при падінні під час запису)
    directory = os.path.dirname(STATE_FILE) or "."
    os.makedirs(directory, exist_ok=True)
    with NamedTemporaryFile("w", delete=False, dir=directory, encoding="utf-8") as tmp:
        json.dump(state, tmp, indent=2, ensure_ascii=False)
        tmp_path = tmp.name
    os.replace(tmp_path, STATE_FILE)