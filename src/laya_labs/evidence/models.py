from dataclasses import dataclass
from datetime import datetime


@dataclass
class Evidence:
    evidence_id: str
    source: str
    evidence_type: str
    resource_id: str
    collected_at: datetime
    data: dict