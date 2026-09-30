from datetime import datetime, timezone
from uuid import uuid4

from laya_labs.engine.schemas import ApprovalResult
from laya_labs.approvals.models import ApprovalDecision, ApprovalRequest


class ApprovalWorkflow:
    def __init__(self):
        self._requests: dict[str, ApprovalRequest] = {}
        self._decisions: dict[str, ApprovalDecision] = {}

    def request(self, decision_id: str, required_action: str) -> ApprovalRequest:
        if not decision_id or not required_action:
            raise ValueError("Decision ID and required action are required.")
        request = ApprovalRequest(
            approval_id=str(uuid4()),
            decision_id=decision_id,
            required_action=required_action,
        )
        self._requests[request.approval_id] = request
        return request

    def decide(
        self,
        request: ApprovalRequest,
        approver: str,
        approved: bool,
        reason: str,
    ) -> ApprovalDecision:
        if request.status != "PENDING":
            raise ValueError("Only pending approval requests can be decided.")
        if self._requests.get(request.approval_id) != request:
            raise ValueError("Approval request is unknown or altered.")
        if request.approval_id in self._decisions:
            raise ValueError("Approval request was already decided.")
        if (
            not isinstance(approver, str)
            or not approver.strip()
            or not isinstance(reason, str)
            or not reason.strip()
        ):
            raise ValueError("An explicit approver and reason are required.")
        decision = ApprovalDecision(
            approval_id=request.approval_id,
            approver=approver,
            status="APPROVED" if approved else "REJECTED",
            reason=reason,
            decided_at=datetime.now(timezone.utc),
        )
        self._decisions[request.approval_id] = decision
        return decision


def create_approval(policy_action: str) -> ApprovalResult:

    if policy_action == "REQUIRES_HUMAN_APPROVAL":
        return ApprovalResult(
            required=True,
            status="PENDING",
        )

    if policy_action in {
        "REQUIRES_REVIEW",
        "REQUIRES_SECURITY_REVIEW",
    }:
        return ApprovalResult(
            required=True,
            status="PENDING",
        )

    return ApprovalResult(
        required=False,
        status="NOT_REQUIRED",
    )


def approve() -> str:
    return "APPROVED"


def reject() -> str:
    return "REJECTED"