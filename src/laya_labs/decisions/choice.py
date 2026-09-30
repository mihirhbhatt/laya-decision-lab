from typing import Any


def build_choice_question(
    question_id: str,
    instructions: str,
    criteria: dict[str, str],
) -> dict[str, Any]:

    return {
        question_id: {
            "type": "choice",
            "instructions": instructions,
            "criteria": criteria,
        }
    }


def extract_choice(result, question_id):
    return result["answers"][question_id]["choice"]


def extract_confidence(result, question_id):

    answer = result["answers"][question_id]

    confidence = answer.get("answer_confidence")

    if confidence is None:
        return None

    return float(confidence)