from dataclasses import dataclass, field


@dataclass
class CloudResource:
    resource_id: str
    provider: str
    resource_type: str
    region: str

    tags: dict[str, str] = field(
        default_factory=dict
    )

    configuration: dict = field(
        default_factory=dict
    )