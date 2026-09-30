from dataclasses import dataclass


@dataclass
class RoutingDecision:
    route: str
    reason: str


class ModelRouter:

    def route(
        self,
        *,
        regex_match: bool,
        risk_level: str | None = None,
    ) -> RoutingDecision:

        if regex_match:
            return RoutingDecision(
                route="REGEX",
                reason="Known deterministic security pattern.",
            )

        if risk_level == "CRITICAL":
            return RoutingDecision(
                route="HUMAN_REVIEW",
                reason="Critical risk requires human review.",
            )

        return RoutingDecision(
            route="LAYA",
            reason="Semantic classification is required.",
        )