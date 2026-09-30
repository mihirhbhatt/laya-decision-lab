def policy_gate(
    risk_level: str,
) -> str:

    if risk_level == "CRITICAL":
        return "REQUIRES_HUMAN_APPROVAL"

    if risk_level == "HIGH":
        return "REQUIRES_SECURITY_REVIEW"

    if risk_level == "MEDIUM":
        return "REQUIRES_REVIEW"

    return "ALLOW"