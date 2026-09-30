from laya_labs.grc.controls import ControlResult


def evaluate_encryption(
    resource,
    control_id="SC-ENC-001",
):

    encrypted = resource.configuration.get("encrypted")

    if encrypted:

        return ControlResult(
            control_id=control_id,
            framework="NIST",
            status="PASS",
            severity="HIGH",
            message=(
                "Resource encryption "
                "requirement satisfied."
            ),
        )

    if encrypted is None:
        return ControlResult(
            control_id=control_id,
            framework="NIST",
            status="UNKNOWN",
            severity="HIGH",
            message="Encryption status could not be verified from observed evidence.",
        )

    return ControlResult(
        control_id=control_id,
        framework="NIST",
        status="FAIL",
        severity="HIGH",
        message=(
            "Resource encryption "
            "requirement failed."
        ),
    )