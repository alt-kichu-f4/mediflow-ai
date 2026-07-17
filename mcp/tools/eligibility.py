from tools.patient import get_patient_history
from tools.policy import get_policy


def compare_eligibility(patient_id: str, provider_name: str):
    patient = get_patient_history(patient_id)
    policy = get_policy(provider_name)

    # Handle missing patient
    if "error" in patient:
        return patient

    # Handle missing policy
    if "error" in policy:
        return policy

    approved = (
        patient["therapy_weeks"] >= policy["minimum_weeks"]
        and patient["specialist_referral"]
    )

    return {
        "approved": approved,
        "patient": patient["name"],
        "provider": provider_name,
        "therapy_weeks": patient["therapy_weeks"],
        "required_weeks": policy["minimum_weeks"],
        "reason": (
            "Patient meets policy requirements."
            if approved
            else "Patient does not meet policy requirements."
        )
    }