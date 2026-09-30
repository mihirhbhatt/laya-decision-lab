import re


def redact_sensitive_data(text: str) -> str:

    text = re.sub(
        r"(?i)(password|token|secret)\s*=\s*\S+",
        r"\1=[REDACTED]",
        text,
    )

    return text