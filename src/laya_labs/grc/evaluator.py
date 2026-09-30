from laya_labs.grc.controls import ControlResult


class ControlEvaluator:

    def evaluate_mfa(
        self,
        control_id: str,
        mfa_enabled: bool,
    ) -> ControlResult:

        if mfa_enabled:

            return ControlResult(
                control_id=control_id,
                framework="NIST",
                status="PASS",
                severity="HIGH",
                message="MFA requirement satisfied.",
            )

        return ControlResult(
            control_id=control_id,
            framework="NIST",
            status="FAIL",
            severity="HIGH",
            message="MFA requirement not satisfied.",
        )