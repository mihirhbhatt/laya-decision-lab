from laya_labs.guardrails.tool_guard import (
    ToolRequest,
    evaluate_tool,
)


def main():

    print()
    print("=" * 80)
    print("LAYA DECISION LAB 08")
    print("TOOL SECURITY CONTROL")
    print("=" * 80)

    requests = [
        ToolRequest(
            tool="aws.ec2.list_instances",
            action="list",
            environment="dev",
        ),
        ToolRequest(
            tool="aws.iam.modify_user",
            action="modify",
            environment="production",
            privileged=True,
        ),
        ToolRequest(
            tool="terraform.destroy",
            action="destroy",
            environment="production",
            destructive=True,
        ),
    ]

    for request in requests:

        decision = evaluate_tool(request)

        print()
        print("-" * 80)
        print(f"Tool        : {request.tool}")
        print(f"Action      : {request.action}")
        print(f"Environment : {request.environment}")
        print(f"Allowed     : {decision.allowed}")
        print(f"Decision    : {decision.action}")
        print(f"Reason      : {decision.reason}")

    print()
    print("=" * 80)
    print("LAB 08 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()