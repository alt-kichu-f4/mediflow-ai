import json
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "authorization_history.json"


def get_authorization_history(patient_id):

    with open(DATA) as f:
        history = json.load(f)

    return [
        h
        for h in history
        if h["patient_id"] == patient_id
    ]