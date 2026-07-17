POLICIES = {
    "Blue Shield": {
        "requires_physical_therapy": True,
        "minimum_weeks": 6,
        "requires_specialist": True
    }
}

def get_policy(name: str):
    policy = POLICIES.get(name)

    if policy is None:
        return {"error": "Policy not found"}

    return policy