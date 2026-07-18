from mcp.server.fastmcp import FastMCP

from tools.patient import get_patient_history
from tools.policy import get_policy
from tools.eligibility import compare_eligibility
from tools.letter import generate_letter
from tools.history import get_authorization_history

mcp = FastMCP("MediFlow AI")


@mcp.tool()
def patient_history(patient_id: str):
    """Fetch patient information from the EHR."""
    return get_patient_history(patient_id)


@mcp.tool()
def insurance_policy(provider_name: str, procedure: str):
    """Fetch policy requirements for a provider and procedure."""
    return get_policy(provider_name, procedure)


@mcp.tool()
def eligibility(patient_id: str):
    """Check whether the patient's request satisfies the payer policy."""
    return compare_eligibility(patient_id)


@mcp.tool()
def authorization_letter(patient_id: str):
    """Generate a prior authorization letter."""
    return generate_letter(patient_id)


@mcp.tool()
def authorization_history(patient_id: str):
    """Retrieve previous authorization decisions."""
    return get_authorization_history(patient_id)