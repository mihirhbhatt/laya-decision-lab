from laya_labs.decisions.score import (
    calculate_risk_score,
)


def test_read_only_is_low_risk():

    result = calculate_risk_score()

    assert result.score == 0
    assert result.level == "LOW"


def test_destructive_production_is_high_risk():

    result = calculate_risk_score(
        destructive=True,
        production=True,
        privileged=True,
    )

    assert result.score >= 0.70
    assert result.level in {
        "HIGH",
        "CRITICAL",
    }


def test_data_exposure_increases_risk():

    result = calculate_risk_score(
        data_exposure=True,
    )

    assert result.score > 0