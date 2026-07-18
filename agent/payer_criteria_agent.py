"""
Payer Criteria Agent
---------------------
Acts like the insurance reviewer. Pulls the payer's policy requirements for a
given provider/procedure, pulls the patient's history, and checks every
policy clause against what's on file. Flags anything missing and suggests
what documentation would close the gap.

This module reuses the tools already built by the mcp/ teammate
(tools.policy, tools.patient) instead of re-implementing data access.
"""

import os
import json
from anthropic import Anthropic

# --- Import the existing MCP tools (built by the mcp/ teammate) -----------
# If you're running this from inside the repo, these imports work directly.
# Adjust the path below if your folder structure differs.
try:
    from mcp.tools.policy import get_policy
    from mcp.tools.patient import get_patient_history
except ImportError:
    # Fallback stubs so this file is runnable/testable on its own before
    # the real tools are wired in. Replace with real imports once integrated.
    def get_policy(provider_name: str, procedure: str) -> dict:
        return {
            "provider": provider_name,
            "procedure": procedure,
            "requirements": [
                "Prior authorization must be requested within 30 days of diagnosis",
                "Documented failure of at least 2 conservative treatments",
                "Imaging report confirming diagnosis within last 6 months",
                "Physician letter of medical necessity",
            ],
        }

    def get_patient_history(patient_id: str) -> dict:
        return {
            "patient_id": patient_id,
            "diagnosis_date": "2026-05-01",
            "conservative_treatments_tried": ["physical therapy"],
            "imaging_reports": [{"date": "2025-11-01", "type": "MRI"}],
            "physician_letter_on_file": False,
        }


client = Anthropic()  # reads ANTHROPIC_API_KEY from environment
MODEL = "claude-sonnet-4-6"


def _check_requirement_with_claude(requirement: str, history: dict) -> dict:
    """
    Uses Claude to reason over a single free-text policy requirement against
    the patient's (structured or unstructured) history, since policy clauses
    are rarely written in a form you can pattern-match against directly.
    """
    prompt = f"""You are reviewing a prior-authorization request against a single
payer policy requirement.

Requirement: "{requirement}"

Patient history (JSON):
{json.dumps(history, indent=2)}

Respond ONLY with JSON in this exact shape, no extra text:
{{
  "satisfied": true or false,
  "reason": "one sentence explaining why",
  "suggested_documentation": "what to add/attach if not satisfied, else empty string"
}}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "satisfied": False,
            "reason": "Could not parse model output; flagged for manual review.",
            "suggested_documentation": "Manual review required.",
        }


def review_against_policy(patient_id: str, provider_name: str, procedure: str) -> dict:
    """
    Main entry point. Returns a structured breakdown of which policy
    requirements are satisfied and which are missing, with suggested fixes.
    """
    policy = get_policy(provider_name, procedure)
    history = get_patient_history(patient_id)

    satisfied = []
    missing = []

    for requirement in policy["requirements"]:
        result = _check_requirement_with_claude(requirement, history)
        entry = {"requirement": requirement, "reason": result["reason"]}

        if result["satisfied"]:
            satisfied.append(entry)
        else:
            entry["suggested_documentation"] = result["suggested_documentation"]
            missing.append(entry)

    return {
        "patient_id": patient_id,
        "provider_name": provider_name,
        "procedure": procedure,
        "satisfied": satisfied,
        "missing": missing,
        "total_requirements": len(policy["requirements"]),
        "requirements_met": len(satisfied),
    }


if __name__ == "__main__":
    result = review_against_policy(
        patient_id="P12345",
        provider_name="Aetna",
        procedure="Lumbar MRI",
    )
    print(json.dumps(result, indent=2))
