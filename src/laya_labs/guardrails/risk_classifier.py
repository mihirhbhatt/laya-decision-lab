def apply_operation_policy(operation_type):

    if operation_type == "READ_ONLY":
        return "ALLOW"

    if operation_type == "MODIFY":
        return "REQUIRES_REVIEW"

    if operation_type == "SECURITY_SENSITIVE":
        return "REQUIRES_SECURITY_REVIEW"

    if operation_type == "DESTRUCTIVE":
        return "REQUIRES_HUMAN_APPROVAL"

    return "BLOCK"