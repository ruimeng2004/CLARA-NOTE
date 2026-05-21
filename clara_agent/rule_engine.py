"""Deterministic fallback engine for CLARA Note."""

from __future__ import annotations

import re
from dataclasses import asdict

from .guardrails import safety_flags


AUDIENCE_COPY = {
    "patient": {
        "intro": "In patient-friendly language",
        "ending": "Use this as a conversation aid, not as a diagnosis or treatment recommendation.",
    },
    "student": {
        "intro": "For a medical AI or clinical student",
        "ending": "The key task is to separate findings, assessment language, and next-step planning while preserving uncertainty; this is not a diagnosis or treatment recommendation.",
    },
    "caregiver": {
        "intro": "For a caregiver",
        "ending": "Focus on what needs monitoring, what questions to ask, and when the care team wants follow-up; this is not a diagnosis or treatment recommendation.",
    },
}

GLOSSARY: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (
        re.compile(r"hypertension|high blood pressure", re.IGNORECASE),
        "Hypertension",
        "High blood pressure, which can increase strain on the heart and blood vessels.",
    ),
    (
        re.compile(r"type 2 diabetes|diabetes", re.IGNORECASE),
        "Type 2 diabetes",
        "A condition where the body has trouble regulating blood sugar.",
    ),
    (
        re.compile(r"chest discomfort|chest pain", re.IGNORECASE),
        "Chest discomfort",
        "Pain, pressure, tightness, or an unusual feeling in the chest that may need urgent evaluation.",
    ),
    (
        re.compile(r"shortness of breath|dyspnea", re.IGNORECASE),
        "Shortness of breath",
        "Difficulty breathing or feeling unable to get enough air.",
    ),
    (
        re.compile(r"ECG|EKG", re.IGNORECASE),
        "ECG",
        "A heart rhythm test that records electrical activity from the heart.",
    ),
    (
        re.compile(r"ST-T", re.IGNORECASE),
        "ST-T changes",
        "ECG changes that can be related to the heart's electrical pattern, but are not specific by themselves.",
    ),
    (
        re.compile(r"troponin", re.IGNORECASE),
        "Troponin",
        "A blood test marker that can rise when the heart muscle is stressed or injured.",
    ),
    (
        re.compile(r"CTA|CT angiography", re.IGNORECASE),
        "CTA",
        "A CT scan with contrast used to look at blood vessels.",
    ),
    (
        re.compile(r"pulmonary embolism|PE", re.IGNORECASE),
        "Pulmonary embolism",
        "A blood clot in the lungs, which can cause chest pain or breathing problems.",
    ),
    (
        re.compile(r"telemetry", re.IGNORECASE),
        "Telemetry",
        "Continuous monitoring of heart rhythm while in the hospital.",
    ),
    (
        re.compile(r"aspirin", re.IGNORECASE),
        "Aspirin",
        "A medication that can reduce blood clotting in certain heart-related situations.",
    ),
    (
        re.compile(r"metformin", re.IGNORECASE),
        "Metformin",
        "A common medication used to manage blood sugar in type 2 diabetes.",
    ),
    (
        re.compile(r"renal function|kidney function|eGFR|creatinine", re.IGNORECASE),
        "Kidney function",
        "A set of lab clues that estimate how well the kidneys are filtering blood.",
    ),
    (
        re.compile(r"cardiology", re.IGNORECASE),
        "Cardiology",
        "The medical specialty focused on the heart and blood vessels.",
    ),
    (
        re.compile(r"hydronephrosis", re.IGNORECASE),
        "Hydronephrosis",
        "Swelling of part of the kidney because urine is not draining normally.",
    ),
    (
        re.compile(r"calculus|stone", re.IGNORECASE),
        "Calculus",
        "A stone, often made of mineral deposits, that can block urine flow.",
    ),
    (
        re.compile(r"ureterovesical junction|UVJ", re.IGNORECASE),
        "Ureterovesical junction",
        "The place where the tube from the kidney enters the bladder.",
    ),
    (
        re.compile(r"pneumonia", re.IGNORECASE),
        "Pneumonia",
        "An infection or inflammation in the lungs.",
    ),
    (
        re.compile(r"ceftriaxone|azithromycin|antibiotics", re.IGNORECASE),
        "Antibiotics",
        "Medicines used to treat infections caused by bacteria.",
    ),
    (
        re.compile(r"hemoglobin A1c|A1c", re.IGNORECASE),
        "Hemoglobin A1c",
        "A blood test that estimates average blood sugar over about three months.",
    ),
    (
        re.compile(r"\bLDL\b", re.IGNORECASE),
        "LDL cholesterol",
        "A type of cholesterol often discussed when assessing heart and blood vessel risk.",
    ),
    (
        re.compile(r"albumin-to-creatinine|albumin", re.IGNORECASE),
        "Urine albumin",
        "Protein in the urine that can be a clue about kidney stress or damage.",
    ),
)

UNCERTAINTY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"nonspecific|mildly|possible|suspected|cannot rule out|rule out|differential|correlation|suggest",
            re.IGNORECASE,
        ),
        "The note includes cautious or uncertain wording. Ask what has been confirmed and what is still being evaluated.",
    ),
    (
        re.compile(r"trend|repeat|follow[- ]?up|monitor|telemetry", re.IGNORECASE),
        "The plan depends on repeated measurements or monitoring, so one result may not tell the full story.",
    ),
    (
        re.compile(r"consult|referral|primary care", re.IGNORECASE),
        "Another clinician or specialist may need to review the case or guide next steps.",
    ),
    (
        re.compile(r"negative|no free air|no abscess", re.IGNORECASE),
        "A negative test can rule out one concern, but it may not explain every symptom.",
    ),
    (
        re.compile(r"recommend|discuss|adjustment", re.IGNORECASE),
        "The note points toward a next conversation, not a final decision by itself.",
    ),
)

