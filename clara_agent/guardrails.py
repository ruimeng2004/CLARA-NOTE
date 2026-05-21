"""Safety checks for CLARA Note.

These checks are intentionally conservative. They do not decide clinical risk;
they identify text patterns that should be handled carefully in the UI.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyFlag:
    label: str
    level: str = "warning"


PHI_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b[A-Z][a-z]+,\s+[A-Z][a-z]+\b"), "Possible patient name"),
    (re.compile(r"\b\d{3}[-.]\d{3}[-.]\d{4}\b"), "Possible phone number"),
    (
        re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
        "Possible email address",
    ),
    (
        re.compile(
            r"\b(MRN|Patient ID|Medical Record Number)\s*[:#]?\s*[A-Za-z0-9-]{4,}\b",
            re.IGNORECASE,
        ),
        "Possible medical record identifier",
    ),
    (re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"), "Possible exact date"),
)

SAFETY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"chest pain|chest discomfort|shortness of breath|confusion|worsening fever",
            re.IGNORECASE,
        ),
        "Urgent language detected",
    ),
    (
        re.compile(
            r"aspirin|metformin|ceftriaxone|azithromycin|antibiotics|medication|oral",
            re.IGNORECASE,
        ),
        "Medication mentioned",
    ),
    (
        re.compile(
            r"nonspecific|mildly|possible|suggest|correlation|recommend|trend",
            re.IGNORECASE,
        ),
        "Uncertain wording",
    ),
    (
        re.compile(r"follow up|return for|consult|primary care|cardiology", re.IGNORECASE),
        "Follow-up needed",
    ),
)

UNSAFE_INTENT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bdiagnose me\b", re.IGNORECASE),
    re.compile(r"\bwhat treatment should I take\b", re.IGNORECASE),
    re.compile(r"\bshould I stop\b.*\bmedication\b", re.IGNORECASE),
    re.compile(r"\bshould I start\b.*\bmedication\b", re.IGNORECASE),
)


def detect_phi(text: str) -> list[SafetyFlag]:
    return [SafetyFlag(label) for pattern, label in PHI_PATTERNS if pattern.search(text)]


def detect_unsafe_intent(text: str) -> list[SafetyFlag]:
    if any(pattern.search(text) for pattern in UNSAFE_INTENT_PATTERNS):
        return [
            SafetyFlag(
                "Request may be asking for diagnosis or treatment advice",
                "warning",
            )
        ]
    return []


def safety_flags(text: str) -> list[SafetyFlag]:
    flags = [SafetyFlag(label) for pattern, label in SAFETY_PATTERNS if pattern.search(text)]
    phi_flags = detect_phi(text)
    unsafe_flags = detect_unsafe_intent(text)

    if phi_flags:
        flags.insert(
            0,
            SafetyFlag(
                "Possible PHI detected. Remove private details before using AI tools.",
                "warning",
            ),
        )
    else:
        flags.insert(0, SafetyFlag("No obvious PHI pattern detected", "ok"))

    flags.extend(phi_flags)
    flags.extend(unsafe_flags)
    flags.append(SafetyFlag("Non-diagnostic explanation only", "ok"))
    return dedupe_flags(flags)


def dedupe_flags(flags: list[SafetyFlag]) -> list[SafetyFlag]:
    seen: set[tuple[str, str]] = set()
    unique: list[SafetyFlag] = []
    for flag in flags:
        key = (flag.label, flag.level)
        if key in seen:
            continue
        seen.add(key)
        unique.append(flag)
    return unique
