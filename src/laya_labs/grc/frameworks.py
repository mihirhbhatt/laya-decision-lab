from dataclasses import dataclass


@dataclass
class FrameworkMapping:
    source_framework: str
    source_control: str

    target_framework: str
    target_control: str

    mapping_type: str
    rationale: str