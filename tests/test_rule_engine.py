from clara_agent.rule_engine import simplify_with_rules


def test_rule_engine_returns_structured_response():
    result = simplify_with_rules(
        "Troponin is mildly elevated. Plan: trend troponins and cardiology consult.",
        "patient",
    )

    assert result["mode"] == "patient"
    assert result["source"] == "local_rules"
    assert result["plain_summary"]
    assert result["terms"]
    assert result["questions"]
    assert result["uncertainties"]
    assert result["safety_flags"]
    assert result["agent_steps"]


def test_invalid_audience_falls_back_to_patient():
    result = simplify_with_rules("Follow up with primary care.", "invalid")

    assert result["mode"] == "patient"
