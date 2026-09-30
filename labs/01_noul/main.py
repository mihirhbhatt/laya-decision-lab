import laya


def apply_policy(risk_probability: float) -> str:
    if risk_probability >= 0.90:
        return "BLOCK"

    if risk_probability >= 0.80:
        return "REQUIRES_HUMAN_APPROVAL"

    return "ALLOW"


def main():
    agent = laya.load("convaiinnovations/laya")

    questions = {
        "is_risky": {
            "type": "noul",
            "instructions": "Is this infrastructure operation potentially risky?",
            "criteria": {
                "false": (
                    "The operation is read-only or has minimal "
                    "impact on infrastructure."
                ),
                "true": (
                    "The operation could modify, delete, expose, "
                    "or significantly affect infrastructure."
                ),
            },
        }
    }

    request = {
        "request": "Run terraform destroy against production"
    }

    result = agent.predict(request, questions)

    answer = result["answers"]["is_risky"]

    risk_probability = float(answer["noul"])
    confidence = float(answer["answer_confidence"])

    decision = apply_policy(risk_probability)

    print("=" * 60)
    print("LAB 01 - NOUL")
    print("=" * 60)

    print(f"Request     : {request['request']}")
    print(f"Risk        : {risk_probability:.4f}")
    print(f"Confidence  : {confidence:.4f}")
    print(f"Decision    : {decision}")
    print(f"Action      : {answer['action']}")


if __name__ == "__main__":
    main()