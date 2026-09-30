import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class RegexDecision:
    category: str
    rule_confidence: float
    matched_pattern: Optional[str] = None


PATTERNS = {

    "DESTRUCTIVE": [
        r"\bterraform\s+destroy\b",
        r"\bdestroy\b",
        r"\bdelete\b",
        r"\bterminate\b",
        r"\bremove\b",
        r"\btear\s+down\b",
    ],

    "SECURITY_SENSITIVE": [
        r"\bdisable\s+mfa\b",
        r"\bdisable\s+multi[-\s]?factor\b",
        r"\bdisable\s+encryption\b",
        r"\bdisable\s+logging\b",
        r"\bmodify\s+iam\b",
        r"\bchange\s+iam\b",
        r"\bremove\s+iam\b",
        r"\bchange\s+permissions\b",
        r"\bgrant\s+administrator\b",
        r"\bgrant\s+admin\b",
        r"\bdisable\s+security\b",
    ],

    "MODIFY": [
        r"\bterraform\s+apply\b",
        r"\bcreate\b",
        r"\bupdate\b",
        r"\bmodify\b",
        r"\bchange\b",
        r"\bconfigure\b",
        r"\bprovision\b",
        r"\bdeploy\b",
    ],

    "READ_ONLY": [
        r"\blist\b",
        r"\bshow\b",
        r"\bdescribe\b",
        r"\bget\b",
        r"\bquery\b",
        r"\bview\b",
        r"\bread\b",
        r"\baudit\b",
        r"\bcheck\b",
    ],
}


PRIORITY = [
    "DESTRUCTIVE",
    "SECURITY_SENSITIVE",
    "MODIFY",
    "READ_ONLY",
]


def normalize_request(request: str) -> str:

    text = request.lower()

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def classify_with_regex(request: str):

    text = normalize_request(request)

    for category in PRIORITY:

        for pattern in PATTERNS[category]:

            match = re.search(pattern, text)

            if match:

                return RegexDecision(
                    category=category,
                    rule_confidence=1.0,
                    matched_pattern=pattern,
                )

    return None