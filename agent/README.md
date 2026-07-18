# Agent Module

Two components, built as requested:

1. **`payer_criteria_agent.py`** — the "insurance reviewer." Pulls the payer
   policy for a provider/procedure and the patient's history, checks every
   clause, and flags what's missing plus what documentation would fix it.

2. **`denial_risk_predictor.py`** — runs before submission. Predicts a
   denial-risk score (0-100), explains which clauses are driving the risk,
   and suggests documentation to improve approval odds. Also includes
   `score_final_letter()` to grade a completed authorization letter/report
   against the policy before it goes out.

## How it fits with `mcp/`

Both files try to import the real data tools first:

```python
from mcp.tools.policy import get_policy
from mcp.tools.patient import get_patient_history
from mcp.tools.eligibility import compare_eligibility
from mcp.tools.history import get_authorization_history
```

If those imports fail (e.g. you're testing standalone before the repo is
fully wired together), each file falls back to small mock functions with
sample data so you can still run and see real output. **Once merged into
the repo, delete the `except ImportError` fallback blocks** so it always
uses the real `mcp/tools` data.

## Setup

```bash
cd agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
```

## Running

```bash
python payer_criteria_agent.py
python denial_risk_predictor.py
```

Each file's `if __name__ == "__main__"` block runs a demo with a sample
patient so you can see the JSON output shape immediately.

## Using in code

```python
from payer_criteria_agent import review_against_policy
from denial_risk_predictor import predict_denial_risk, score_final_letter

criteria = review_against_policy("P12345", "Aetna", "Lumbar MRI")
risk = predict_denial_risk("P12345", "Aetna", "Lumbar MRI")
readiness = score_final_letter(letter_text, "Aetna", "Lumbar MRI")
```

## Next steps / TODO

- [ ] Swap mock fallbacks for real `mcp/tools` imports once confirmed working end-to-end
- [ ] Add unit tests with real sample policy/patient data from `database/`
- [ ] Decide whether this should be exposed as its own MCP tool (so `mcp/server.py`
      can call it too) or stay a standalone module called by `frontend/`
