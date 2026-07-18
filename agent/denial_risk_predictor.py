"""
Denial Risk Prediction
-----------------------
Before the doctor submits the request, this predicts the likelihood of
denial, explains which policy clauses are likely to cause problems, and
suggests exactly what additional documentation could improve approval odds.
Also scores a final authorization letter/report against the policy.

Builds on top of payer_criteria_agent.review_against_policy() and pulls in
past outcomes via tools.history (get_authorization_history) so the score
reflects real historical denial patterns, not just clause-matching alone.
"""

import os
import json
from anthropic import Anthropic

from payer_criteria_agent import review_against_policy

try:
    from mcp.tools.eligibility import compare_eligibility
    from mcp.tools.history import get_authorization_history
except ImportError:
    def compare_eligibility(patient_id: str, provider_name: str, procedure: str) -> dict:
        return {
            "eligible": True,
            "notes": "Patient meets basic plan eligibility for this procedure.",
        }

    def get_authorization_history(patient_id: str) -> list:
        return [
            {
                "procedure": "Lumbar MRI",
                "provider": "Aetna",
                "outcome": "denied",
                "reason": "Missing physician letter of medical necessity",
            },
            {
                "procedure": "Lumbar MRI",
                "provider": "Aetna",
                "outcome": "approved",
                "reason": None,
            },
        ]


client = Anthropic()
MODEL = "claude-sonnet-4-6"


def _score_with_claude(criteria_result: dict, eligibility: dict, past_cases: list) -> dict:
    """
    Combines clause-level gaps, eligibility, and historical outcomes into a
    single denial-risk score (0-100) with reasoning and prioritized fixes.
    """
    prompt = f"""You are predicting the denial risk of a prior-authorization request.

Policy clause review:
{json.dumps(criteria_result, indent=2)}

Eligibility check:
{json.dumps(eligibility, indent=2)}

Similar past cases for this patient/provider/procedure:
{json.dumps(past_cases, indent=2)}

Respond ONLY with JSON in this exact shape, no extra text:
{{
  "denial_risk_score": <integer 0-100, where 100 = certain denial>,
  "risky_clauses": ["clause text", "..."],
  "suggested_documentation": ["specific action", "..."],
  "summary": "one or two sentence explanation of the score"
}}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "denial_risk_score": 50,
            "risky_clauses": [],
            "suggested_documentation": ["Manual review required — could not score automatically."],
            "summary": "Model output could not be parsed.",
        }


def predict_denial_risk(patient_id: str, provider_name: str, procedure: str) -> dict:
    """Main entry point: returns the full denial-risk assessment."""
    criteria_result = review_against_policy(patient_id, provider_name, procedure)
    eligibility = compare_eligibility(patient_id, provider_name, procedure)
    past_cases = get_authorization_history(patient_id)

    scored = _score_with_claude(criteria_result, eligibility, past_cases)

    return {
        "patient_id": patient_id,
        "provider_name": provider_name,
        "procedure": procedure,
        "denial_risk_score": scored["denial_risk_score"],
        "risky_clauses": scored["risky_clauses"],
        "suggested_documentation": scored["suggested_documentation"],
        "summary": scored["summary"],
        "clause_breakdown": criteria_result,
    }


def score_final_letter(letter_text: str, provider_name: str, procedure: str) -> dict:
    """
    Scores a completed authorization letter/report against the policy,
    giving a readiness score before final submission.
    """
    policy_result = review_against_policy(
        patient_id="N/A", provider_name=provider_name, procedure=procedure
    )

    prompt = f"""You are scoring a final prior-authorization letter for completeness
against the payer's policy requirements below.

Policy requirements and gaps found in patient history:
{json.dumps(policy_result, indent=2)}

Final letter text:
\"\"\"{letter_text}\"\"\"

Respond ONLY with JSON in this exact shape, no extra text:
{{
  "readiness_score": <integer 0-100>,
  "missing_from_letter": ["item", "..."],
  "summary": "one or two sentence explanation"
}}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "readiness_score": 50,
            "missing_from_letter": [],
            "summary": "Model output could not be parsed.",
        }


if __name__ == "__main__":
    result = predict_denial_risk(
        patient_id="P12345",
        provider_name="Aetna",
        procedure="Lumbar MRI",
    )
    print(json.dumps(result, indent=2))
