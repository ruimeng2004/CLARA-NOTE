const sampleNotes = {
  cardiology:
    "Assessment: 54-year-old female with hypertension and type 2 diabetes presents with intermittent chest discomfort and shortness of breath. ECG shows nonspecific ST-T changes. Troponin is mildly elevated. CTA chest negative for pulmonary embolism. Plan: admit for telemetry, trend troponins, start aspirin, continue home metformin unless renal function worsens, cardiology consult.",
  radiology:
    "CT abdomen and pelvis with IV contrast: Mild right hydronephrosis with a 4 mm obstructing calculus at the ureterovesical junction. No free air or abscess. Impression: Right distal ureteral stone with mild upstream collecting system dilation. Recommend correlation with urinalysis and renal function.",
  discharge:
    "Discharge summary: Patient admitted for community-acquired pneumonia and treated with ceftriaxone and azithromycin. Oxygen requirement improved and patient is stable on room air. Complete oral antibiotics for 3 more days. Follow up with primary care in 1 week. Return for worsening fever, chest pain, confusion, or shortness of breath.",
  labs:
    "Lab note: Hemoglobin A1c is 8.4%, LDL cholesterol is 142 mg/dL, creatinine is 1.4 mg/dL, and eGFR is 52 mL/min/1.73m2. Urine albumin-to-creatinine ratio is elevated. Results suggest suboptimal diabetes control and possible early kidney involvement. Discuss medication adjustment and lifestyle plan."
};

const glossary = [
  {
    match: /hypertension|high blood pressure/i,
    term: "Hypertension",
    explanation: "High blood pressure, which can increase strain on the heart and blood vessels."
  },
  {
    match: /type 2 diabetes|diabetes/i,
    term: "Type 2 diabetes",
    explanation: "A condition where the body has trouble regulating blood sugar."
  },
  {
    match: /chest discomfort|chest pain/i,
    term: "Chest discomfort",
    explanation: "Pain, pressure, tightness, or an unusual feeling in the chest that may need urgent evaluation."
  },
  {
    match: /shortness of breath|dyspnea/i,
    term: "Shortness of breath",
    explanation: "Difficulty breathing or feeling unable to get enough air."
  },
  {
    match: /ECG|EKG/i,
    term: "ECG",
    explanation: "A heart rhythm test that records electrical activity from the heart."
  },
  {
    match: /ST-T/i,
    term: "ST-T changes",
    explanation: "ECG changes that can be related to the heart's electrical pattern, but are not specific by themselves."
  },
  {
    match: /troponin/i,
    term: "Troponin",
    explanation: "A blood test marker that can rise when the heart muscle is stressed or injured."
  },
  {
    match: /CTA|CT angiography/i,
    term: "CTA",
    explanation: "A CT scan with contrast used to look at blood vessels."
  },
  {
    match: /pulmonary embolism|PE/i,
    term: "Pulmonary embolism",
    explanation: "A blood clot in the lungs, which can cause chest pain or breathing problems."
  },
  {
    match: /telemetry/i,
    term: "Telemetry",
    explanation: "Continuous monitoring of heart rhythm while in the hospital."
  },
  {
    match: /aspirin/i,
    term: "Aspirin",
    explanation: "A medication that can reduce blood clotting in certain heart-related situations."
  },
  {
    match: /metformin/i,
    term: "Metformin",
    explanation: "A common medication used to manage blood sugar in type 2 diabetes."
  },
  {
    match: /renal function|kidney function|eGFR|creatinine/i,
    term: "Kidney function",
    explanation: "A set of lab clues that estimate how well the kidneys are filtering blood."
  },
  {
    match: /cardiology/i,
    term: "Cardiology",
    explanation: "The medical specialty focused on the heart and blood vessels."
  },
  {
    match: /hydronephrosis/i,
    term: "Hydronephrosis",
    explanation: "Swelling of part of the kidney because urine is not draining normally."
  },
  {
    match: /calculus|stone/i,
    term: "Calculus",
    explanation: "A stone, often made of mineral deposits, that can block urine flow."
  },
  {
    match: /ureterovesical junction|UVJ/i,
    term: "Ureterovesical junction",
    explanation: "The place where the tube from the kidney enters the bladder."
  },
  {
    match: /pneumonia/i,
    term: "Pneumonia",
    explanation: "An infection or inflammation in the lungs."
  },
  {
    match: /ceftriaxone|azithromycin|antibiotics/i,
    term: "Antibiotics",
    explanation: "Medicines used to treat infections caused by bacteria."
  },
  {
    match: /hemoglobin A1c|A1c/i,
    term: "Hemoglobin A1c",
    explanation: "A blood test that estimates average blood sugar over about three months."
  },
  {
    match: /\bLDL\b/i,
    term: "LDL cholesterol",
    explanation: "A type of cholesterol often discussed when assessing heart and blood vessel risk."
  },
  {
    match: /albumin-to-creatinine|albumin/i,
    term: "Urine albumin",
    explanation: "Protein in the urine that can be a clue about kidney stress or damage."
  }
];

