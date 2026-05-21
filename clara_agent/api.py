"""FastAPI app for CLARA Note."""

from __future__ import annotations

from enum import Enum

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .llm import simplify_note


class Audience(str, Enum):
    patient = "patient"
    student = "student"
    caregiver = "caregiver"


class SimplifyRequest(BaseModel):
    note: str = Field(min_length=1, max_length=6000)
    audience: Audience = Audience.patient
    use_llm: bool = True


class Term(BaseModel):
    term: str
    explanation: str


class SafetyFlag(BaseModel):
    label: str
    level: str


class SimplifyResponse(BaseModel):
    plain_summary: str
    terms: list[Term]
    questions: list[str]
    uncertainties: list[str]
    safety_flags: list[SafetyFlag]
    agent_steps: list[str]
    mode: Audience
    source: str


app = FastAPI(
    title="CLARA Note API",
    description="Safety-aware clinical note simplification for simulated text.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "null"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "clara-note"}


@app.post("/api/simplify", response_model=SimplifyResponse)
def simplify(payload: SimplifyRequest) -> dict:
    return simplify_note(
        note=payload.note,
        audience=payload.audience.value,
        use_llm=payload.use_llm,
    )
