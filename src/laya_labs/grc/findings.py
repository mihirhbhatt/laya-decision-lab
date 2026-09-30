from dataclasses import dataclass, field


@dataclass
class Finding:
    finding_id: str
    control_id: str
    framework: str
    resource_id: str
    severity: str
    status: str

    description: str

    evidence_ids: list[str] = field(
        default_factory=list
    )

    recommendation: str = ""