const uncertaintyPatterns = [
  {
    match: /nonspecific|mildly|possible|suspected|cannot rule out|rule out|differential|correlation|suggest/i,
    text: "The note includes cautious or uncertain wording. Ask what has been confirmed and what is still being evaluated."
  },
  {
    match: /trend|repeat|follow[- ]?up|monitor|telemetry/i,
    text: "The plan depends on repeated measurements or monitoring, so one result may not tell the full story."
  },
  {
    match: /consult|referral|primary care/i,
    text: "Another clinician or specialist may need to review the case or guide next steps."
  },
  {
    match: /negative|no free air|no abscess/i,
    text: "A negative test can rule out one concern, but it may not explain every symptom."
  },
  {
    match: /recommend|discuss|adjustment/i,
    text: "The note points toward a next conversation, not a final decision by itself."
  }
];

const questionRules = [
  {
    match: /troponin|ECG|EKG|chest discomfort|chest pain/i,
    question: "What do the heart tests suggest, and what findings would change the plan?"
  },
  {
    match: /medication|aspirin|metformin|start|continue|hold|ceftriaxone|azithromycin|antibiotics/i,
    question: "Which medications should be started, stopped, or watched for side effects?"
  },
  {
    match: /CTA|CT|scan|negative|positive|impression|radiology/i,
    question: "What did the imaging test rule out, and what questions remain?"
  },
  {
    match: /admit|telemetry|monitor|oxygen|room air/i,
    question: "Why is monitoring needed, and what signs would show improvement or worsening?"
  },
  {
    match: /diabetes|hypertension|renal|kidney|creatinine|eGFR|A1c|\bLDL\b/i,
    question: "How do existing conditions or lab results affect the care plan?"
  },
  {
    match: /follow up|return for|discharge/i,
    question: "When should follow-up happen, and what symptoms should lead to urgent care?"
  }
];

const safetyRules = [
  {
    match: /chest pain|chest discomfort|shortness of breath|confusion|worsening fever/i,
    label: "Urgent language detected",
    level: "warning"
  },
  {
    match: /aspirin|metformin|ceftriaxone|azithromycin|antibiotics|medication|oral/i,
    label: "Medication mentioned",
    level: "warning"
  },
  {
    match: /nonspecific|mildly|possible|suggest|correlation|recommend|trend/i,
    label: "Uncertain wording",
    level: "warning"
  },
  {
    match: /follow up|return for|consult|primary care|cardiology/i,
    label: "Follow-up needed",
    level: "warning"
  }
];

