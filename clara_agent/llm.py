"""Optional OpenAI-backed simplification for CLARA Note."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .rule_engine import AGENT_STEPS, simplify_with_rules

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency for local dev
    load_dotenv = None

if load_dotenv:
    load_dotenv()

OPENAI_BASE_URL = "https://api.openai.com/v1"
GPTSAPI_BASE_URL = "https://api.gptsapi.net/v1"
DEFAULT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are CLARA Note, a safety-aware clinical language agent.

Task:
- Rewrite simulated clinical notes into readable, plain-language explanations.
- Explain medical terms.
- Flag uncertainty and privacy concerns.
- Suggest questions a patient, caregiver, or student could ask a clinician.

Safety boundaries:
- Do not diagnose.
- Do not recommend treatment.
- Do not decide whether symptoms are severe.
- Do not tell users to start, stop, or change medication.
- Do not claim the note is complete or correct.
- Always preserve uncertainty.
- Always state that the output is not medical advice.

Return only structured data matching the provided JSON schema."""

RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "plain_summary": {"type": "string"},
        "terms": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "term": {"type": "string"},
                    "explanation": {"type": "string"},
                },
                "required": ["term", "explanation"],
            },
        },
        "questions": {"type": "array", "items": {"type": "string"}},
        "uncertainties": {"type": "array", "items": {"type": "string"}},
        "safety_flags": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "label": {"type": "string"},
                    "level": {"type": "string", "enum": ["ok", "warning"]},
                },
                "required": ["label", "level"],
            },
        },
        "agent_steps": {"type": "array", "items": {"type": "string"}},
        "mode": {"type": "string", "enum": ["patient", "student", "caregiver"]},
        "source": {"type": "string"},
    },
    "required": [
        "plain_summary",
        "terms",
        "questions",
        "uncertainties",
        "safety_flags",
        "agent_steps",
        "mode",
        "source",
    ],
}


def simplify_note(note: str, audience: str = "patient", use_llm: bool = True) -> dict:
    fallback = simplify_with_rules(note, audience)
    if not use_llm or not get_api_key():
        return fallback

    try:
        llm_response, source = call_llm(note, audience)
    except (OSError, urllib.error.URLError, json.JSONDecodeError, KeyError, ValueError):
        fallback["source"] = "local_rules_after_llm_error"
        return fallback

    merged = fallback | llm_response
    merged["safety_flags"] = merge_flags(
        fallback.get("safety_flags", []),
        llm_response.get("safety_flags", []),
    )
    merged["agent_steps"] = llm_response.get("agent_steps") or AGENT_STEPS
    merged["mode"] = audience
    merged["source"] = source
    return merged


def get_api_key() -> str:
    return (
        os.getenv("CLARA_LLM_API_KEY")
        or os.getenv("GPTSAPI_KEY")
        or os.getenv("OPENAI_API_KEY")
        or ""
    )


def get_provider() -> str:
    return os.getenv("CLARA_LLM_PROVIDER", "openai_responses").lower()


def get_base_url() -> str:
    configured = os.getenv("CLARA_LLM_BASE_URL")
    if configured:
        return configured.rstrip("/")
    if get_provider() == "gptsapi":
        return GPTSAPI_BASE_URL
    return OPENAI_BASE_URL


def get_model() -> str:
    return os.getenv("CLARA_LLM_MODEL") or os.getenv("OPENAI_MODEL") or DEFAULT_MODEL


def call_llm(note: str, audience: str) -> tuple[dict, str]:
    provider = get_provider()
    if provider in {"gptsapi", "openai_chat", "chat_completions"}:
        return call_chat_completions(note, audience), f"{provider}_structured"
    return call_openai_responses(note, audience), "openai_responses_structured"


def call_openai_responses(note: str, audience: str) -> dict:
    model = get_model()
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Audience mode: {audience}\n\n"
                    "Simplify this simulated clinical note while preserving uncertainty:\n"
                    f"{note}"
                ),
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "clara_note_response",
                "strict": True,
                "schema": RESPONSE_SCHEMA,
            }
        },
        "max_output_tokens": 900,
    }
    request = urllib.request.Request(
        f"{get_base_url()}/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {get_api_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.loads(response.read().decode("utf-8"))

    output_text = extract_output_text(body)
    parsed = json.loads(output_text)
    validate_response_shape(parsed)
    return parsed


def call_chat_completions(note: str, audience: str) -> dict:
    model = get_model()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Audience mode: {audience}\n\n"
                    "Simplify this simulated clinical note while preserving uncertainty. "
                    "Return JSON only:\n"
                    f"{note}"
                ),
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "clara_note_response",
                "strict": True,
                "schema": RESPONSE_SCHEMA,
            },
        },
        "max_tokens": 900,
    }
    request = urllib.request.Request(
        f"{get_base_url()}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {get_api_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.loads(response.read().decode("utf-8"))

    output_text = body["choices"][0]["message"]["content"]
    parsed = json.loads(output_text)
    validate_response_shape(parsed)
    return parsed


def extract_output_text(response: dict) -> str:
    if response.get("output_text"):
        return response["output_text"]

    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                return content["text"]

    raise KeyError("No output text found in OpenAI response")


def validate_response_shape(data: dict) -> None:
    required = set(RESPONSE_SCHEMA["required"])
    missing = required - set(data)
    if missing:
        raise ValueError(f"Missing required keys: {sorted(missing)}")
    if data.get("mode") not in {"patient", "student", "caregiver"}:
        raise ValueError("Invalid mode")


def merge_flags(first: list[dict], second: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    merged: list[dict] = []
    for flag in first + second:
        key = (flag.get("label", ""), flag.get("level", "warning"))
        if key in seen:
            continue
        seen.add(key)
        merged.append({"label": key[0], "level": key[1]})
    return merged
