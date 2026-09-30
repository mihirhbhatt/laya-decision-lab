from dataclasses import replace

import pytest

from laya_labs.approvals.workflow import ApprovalWorkflow
from laya_labs.audit.logger import AuditLog
from laya_labs.cloud.azure import normalize_resource as normalize_azure
from laya_labs.cloud.gcp import normalize_resource as normalize_gcp
from laya_labs.cloud.kubernetes import normalize_resource as normalize_kubernetes
from laya_labs.cloud.terraform import TerraformAnalyzer
from laya_labs.evidence.collector import collect_evidence
from laya_labs.evidence.store import InMemoryEvidenceStore


def test_audit_log_redacts_secret_fields():
    event = AuditLog().record(
        "DECISION", "decision-1", {"access_token": "hidden", "region": "west"}
    )

    assert event.payload == {"access_token": "[REDACTED]", "region": "west"}


def test_approval_records_named_human_and_requires_reason():
    workflow = ApprovalWorkflow()
    request = workflow.request("decision-1", "production change")

    decision = workflow.decide(request, "security-reviewer", True, "Reviewed plan")

    assert decision.status == "APPROVED"
    assert decision.approver == "security-reviewer"


def test_approval_request_cannot_be_decided_twice():
    workflow = ApprovalWorkflow()
    request = workflow.request("decision-2", "production change")
    workflow.decide(request, "reviewer", True, "Approved")

    with pytest.raises(ValueError, match="already decided"):
        workflow.decide(request, "reviewer", False, "Changed my mind")


def test_approval_rejects_altered_requests_and_missing_human_identity():
    workflow = ApprovalWorkflow()
    request = workflow.request("decision-3", "security review")

    with pytest.raises(ValueError, match="unknown or altered"):
        workflow.decide(
            replace(request, required_action="ALLOW"),
            "reviewer",
            True,
            "Approved",
        )
    with pytest.raises(ValueError, match="approver and reason"):
        workflow.decide(request, "", True, "")


def test_evidence_store_indexes_by_resource():
    store = InMemoryEvidenceStore()
    evidence = collect_evidence("fixture", "configuration", "resource-1", {})
    store.add(evidence)

    assert store.get(evidence.evidence_id) is evidence
    assert store.list_for_resource("resource-1") == [evidence]


def test_cloud_normalizers_map_provider_resources():
    azure = normalize_azure({"id": "a1", "type": "vm", "location": "west"})
    gcp = normalize_gcp({"name": "g1", "kind": "bucket", "region": "us"})
    kube = normalize_kubernetes(
        {"kind": "Pod", "metadata": {"name": "p1", "namespace": "apps"}}
    )

    assert (azure.provider, gcp.provider, kube.resource_id) == (
        "azure", "gcp", "apps/p1"
    )


def test_terraform_production_destroy_requires_human_approval():
    plan = {
        "resource_changes": [
            {"address": "aws_instance.web", "change": {"actions": ["delete"]}}
        ]
    }

    result = TerraformAnalyzer().validate_plan(plan, "production")

    assert result["policy_action"] == "REQUIRES_HUMAN_APPROVAL"