const phiRules = [
  { match: /\b[A-Z][a-z]+,\s+[A-Z][a-z]+\b/, label: "Possible patient name" },
  { match: /\b\d{3}[-.]\d{3}[-.]\d{4}\b/, label: "Possible phone number" },
  { match: /\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b/, label: "Possible email address" },
  { match: /\b(MRN|Patient ID|Medical Record Number)\s*[:#]?\s*[A-Za-z0-9-]{4,}\b/i, label: "Possible medical record identifier" },
  { match: /\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/, label: "Possible exact date" }
];

const audienceCopy = {
  patient: {
    intro: "In patient-friendly language",
    ending: "Use this as a conversation aid, not as a diagnosis or treatment recommendation."
  },
  student: {
    intro: "For a medical AI or clinical student",
    ending: "The key task is to separate findings, assessment language, and next-step planning while preserving uncertainty; this is not a diagnosis or treatment recommendation."
  },
  caregiver: {
    intro: "For a caregiver",
    ending: "Focus on what needs monitoring, what questions to ask, and when the care team wants follow-up; this is not a diagnosis or treatment recommendation."
  }
};

const noteInput = document.querySelector("#noteInput");
const simplifyButton = document.querySelector("#simplifyButton");
const sampleButton = document.querySelector("#sampleButton");
const clearButton = document.querySelector("#clearButton");
const copyButton = document.querySelector("#copyButton");
const sampleChips = document.querySelectorAll(".sample-chip");
const audienceInputs = document.querySelectorAll("input[name='audience']");
const summaryOutput = document.querySelector("#summaryOutput");
const termsOutput = document.querySelector("#termsOutput");
const questionsOutput = document.querySelector("#questionsOutput");
const uncertaintyOutput = document.querySelector("#uncertaintyOutput");
const safetyOutput = document.querySelector("#safetyOutput");
const runtimeStatus = document.querySelector("#runtimeStatus");
const resultCards = document.querySelectorAll(".result-card");

const safetyReasons = {
  "No obvious PHI pattern detected": "The note did not match common personal identifier patterns checked by this demo.",
  "Possible PHI detected. Remove private details before using AI tools.":
    "The note matched one or more personal identifier patterns. Use simulated or de-identified text only.",
  "Urgent language detected": "The note contains symptoms or warning phrases that should be discussed with a clinician.",
  "Medication mentioned": "The note includes medication names or medication-plan language. This tool will not recommend changes.",
  "Uncertain wording": "The note uses cautious language such as possible, mild, recommend, or correlation.",
  "Follow-up needed": "The note mentions follow-up, return precautions, consults, or clinician review.",
  "Possible patient name": "A name-like pattern was found.",
  "Possible phone number": "A phone-number-like pattern was found.",
  "Possible email address": "An email-like pattern was found.",
  "Possible medical record identifier": "An MRN or patient-ID-like pattern was found.",
  "Possible exact date": "An exact-date-like pattern was found.",
  "Non-diagnostic explanation only": "CLARA explains language and questions; it does not diagnose or recommend treatment."
};

function splitSentences(text) {
  return text
    .replace(/\s+/g, " ")
    .split(/(?<=[.!?])\s+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean);
}

function getAudience() {
  return document.querySelector("input[name='audience']:checked")?.value || "patient";
}

function setRuntimeStatus(message, state = "idle") {
  runtimeStatus.lastChild.textContent = ` ${message}`;
  runtimeStatus.dataset.state = state;
}

function setLoading(isLoading) {
  resultCards.forEach((card) => {
    card.classList.toggle("loading", isLoading);
  });
}

function makePlainSummary(note, audience) {
  const lowerNote = note.toLowerCase();
  const findings = [];
  const plan = [];
  const copy = audienceCopy[audience];

  if (/chest discomfort|chest pain|shortness of breath|dyspnea/.test(lowerNote)) {
    findings.push("The note describes symptoms involving the chest or breathing.");
  }

  if (/troponin|ECG|EKG|ST-T/i.test(note)) {
    findings.push("The care team is checking whether the heart may be under stress.");
  }

  if (/negative.*pulmonary embolism|pulmonary embolism.*negative|negative.*PE/i.test(note)) {
    findings.push("One serious lung blood clot concern appears to have been checked and not found.");
  }

  if (/hydronephrosis|calculus|ureter|stone/i.test(note)) {
    findings.push("The imaging language points to a urinary stone causing some blockage or swelling.");
  }

  if (/pneumonia|oxygen|antibiotics/i.test(note)) {
    findings.push("The note describes treatment and recovery monitoring for a lung infection.");
  }

  if (/A1c|\bLDL\b|creatinine|eGFR|albumin/i.test(note)) {
    findings.push("The lab results relate to blood sugar, cholesterol, and kidney health.");
  }

  if (/admit|telemetry|monitor/i.test(note)) {
    plan.push("The plan includes monitoring.");
  }

  if (/consult|cardiology|primary care/i.test(note)) {
    plan.push("A clinician or specialist follow-up is part of the plan.");
  }

  if (/aspirin|metformin|medication|continue|start|hold|antibiotics|adjustment/i.test(note)) {
    plan.push("Medication decisions are part of the plan.");
  }

  if (/return for|follow up|complete oral/i.test(note)) {
    plan.push("The note includes instructions for what to do after leaving care.");
  }

  const fallback = splitSentences(note).slice(0, 2).join(" ");
  const summary = [...findings, ...plan];

  if (summary.length === 0) {
    return `${copy.intro}: ${fallback || "This note contains medical information that should be reviewed with a clinician."} ${copy.ending}`;
  }

  return `${copy.intro}: ${summary.join(" ")} ${copy.ending}`;
}

function findTerms(note) {
  return glossary
    .filter((entry) => entry.match.test(note))
    .map((entry) => `${entry.term}: ${entry.explanation}`);
}

function makeQuestions(note) {
  const questions = questionRules
    .filter((rule) => rule.match.test(note))
    .map((rule) => rule.question);

  questions.push("What symptoms or warning signs should prompt urgent medical attention?");
  questions.push("What should the patient understand before leaving the visit or hospital?");

  return [...new Set(questions)].slice(0, 6);
}

function findUncertainty(note) {
  const notes = uncertaintyPatterns
    .filter((pattern) => pattern.match.test(note))
    .map((pattern) => pattern.text);

  if (notes.length === 0) {
    notes.push("The note may omit context such as exam findings, timing, prior history, or full lab values.");
  }

  notes.push("This tool cannot verify whether the note is accurate or complete.");
  return [...new Set(notes)];
}

function findSafetyTags(note) {
  const tags = safetyRules
    .filter((rule) => rule.match.test(note))
    .map((rule) => ({ label: rule.label, level: rule.level }));

  const phiTags = phiRules
    .filter((rule) => rule.match.test(note))
    .map((rule) => ({ label: rule.label, level: "warning" }));

  if (phiTags.length > 0) {
    tags.unshift({
      label: "Possible PHI detected. Remove private details before using AI tools.",
      level: "warning"
    });
  } else {
    tags.unshift({ label: "No obvious PHI pattern detected", level: "ok" });
  }

  tags.push({ label: "Non-diagnostic explanation only", level: "ok" });
  return [...tags, ...phiTags];
}

function normalizeTerm(term) {
  if (typeof term === "string") {
    return term;
  }
  return `${term.term}: ${term.explanation}`;
}

function renderList(element, items) {
  element.classList.remove("muted");
  element.innerHTML = "";

  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = normalizeTerm(item);
    element.appendChild(li);
  });
}

