from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

from laya_labs.approvals.workflow import ApprovalWorkflow
from laya_labs.audit import AuditLog
from laya_labs.cloud.models import CloudResource
from laya_labs.cloud.security_pipeline import CloudSecurityPipeline
from laya_labs.engine.security_decision_engine import SecurityDecisionEngine
from laya_labs.guardrails.prompt_guard import inspect_prompt
from laya_labs.guardrails.tool_guard import ToolDecision, ToolRequest, evaluate_tool
from laya_labs.middleware.redaction import redact_sensitive_data
from laya_labs.routing.confidence_router import route_by_confidence

DEFAULT_WORKFLOW = (
    Path(__file__).resolve().parents[3]
    / "workflows"
    / "interactive-review.yaml"
)
REQUIRED_HANDLERS = (
    "decision",
    "routing",
    "approval",
    "tool_guard",
    "cloud_control",
    "audit",
)


@dataclass(frozen=True)
class WorkflowStage:
    stage_id: str
    title: str
    handler: str


@dataclass(frozen=True)
class WorkflowDefinition:
    workflow_id: str
    title: str
    description: str
    stages: tuple[WorkflowStage, ...]


def load_workflow(path: str | Path = DEFAULT_WORKFLOW) -> WorkflowDefinition:
    with Path(path).open(encoding="utf-8") as workflow_file:
        document: Any = yaml.safe_load(workflow_file)

    if not isinstance(document, dict) or document.get("version") != 1:
        raise ValueError("Workflow must be a version 1 mapping.")
    for field in ("id", "title", "description"):
        if not isinstance(document.get(field), str) or not document[field].strip():
            raise ValueError(f"Workflow needs a non-empty {field}.")

    raw_stages = document.get("stages")
    if not isinstance(raw_stages, list):
        raise ValueError("Workflow must contain a stages list.")

    stages = []
    for item in raw_stages:
        if not isinstance(item, dict) or any(
            not isinstance(item.get(field), str) or not item[field].strip()
            for field in ("id", "title", "handler")
        ):
            raise ValueError("Each workflow stage needs an id, title, and handler.")
        stages.append(
            WorkflowStage(
                stage_id=item["id"],
                title=item["title"],
                handler=item["handler"],
            )
        )

    if tuple(stage.handler for stage in stages) != REQUIRED_HANDLERS:
        raise ValueError(
            "Workflow stages must preserve the required decision, approval, "
            "cloud-control, and audit sequence."
        )

    return WorkflowDefinition(
        workflow_id=document["id"],
        title=document["title"],
        description=document["description"],
        stages=tuple(stages),
    )


def _ask_text(
    prompt: str,
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
) -> str:
    while True:
        answer = input_fn(prompt).strip()
        if answer:
            return answer
        output_fn("Please enter a value.")


def _ask_choice(
    prompt: str,
    choices: tuple[str, ...],
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
) -> str:
    available = "/".join(choices)
    while True:
        answer = input_fn(f"{prompt} ({available}): ").strip().lower()
        if answer in choices:
            return answer
        output_fn(f"Choose one of: {available}.")


