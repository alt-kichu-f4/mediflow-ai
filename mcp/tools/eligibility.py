from tools.patient import get_patient_history
from tools.policy import get_policy


def compare_eligibility(patient_id):

    patient = get_patient_history(patient_id)

    if "error" in patient:
        return patient

    policy = get_policy(
        patient["insurance"],
        patient["requested_procedure"]
    )

    if policy is None:
        return {
            "patient_id": patient_id,
            "provider": patient["insurance"],
            "procedure": patient["requested_procedure"],
            "eligible": False,
            "status": "Pending",
            "reasons": [
                "No matching policy found."
            ]
        }

    requirements = policy["requirements"]

    reasons = []

    if patient["physical_therapy_sessions"] < requirements["minimum_pt_sessions"]:
        reasons.append(
            f"Insufficient PT sessions ({patient['physical_therapy_sessions']}/{requirements['minimum_pt_sessions']} required)"
        )

    if patient["pain_duration_weeks"] < requirements["minimum_pain_duration_weeks"]:
        reasons.append(
            f"Pain duration too short ({patient['pain_duration_weeks']}/{requirements['minimum_pain_duration_weeks']} weeks required)"
        )

    if (
        requirements["specialist_referral"]
        and not patient["specialist_referral"]
    ):
        reasons.append("Missing specialist referral")

    if reasons:
        return {
            "patient_id": patient_id,
            "provider": patient["insurance"],
            "procedure": patient["requested_procedure"],
            "eligible": False,
            "status": "Denied",
            "reasons": reasons
        }

    return {
        "patient_id": patient_id,
        "provider": patient["insurance"],
        "procedure": patient["requested_procedure"],
        "eligible": True,
        "status": "Approved",
        "reasons": [
            "Patient meets all payer requirements."
        ]
    }