function renderSafetyTags(items) {
  safetyOutput.classList.remove("muted");
  safetyOutput.innerHTML = "";

  items.forEach((item) => {
    const span = document.createElement("span");
    span.className = `safety-tag ${item.level}`;
    span.textContent = item.label;
    span.title = safetyReasons[item.label] || "Safety flag generated by CLARA Note.";
    safetyOutput.appendChild(span);
  });
}

function currentReportText() {
  const section = (title, items) => {
    const lines = Array.from(items.children).map((item) => `- ${item.textContent}`);
    return `${title}\n${lines.join("\n")}`;
  };

  const safetyLines = Array.from(safetyOutput.children).map((item) => `- ${item.textContent}`);

  return [
    "CLARA Note",
    "",
    "What this note says",
    summaryOutput.textContent.trim(),
    "",
    section("Terms translated", termsOutput),
    "",
    section("Questions to ask", questionsOutput),
    "",
    section("What is still unclear", uncertaintyOutput),
    "",
    `Safety checks\n${safetyLines.join("\n")}`,
    "",
    "This is a plain-language explanation, not medical advice."
  ].join("\n");
}

function renderResponse(response) {
  summaryOutput.textContent = response.plain_summary;
  summaryOutput.classList.remove("muted");
  renderList(
    termsOutput,
    response.terms.length ? response.terms : ["No glossary terms matched. Try adding more clinical detail."]
  );
  renderList(questionsOutput, response.questions);
  renderList(uncertaintyOutput, response.uncertainties);
  renderSafetyTags(response.safety_flags);
}

