from laya_labs.evidence.models import Evidence


class InMemoryEvidenceStore:
    def __init__(self):
        self._items: dict[str, Evidence] = {}

    def add(self, evidence: Evidence) -> None:
        if evidence.evidence_id in self._items:
            raise ValueError(f"Evidence already exists: {evidence.evidence_id}")
        self._items[evidence.evidence_id] = evidence

    def get(self, evidence_id: str) -> Evidence | None:
        return self._items.get(evidence_id)

    def list_for_resource(self, resource_id: str) -> list[Evidence]:
        return [
            item for item in self._items.values()
            if item.resource_id == resource_id
        ]