import json
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "patients.json"


def get_patient_history(patient_id):
    with open(DATA, "r") as f:
        patients = json.load(f)

    for patient in patients:
        if patient["patient_id"] == patient_id:
            return patient

    return {"error": "Patient not found"}