function localSimplify(note, audience) {
  const terms = findTerms(note);
  return {
    plain_summary: makePlainSummary(note, audience),
    terms,
    questions: makeQuestions(note),
    uncertainties: findUncertainty(note),
    safety_flags: findSafetyTags(note),
    source: "local_rules"
  };
}

async function simplifyWithBackend(note, audience) {
  const response = await fetch("http://localhost:8001/api/simplify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ note, audience, use_llm: true })
  });

  if (!response.ok) {
    throw new Error(`Backend returned ${response.status}`);
  }

  return response.json();
}

async function simplifyNote() {
  const note = noteInput.value.trim();
  const audience = getAudience();

  if (!note) {
    summaryOutput.textContent = "Enter a simulated note first.";
    summaryOutput.classList.add("muted");
    renderList(termsOutput, ["No terms analyzed yet."]);
    renderList(questionsOutput, ["No questions generated yet."]);
    renderList(uncertaintyOutput, ["No uncertainty flags yet."]);
    safetyOutput.textContent = "No safety checks run yet.";
    safetyOutput.classList.add("muted");
    setRuntimeStatus("Local rules ready", "idle");
    return;
  }

  simplifyButton.disabled = true;
  simplifyButton.textContent = "Simplifying...";
  setLoading(true);
  setRuntimeStatus("Trying CLARA backend...", "loading");

  try {
    const response = await simplifyWithBackend(note, audience);
    renderResponse(response);
    setRuntimeStatus(
      response.source === "openai_structured"
        ? "OpenAI structured output"
        : "Backend local rules fallback",
      "ok"
    );
  } catch {
    renderResponse(localSimplify(note, audience));
    setRuntimeStatus("Local rules fallback", "warn");
  } finally {
    setLoading(false);
    simplifyButton.disabled = false;
    simplifyButton.textContent = "Simplify Note";
  }
}

async function checkBackendHealth() {
  try {
    const response = await fetch("http://localhost:8001/api/health");
    if (!response.ok) {
      throw new Error("Health check failed");
    }
    setRuntimeStatus("Backend ready", "ok");
  } catch {
    setRuntimeStatus("Local rules ready", "idle");
  }
}

function setActiveSample(sampleKey) {
  sampleChips.forEach((chip) => {
    chip.classList.toggle("active", chip.dataset.sample === sampleKey);
  });
}

sampleChips.forEach((chip) => {
  chip.addEventListener("click", () => {
    const sampleKey = chip.dataset.sample;
    noteInput.value = sampleNotes[sampleKey];
    setActiveSample(sampleKey);
    simplifyNote();
  });
});

sampleButton.addEventListener("click", () => {
  const current = document.querySelector(".sample-chip.active")?.dataset.sample || "cardiology";
  noteInput.value = sampleNotes[current];
  simplifyNote();
});

clearButton.addEventListener("click", () => {
  noteInput.value = "";
  summaryOutput.textContent = "Enter a simulated note to generate a patient-friendly explanation.";
  summaryOutput.classList.add("muted");
  renderList(termsOutput, ["No terms analyzed yet."]);
  renderList(questionsOutput, ["No questions generated yet."]);
  renderList(uncertaintyOutput, ["No uncertainty flags yet."]);
  safetyOutput.textContent = "No safety checks run yet.";
  safetyOutput.classList.add("muted");
  setRuntimeStatus("Local rules ready", "idle");
});

copyButton.addEventListener("click", async () => {
  const originalText = copyButton.textContent;
  try {
    await navigator.clipboard.writeText(currentReportText());
    copyButton.textContent = "Copied";
    setRuntimeStatus("Report copied", "ok");
  } catch {
    setRuntimeStatus("Copy unavailable in this browser", "warn");
  } finally {
    window.setTimeout(() => {
      copyButton.textContent = originalText;
    }, 1400);
  }
});

audienceInputs.forEach((input) => {
  input.addEventListener("change", simplifyNote);
});

simplifyButton.addEventListener("click", simplifyNote);

noteInput.value = sampleNotes.cardiology;
simplifyNote();
checkBackendHealth();
