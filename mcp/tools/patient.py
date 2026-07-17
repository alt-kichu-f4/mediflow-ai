PATIENTS = {
    "P001": {
        "name": "John Smith",
        "age": 45,
        "diagnosis": "Lower Back Pain",
        "therapy_weeks": 8,
        "insurance": "Blue Shield"
    }
}

def get_patient_history(patient_id: str):
    """
    Returns patient history based on patient ID.
    """
    return PATIENTS.get(
        patient_id,
        {"error": "Patient not found"}
    )