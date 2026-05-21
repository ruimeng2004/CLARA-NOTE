from clara_agent.guardrails import detect_phi, safety_flags


def test_detects_common_phi_patterns():
    text = "Smith, Anna MRN: A12345 was called at 555-123-4567 on 04/12/2026."

    labels = [flag.label for flag in detect_phi(text)]

    assert "Possible patient name" in labels
    assert "Possible phone number" in labels
    assert "Possible medical record identifier" in labels
    assert "Possible exact date" in labels


def test_safety_flags_include_non_diagnostic_boundary():
    labels = [
        flag.label
        for flag in safety_flags(
            "Chest pain noted. Start aspirin and follow up with cardiology."
        )
    ]

    assert "Urgent language detected" in labels
    assert "Medication mentioned" in labels
    assert "Follow-up needed" in labels
    assert "Non-diagnostic explanation only" in labels
