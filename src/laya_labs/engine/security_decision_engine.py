from uuid import uuid4

from laya_labs.decisions.choice import build_choice_question
from laya_labs.engine.decision_pipeline import DecisionPipeline
from laya_labs.engine.schemas import DecisionResult
from laya_labs.policy.engine import (
    calculate_risk,
    evaluate_policy,
)
from laya_labs.approvals.workflow import (
    create_approval,
)

MAX_REQUEST_LENGTH = 2000
ENVIRONMENTS = {"development", "staging", "production"}
DEFAULT_LAYA_QUESTIONS = build_choice_question(
    "operation_type",
    "Classify the requested operation. Do not decide whether it is authorized.",
    {
        "READ_ONLY": "Inspect, list, describe, or retrieve without changing state.",
        "MODIFY": "Create, update, configure, or deploy a resource.",
        "SECURITY_SENSITIVE": "Change security controls, identity, encryption, or logging.",
        "DESTRUCTIVE": "Delete, destroy, terminate, or remove resources.",
        "DATA_ACCESS": "Access or expose protected or sensitive data.",
        "PRIVILEGED": "Use elevated permissions or administrative authority.",
        "UNKNOWN": "The operation cannot be confidently classified.",
    },
)


class SecurityDecisionEngine:

    def __init__(
        self,
        laya_engine=None,
        llm_provider=None,
        laya_questions=None,
        confidence_threshold: float = 0.80,
    ):
        self.classifier = DecisionPipeline(
            laya_engine=laya_engine,
            llm_provider=llm_provider,
            confidence_threshold=confidence_threshold,
        )
        self.laya_questions = (
            laya_questions
            if laya_questions is not None
            else DEFAULT_LAYA_QUESTIONS
        )

    def evaluate(
        self,
        request: str,
        environment: str = "development",
        privileged: bool = False,
        data_exposure: bool = False,
    ) -> DecisionResult:
        if not isinstance(request, str) or not request.strip():
            raise ValueError("request must be non-empty text.")
        request = request.strip()
        if len(request) > MAX_REQUEST_LENGTH:
            raise ValueError(f"request must not exceed {MAX_REQUEST_LENGTH} characters.")
        if not isinstance(environment, str) or not environment.strip():
            raise ValueError("environment must be development, staging, or production.")
        environment = environment.strip().lower()
        if environment not in ENVIRONMENTS:
            raise ValueError("environment must be development, staging, or production.")
        if not isinstance(privileged, bool) or not isinstance(data_exposure, bool):
            raise ValueError("privileged and data_exposure context flags must be boolean.")

        classification_result = self.classifier.classify(
            request,
            laya_questions=self.laya_questions,
        )
        source = classification_result["source"]
        classification = classification_result["category"]
        confidence = classification_result["confidence"]

        risk = calculate_risk(
            classification=classification,
            environment=environment,
            privileged=privileged,
            data_exposure=data_exposure,
        )

        policy = evaluate_policy(
            classification=classification,
            risk=risk,
            environment=environment,
            classification_source=source,
        )

        approval = create_approval(
            policy.action
        )

        return DecisionResult(
            decision_id=str(uuid4()),
            request=request,
            source=source,
            classification=classification,
            confidence=confidence,
            risk=risk,
            policy=policy,
            approval=approval,
            evidence=[
                {
                    "type": "classification",
                    "source": source,
                    "value": classification,
                    "confidence": confidence,
                },
                {
                    "type": "risk_assessment",
                    "source": "deterministic",
                    "score": risk.score,
                    "level": risk.level,
                    "factors": risk.factors,
                },
                {
                    "type": "policy_evaluation",
                    "source": "policy_engine",
                    "policy_id": policy.policy_id,
                    "action": policy.action,
                },
            ],
            metadata={
                "environment": environment,
                "candidate_category": classification_result.get("candidate_category"),
            },
        )