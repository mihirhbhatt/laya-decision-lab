import json


class TerraformAnalyzer:

    def analyze_plan(
        self,
        plan_json: dict,
    ):

        changes = []

        for resource in plan_json.get(
            "resource_changes",
            [],
        ):

            actions = resource.get(
                "change",
                {},
            ).get(
                "actions",
                [],
            )

            changes.append(
                {
                    "address": resource[
                        "address"
                    ],
                    "actions": actions,
                }
            )

        return changes

    def validate_plan(self, plan_json: dict, environment: str) -> dict:
        changes = self.analyze_plan(plan_json)
        destructive = [
            change for change in changes
            if "delete" in change["actions"]
        ]
        if destructive and environment.lower() == "production":
            action = "REQUIRES_HUMAN_APPROVAL"
        elif destructive:
            action = "REQUIRES_REVIEW"
        else:
            action = "ALLOW"
        return {
            "environment": environment,
            "changes": changes,
            "destructive": bool(destructive),
            "policy_action": action,
        }