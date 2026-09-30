from dataclasses import dataclass, field


@dataclass
class Control:
    control_id: str
    framework: str
    name: str
    description: str
    severity: str

    policy_ids: list[str] = field(
        default_factory=list
    )


@dataclass
class ControlResult:
    control_id: str
    framework: str
    status: str
    severity: str
    evidence: list[dict] = field(
        default_factory=list
    )
    message: str = ""