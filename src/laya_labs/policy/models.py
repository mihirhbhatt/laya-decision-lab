from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyRule:
    policy_id: str
    action: str
    reason: str
    classification: str | None = None
    environment: str | None = None
    priority: int = 100

    def matches(self, classification: str, environment: str) -> bool:
        return (
            (self.classification is None or self.classification == classification)
            and (self.environment is None or self.environment == environment)
        )