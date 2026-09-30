from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ApprovalRequest:
    approval_id: str
    decision_id: str
    required_action: str
    status: str = "PENDING"


@dataclass(frozen=True)
class ApprovalDecision:
    approval_id: str
    approver: str
    status: str
    reason: str
    decided_at: datetime