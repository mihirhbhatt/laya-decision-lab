from dataclasses import dataclass


@dataclass
class ToolRequest:
    tool: str
    action: str
    environment: str
    privileged: bool = False
    destructive: bool = False


@dataclass
class ToolDecision:
    allowed: bool
    action: str
    reason: str


def evaluate_tool(request: ToolRequest) -> ToolDecision:

    if request.destructive and request.environment == "production":

        return ToolDecision(
            allowed=False,
            action="REQUIRES_HUMAN_APPROVAL",
            reason=(
                "Destructive production tool execution "
                "requires human approval."
            ),
        )

    if request.privileged and request.environment == "production":

        return ToolDecision(
            allowed=False,
            action="REQUIRES_SECURITY_REVIEW",
            reason=(
                "Privileged production tool execution "
                "requires security review."
            ),
        )

    return ToolDecision(
        allowed=True,
        action="ALLOW",
        reason="Tool request passed the current policy.",
    )