QUESTION_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"troponin|ECG|EKG|chest discomfort|chest pain", re.IGNORECASE),
        "What do the heart tests suggest, and what findings would change the plan?",
    ),
    (
        re.compile(
            r"medication|aspirin|metformin|start|continue|hold|ceftriaxone|azithromycin|antibiotics",
            re.IGNORECASE,
        ),
        "Which medications should be started, stopped, or watched for side effects?",
    ),
    (
        re.compile(r"CTA|CT|scan|negative|positive|impression|radiology", re.IGNORECASE),
        "What did the imaging test rule out, and what questions remain?",
    ),
    (
        re.compile(r"admit|telemetry|monitor|oxygen|room air", re.IGNORECASE),
        "Why is monitoring needed, and what signs would show improvement or worsening?",
    ),
    (
        re.compile(r"diabetes|hypertension|renal|kidney|creatinine|eGFR|A1c|\bLDL\b", re.IGNORECASE),
        "How do existing conditions or lab results affect the care plan?",
    ),
    (
        re.compile(r"follow up|return for|discharge", re.IGNORECASE),
        "When should follow-up happen, and what symptoms should lead to urgent care?",
    ),
)

AGENT_STEPS = [
    "Detect clinical concepts",
    "Translate medical language",
    "Flag uncertainty and privacy risk",
    "Generate clinician questions",
    "Apply non-diagnostic safety boundary",
]


def simplify_with_rules(note: str, audience: str = "patient") -> dict:
    audience = audience if audience in AUDIENCE_COPY else "patient"
    terms = find_terms(note)
    return {
        "plain_summary": make_plain_summary(note, audience),
        "terms": terms,
        "questions": make_questions(note),
        "uncertainties": find_uncertainties(note),
        "safety_flags": [asdict(flag) for flag in safety_flags(note)],
        "agent_steps": AGENT_STEPS,
        "mode": audience,
        "source": "local_rules",
    }


def split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text)) if sentence.strip()]


def make_plain_summary(note: str, audience: str) -> str:
    lower_note = note.lower()
    findings: list[str] = []
    plan: list[str] = []
    copy = AUDIENCE_COPY[audience]

    if re.search(r"chest discomfort|chest pain|shortness of breath|dyspnea", lower_note):
        findings.append("The note describes symptoms involving the chest or breathing.")
    if re.search(r"troponin|ECG|EKG|ST-T", note, re.IGNORECASE):
        findings.append("The care team is checking whether the heart may be under stress.")
    if re.search(r"negative.*pulmonary embolism|pulmonary embolism.*negative|negative.*PE", note, re.IGNORECASE):
        findings.append("One serious lung blood clot concern appears to have been checked and not found.")
    if re.search(r"hydronephrosis|calculus|ureter|stone", note, re.IGNORECASE):
        findings.append("The imaging language points to a urinary stone causing some blockage or swelling.")
    if re.search(r"pneumonia|oxygen|antibiotics", note, re.IGNORECASE):
        findings.append("The note describes treatment and recovery monitoring for a lung infection.")
    if re.search(r"A1c|\bLDL\b|creatinine|eGFR|albumin", note, re.IGNORECASE):
        findings.append("The lab results relate to blood sugar, cholesterol, and kidney health.")

    if re.search(r"admit|telemetry|monitor", note, re.IGNORECASE):
        plan.append("The plan includes monitoring.")
    if re.search(r"consult|cardiology|primary care", note, re.IGNORECASE):
        plan.append("A clinician or specialist follow-up is part of the plan.")
    if re.search(r"aspirin|metformin|medication|continue|start|hold|antibiotics|adjustment", note, re.IGNORECASE):
        plan.append("Medication decisions are part of the plan.")
    if re.search(r"return for|follow up|complete oral", note, re.IGNORECASE):
        plan.append("The note includes instructions for what to do after leaving care.")

    summary = findings + plan
    if not summary:
        fallback = " ".join(split_sentences(note)[:2])
        body = fallback or "This note contains medical information that should be reviewed with a clinician."
        return f"{copy['intro']}: {body} {copy['ending']}"

    return f"{copy['intro']}: {' '.join(summary)} {copy['ending']}"


def find_terms(note: str) -> list[dict]:
    return [
        {"term": term, "explanation": explanation}
        for pattern, term, explanation in GLOSSARY
        if pattern.search(note)
    ]


def make_questions(note: str) -> list[str]:
    questions = [question for pattern, question in QUESTION_RULES if pattern.search(note)]
    questions.extend(
        [
            "What symptoms or warning signs should prompt urgent medical attention?",
            "What should the patient understand before leaving the visit or hospital?",
        ]
    )
    return list(dict.fromkeys(questions))[:6]


def find_uncertainties(note: str) -> list[str]:
    notes = [text for pattern, text in UNCERTAINTY_PATTERNS if pattern.search(note)]
    if not notes:
        notes.append("The note may omit context such as exam findings, timing, prior history, or full lab values.")
    notes.append("This tool cannot verify whether the note is accurate or complete.")
    return list(dict.fromkeys(notes))