def run_interactive(
    workflow_path: str | Path = DEFAULT_WORKFLOW,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
    decision_engine: SecurityDecisionEngine | None = None,
) -> dict[str, Any]:
    ask = input if input_fn is None else input_fn
    show = print if output_fn is None else output_fn
    workflow = load_workflow(workflow_path)
    engine = decision_engine or SecurityDecisionEngine()
    context: dict[str, Any] = {}

    show(workflow.title)
    show(workflow.description.strip())
    show("Do not enter credentials, secrets, or customer data.")

    for index, stage in enumerate(workflow.stages, start=1):
        show(f"\n{index}. {stage.title}")

        if stage.handler == "decision":
            context["request"] = _ask_text("What operation is being considered? ", ask, show)
            environment = _ask_choice(
                "Environment", ("development", "staging", "production"), ask, show
            )
            privileged = _ask_choice("Privileged operation?", ("yes", "no"), ask, show)
            data_exposure = _ask_choice("Could sensitive data be exposed?", ("yes", "no"), ask, show)
            context["environment"] = environment
            context["privileged"] = privileged == "yes"
            prompt_result = inspect_prompt(context["request"])
            context["prompt_guard"] = prompt_result
            show(f"Prompt guard: {'PASS' if prompt_result.allowed else 'BLOCK'} ({prompt_result.category})")
            if prompt_result.allowed:
                context["advisory"] = _ask_choice(
                    "Simulated AI advice (not an AI call)", ("none", "allow", "block"), ask, show
                )
            else:
                context["advisory"] = "none"
                show("Advisory step skipped because the prompt guard blocked this input.")
            decision = engine.evaluate(
                request=context["request"],
                environment=environment,
                privileged=context["privileged"],
                data_exposure=data_exposure == "yes",
            )
            context["decision"] = decision
            show(f"Classification: {decision.classification} ({decision.source})")
            show(f"Risk: {decision.risk.level} ({decision.risk.score:.2f})")
            show(f"Policy: {decision.policy.action} - {decision.policy.reason}")
            show(f"Approval required: {'yes' if decision.approval.required else 'no'}")
            if context["advisory"] != "none":
                show(
                    f"Advisory only: {context['advisory'].upper()}; "
                    f"policy remains {decision.policy.action}."
                )

        elif stage.handler == "approval":
            decision = context["decision"]
            if decision.policy.action == "BLOCK":
                show("Blocked by policy; human approval cannot override this block.")
            elif decision.approval.required:
                approver = _ask_text("Reviewer name: ", ask, show)
                outcome = _ask_choice("Reviewer outcome", ("approve", "reject"), ask, show)
                reason = _ask_text("Review reason: ", ask, show)
                approval_workflow = ApprovalWorkflow()
                approval_request = approval_workflow.request(
                    decision.decision_id,
                    decision.policy.action,
                )
                approval = approval_workflow.decide(
                    approval_request,
                    approver=approver,
                    approved=outcome == "approve",
                    reason=reason,
                )
                decision.approval.status = approval.status
                context["human_approval"] = approval
                show(f"Recorded human decision: {approval.status}")
            else:
                show("No human approval is required for this request.")

        elif stage.handler == "routing":
            decision = context["decision"]
            route = route_by_confidence(decision.confidence or 0.0)
            context["route"] = route
            show(
                f"Confidence route: {route} "
                f"(confidence {decision.confidence or 0.0:.2f}; low confidence escalates)."
            )

        elif stage.handler == "tool_guard":
            decision = context["decision"]
            if decision.policy.action == "BLOCK":
                tool_decision = ToolDecision(
                    allowed=False,
                    action="BLOCK",
                    reason="The authoritative policy block is final.",
                )
            else:
                tool_decision = evaluate_tool(
                    ToolRequest(
                        tool="simulated.infrastructure_change",
                        action=decision.classification.lower(),
                        environment=context["environment"],
                        privileged=context["privileged"],
                        destructive=decision.classification == "DESTRUCTIVE",
                    )
                )
            context["tool_guard"] = tool_decision
            show(f"Tool guard signal: {tool_decision.action} - {tool_decision.reason}")
            show("This check is diagnostic only; it cannot override the policy engine.")

        elif stage.handler == "cloud_control":
            provider = _ask_choice(
                "Sample provider", ("aws", "azure", "gcp", "kubernetes"), ask, show
            )
            resource_id = _ask_text("Sample resource ID: ", ask, show)
            region = _ask_text("Region or cluster: ", ask, show)
            encryption = _ask_choice(
                "Observed encryption", ("encrypted", "unencrypted", "unknown"), ask, show
            )
            encrypted = {"encrypted": True, "unencrypted": False, "unknown": None}[encryption]
            resource = CloudResource(
                resource_id=resource_id,
                provider=provider,
                resource_type="demo_resource",
                region=region,
                configuration={"encrypted": encrypted},
            )
            result = CloudSecurityPipeline().evaluate_resource(resource)
            context["resource_result"] = result
            show(f"Encryption control: {result['control_result'].status}")
            show(f"Evidence collected: {result['evidence'].evidence_id}")
            if result["finding"]:
                show(f"Finding created: {result['finding'].finding_id}")
            else:
                show("Finding created: no")

        elif stage.handler == "audit":
            decision = context["decision"]
            resource_result = context["resource_result"]
            control_result = resource_result["control_result"]
            finding = resource_result["finding"]
            approval_details = {
                "required": decision.approval.required,
                "status": decision.approval.status,
            }
            human_approval = context.get("human_approval")
            if human_approval is not None:
                approval_details.update(
                    approval_id=human_approval.approval_id,
                    approver=human_approval.approver,
                    reason=human_approval.reason,
                    decided_at=human_approval.decided_at.isoformat(),
                )
            event = AuditLog().record(
                "INTERACTIVE_REVIEW_COMPLETED",
                decision.decision_id,
                {
                    "request": redact_sensitive_data(context["request"]),
                    "classification_source": decision.source,
                    "classification": decision.classification,
                    "classification_confidence": decision.confidence,
                    "risk_score": decision.risk.score,
                    "risk_level": decision.risk.level,
                    "risk_factors": decision.risk.factors,
                    "policy_id": decision.policy.policy_id,
                    "policy_action": decision.policy.action,
                    "policy_reason": decision.policy.reason,
                    "approval": approval_details,
                    "advisory": context["advisory"],
                    "prompt_allowed": context["prompt_guard"].allowed,
                    "confidence_route": context["route"],
                    "tool_guard_action": context["tool_guard"].action,
                    "resource_id": resource_result["resource"].resource_id,
                    "control_id": control_result.control_id,
                    "control_status": control_result.status,
                    "decision_evidence": decision.evidence,
                    "evidence_id": resource_result["evidence"].evidence_id,
                    "finding_id": finding.finding_id if finding else None,
                    "execution": "NOT_RUN",
                },
            )
            context["audit_event"] = event
            show(f"Audit event recorded: {event.event_id}")
            show("Execution: NOT RUN (this demo evaluates; it does not change infrastructure).")

    return context