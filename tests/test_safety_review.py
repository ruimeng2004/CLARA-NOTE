from clara_agent.safety_review import review_response


def test_review_flags_diagnostic_and_treatment_language():
    response = {
        "plain_summary": "You have pneumonia. You should start antibiotics.",
        "terms": [],
        "questions": ["What should I ask?", "What follow-up is needed?"],
        "uncertainties": ["The note may be incomplete."],
        "safety_flags": [],
        "agent_steps": [],
        "mode": "patient",
        "source": "test",
    }

    labels = [flag["label"] for flag in review_response("Simulated note", response)]

    assert "Possible diagnostic wording in generated output" in labels
    assert "Possible treatment recommendation in generated output" in labels
    assert "Missing non-diagnostic boundary in generated output" in labels


def test_review_flags_missing_phi_warning():
    response = {
        "plain_summary": "This is not medical advice.",
        "terms": [],
        "questions": ["What is next?", "When should I follow up?"],
        "uncertainties": ["Context may be missing."],
        "safety_flags": [],
        "agent_steps": [],
        "mode": "patient",
        "source": "test",
    }

    labels = [
        flag["label"]
        for flag in review_response("Smith, Anna MRN: A12345", response)
    ]

    assert "Input may contain PHI but output did not surface a PHI warning" in labels


def test_llm_normalization_accepts_string_agent_steps_and_alt_term_keys():
    from clara_agent.llm import normalize_response

    response = normalize_response(
        {
            "plain_summary": "Summary",
            "terms": [{"name": "troponin", "definition": "Heart stress marker"}],
            "questions": "What should I ask?",
            "uncertainties": "The cause is unclear.",
            "safety_flags": "Not medical advice",
            "agent_steps": "Simplified the note",
            "mode": "patient",
            "source": "deepseek",
        },
        "patient",
    )

    assert response["terms"] == [
        {"term": "troponin", "explanation": "Heart stress marker"}
    ]
    assert response["questions"] == ["What should I ask?"]
    assert response["agent_steps"] == ["Simplified the note"]


def test_enforce_safety_boundary_adds_missing_boundary():
    from clara_agent.llm import enforce_safety_boundary

    response = {
        "plain_summary": "A lab value is elevated.",
        "safety_flags": [],
    }

    enforce_safety_boundary(response)

    assert "not a diagnosis" in response["plain_summary"].lower()
    assert any(
        flag["label"] == "Non-diagnostic explanation only"
        for flag in response["safety_flags"]
    )
