from laya_labs.guardrails.regex_classifier import (
    classify_with_regex
)


def test_destroy():

    result = classify_with_regex(
        "terraform destroy production"
    )

    assert result.category == "DESTRUCTIVE"


def test_mfa():

    result = classify_with_regex(
        "disable MFA"
    )

    assert result.category == "SECURITY_SENSITIVE"


def test_create():

    result = classify_with_regex(
        "create EC2 instance"
    )

    assert result.category == "MODIFY"


def test_list():

    result = classify_with_regex(
        "list EC2 instances"
    )

    assert result.category == "READ_ONLY"