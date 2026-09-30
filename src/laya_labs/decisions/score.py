from dataclasses import dataclass, field

@dataclass
class RiskFactor:
    name: str
    weight: float
    reason: str


@dataclass
class RiskScore:
    score: float
    level: str
    factors: list[RiskFactor] = field(default_factory=list)


def calculate_risk_score(
    *,
    destructive: bool = False,
    security_sensitive: bool = False,
    production: bool = False,
    privileged: bool = False,
    data_exposure: bool = False,
) -> RiskScore:

    factors = []

    if destructive:
        factors.append(
            RiskFactor(
                name="destructive_operation",
                weight=0.40,
                reason="The operation can delete or destroy infrastructure.",
            )
        )

    if security_sensitive:
        factors.append(
            RiskFactor(
                name="security_sensitive",
                weight=0.25,
                reason="The operation changes a security control.",
            )
        )

    if production:
        factors.append(
            RiskFactor(
                name="production_environment",
                weight=0.20,
                reason="The operation targets production.",
            )
        )

    if privileged:
        factors.append(
            RiskFactor(
                name="privileged_operation",
                weight=0.10,
                reason="The operation requires elevated privileges.",
            )
        )

    if data_exposure:
        factors.append(
            RiskFactor(
                name="data_exposure",
                weight=0.20,
                reason="The operation may expose sensitive data.",
            )
        )

    score = min(
        sum(factor.weight for factor in factors),
        1.0,
    )

    if score >= 0.80:
        level = "CRITICAL"
    elif score >= 0.60:
        level = "HIGH"
    elif score >= 0.30:
        level = "MEDIUM"
    else:
        level = "LOW"

    return RiskScore(
        score=score,
        level=level,
        factors=factors,
    )