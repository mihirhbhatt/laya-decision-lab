from laya_labs.approvals import ApprovalWorkflow


def main():
    workflow = ApprovalWorkflow()
    request = workflow.request("decision-demo", "production destructive change")
    decision = workflow.decide(request, "security-reviewer", False, "Plan is too broad")
    print(f"Approval {decision.approval_id}: {decision.status}")
    print(f"Approver: {decision.approver}; reason: {decision.reason}")


if __name__ == "__main__":
    main()