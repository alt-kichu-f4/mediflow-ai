from mcp.server.fastmcp import FastMCP

from tools.patient import get_patient_history
from tools.policy import get_policy
from tools.eligibility import compare_eligibility
from tools.letter import generate_letter

mcp = FastMCP("MediFlow AI")


@mcp.tool()
def patient_history(patient_id: str):
    """Get patient history."""
    return get_patient_history(patient_id)


@mcp.tool()
def insurance_policy(provider_name: str):
    """Get insurance policy."""
    return get_policy(provider_name)


@mcp.tool()
def eligibility(patient_id: str, provider_name: str):
    """Check insurance eligibility."""
    return compare_eligibility(patient_id, provider_name)


@mcp.tool()
def authorization_letter(patient_id: str, provider_name: str):
    """Generate prior authorization letter."""
    return generate_letter(patient_id, provider_name)


if __name__ == "__main__":
    print("🚀 MediFlow MCP Server Started")
    mcp.run()