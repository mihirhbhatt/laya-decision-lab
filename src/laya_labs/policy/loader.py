from pathlib import Path
from typing import Any

import yaml

from laya_labs.policy.models import PolicyRule

ALLOWED_ACTIONS = {
    "ALLOW",
    "REQUIRES_REVIEW",
    "REQUIRES_SECURITY_REVIEW",
    "REQUIRES_HUMAN_APPROVAL",
    "BLOCK",
}


def load_policy_rules(path: str | Path) -> list[PolicyRule]:
    with Path(path).open(encoding="utf-8") as policy_file:
        document: Any = yaml.safe_load(policy_file)

    if not isinstance(document, dict) or document.get("version") != 1:
        raise ValueError("Policy document must be a version 1 mapping.")

    raw_rules = document.get("rules")
    if not isinstance(raw_rules, list):
        raise ValueError("Policy document must contain a rules list.")

    rules: list[PolicyRule] = []
    for item in raw_rules:
        if not isinstance(item, dict):
            raise ValueError("Each policy rule must be a mapping.")
        policy_id = item.get("policy_id")
        action = item.get("action")
        reason = item.get("reason")
        priority = item.get("priority", 100)
        if not isinstance(policy_id, str) or not policy_id.strip():
            raise ValueError("Each policy rule needs a non-empty policy_id.")
        if action not in ALLOWED_ACTIONS:
            raise ValueError(f"Unsupported policy action: {action!r}.")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"Policy {policy_id!r} needs a reason.")
        if not isinstance(priority, int) or isinstance(priority, bool):
            raise ValueError(f"Policy {policy_id!r} priority must be an integer.")
        classification = item.get("classification")
        environment = item.get("environment")
        if classification is not None and not isinstance(classification, str):
            raise ValueError(f"Policy {policy_id!r} classification must be text.")
        if environment is not None and not isinstance(environment, str):
            raise ValueError(f"Policy {policy_id!r} environment must be text.")

        rules.append(
            PolicyRule(
                policy_id=policy_id,
                action=action,
                reason=reason,
                classification=classification,
                environment=environment,
                priority=priority,
            )
        )
    return rules