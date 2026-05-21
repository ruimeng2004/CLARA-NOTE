"""Output safety review for CLARA Note responses."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from .guardrails import detect_phi

DIAGNOSIS_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\byou have\b", re.IGNORECASE),
    re.compile(r"\bthis means you have\b", re.IGNORECASE),
    re.compile(r"\bthe diagnosis is\b", re.IGNORECASE),
    re.compile(r"\byou are diagnosed with\b", re.IGNORECASE),
)

TREATMENT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\byou should start\b", re.IGNORECASE),
    re.compile(r"\byou should stop\b", re.IGNORECASE),
    re.compile(r"\byou should take\b", re.IGNORECASE),
    re.compile(r"\bincrease your dose\b", re.IGNORECASE),
    re.compile(r"\bdecrease your dose\b", re.IGNORECASE),
)

BOUNDARY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"not (a )?diagnosis", re.IGNORECASE),
    re.compile(r"not medical advice", re.IGNORECASE),
    re.compile(r"not.*treatment recommendation", re.IGNORECASE),
)


@dataclass(frozen=True)
class ReviewFlag:
    label: str
    level: str = "warning"


def review_response(note: str, response: dict) -> list[dict]:
    text = response_text(response)
    flags: list[ReviewFlag] = []

    if any(pattern.search(text) for pattern in DIAGNOSIS_PATTERNS):
        flags.append(ReviewFlag("Possible diagnostic wording in generated output"))

    if any(pattern.search(text) for pattern in TREATMENT_PATTERNS):
        flags.append(ReviewFlag("Possible treatment recommendation in generated output"))

    if not any(pattern.search(text) for pattern in BOUNDARY_PATTERNS):
        flags.append(ReviewFlag("Missing non-diagnostic boundary in generated output"))

    if detect_phi(note) and "Possible PHI detected. Remove private details before using AI tools." not in text:
        flags.append(ReviewFlag("Input may contain PHI but output did not surface a PHI warning"))

    if not response.get("uncertainties"):
        flags.append(ReviewFlag("Missing uncertainty notes"))

    if len(response.get("questions", [])) < 2:
        flags.append(ReviewFlag("Too few clinician questions"))

    return [asdict(flag) for flag in dedupe(flags)]


def response_text(response: dict) -> str:
    parts: list[str] = []
    for value in response.values():
        collect_text(value, parts)
    return "\n".join(parts)


def collect_text(value: object, parts: list[str]) -> None:
    if isinstance(value, str):
        parts.append(value)
    elif isinstance(value, dict):
        for nested in value.values():
            collect_text(nested, parts)
    elif isinstance(value, list):
        for nested in value:
            collect_text(nested, parts)


def dedupe(flags: list[ReviewFlag]) -> list[ReviewFlag]:
    seen: set[tuple[str, str]] = set()
    unique: list[ReviewFlag] = []
    for flag in flags:
        key = (flag.label, flag.level)
        if key in seen:
            continue
        seen.add(key)
        unique.append(flag)
    return unique
