def route_by_confidence(
    confidence: float,
    threshold: float = 0.80,
) -> str:

    if confidence >= threshold:
        return "ACCEPT"

    return "ESCALATE"