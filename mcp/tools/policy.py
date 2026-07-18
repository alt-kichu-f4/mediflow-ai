import json
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "insurance_policies.json"


def get_policy(provider, procedure):

    with open(DATA, "r") as f:
        policies = json.load(f)

    for policy in policies:
        if (
            policy["provider"] == provider
            and
            policy["procedure"] == procedure
        ):
            return policy

    return None