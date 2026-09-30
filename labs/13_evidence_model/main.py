from laya_labs.evidence import InMemoryEvidenceStore, collect_evidence


def main():
    store = InMemoryEvidenceStore()
    evidence = collect_evidence(
        source="fixture", evidence_type="configuration",
        resource_id="bucket-demo", data={"encrypted": False},
    )
    store.add(evidence)
    print(f"Stored {evidence.evidence_type} evidence {evidence.evidence_id}")
    print(f"Evidence items for resource: {len(store.list_for_resource('bucket-demo'))}")


if __name__ == "__main__":
    main()