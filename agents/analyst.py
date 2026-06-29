import anthropic
import json

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an Analyst agent performing post-incident analysis.
You receive structured facts extracted from a Slack incident thread.
Your job is to reason — not summarize. Identify root causes, contributing factors, causal chains, and what went well.

Rules:
- Distinguish root cause (the underlying condition) from trigger (the immediate action)
- Distinguish correlation from causation — only assert causation when the thread provides clear evidence
- Flag where you are inferring vs where the thread explicitly states something
- Write in blameless language — no individual blame, focus on systems and processes
- Output valid JSON only"""

ANALYSIS_SCHEMA = """
{
  "severity": "P1/P2/P3/P4",
  "severity_rationale": "string",
  "trigger": "string (the immediate action that started the incident)",
  "root_cause": "string (the underlying condition that made the trigger harmful)",
  "causal_chain": ["string (ordered steps from trigger to impact)"],
  "contributing_factors": [
    {
      "factor": "string",
      "type": "process|technical|organizational",
      "inference_level": "explicit|inferred"
    }
  ],
  "what_went_well": ["string"],
  "customer_impact": {
    "summary": "string",
    "affected_users_approx": "string or null",
    "duration_minutes": number,
    "data_loss": true/false,
    "financial_impact_known": true/false
  },
  "detection": {
    "how_detected": "string",
    "time_to_detect_minutes": number,
    "could_have_detected_earlier": "string or null"
  },
  "resolution": {
    "how_resolved": "string",
    "time_to_resolve_minutes": number,
    "workarounds_used": ["string"]
  },
  "action_items": [
    {
      "description": "string",
      "type": "prevention|detection|mitigation|process",
      "priority": "high|medium|low",
      "owner_role": "string (role not name)",
      "source": "explicit|inferred"
    }
  ],
  "open_questions": ["string (things the thread doesn't answer that the PIR author should investigate)"],
  "recurrence_risk": "high|medium|low",
  "recurrence_rationale": "string"
}
"""

def run(extracted: dict) -> dict:
    prompt = f"""Analyze this structured incident data and produce a deep analysis.
Follow this JSON schema exactly:
{ANALYSIS_SCHEMA}

EXTRACTED INCIDENT DATA:
{json.dumps(extracted, indent=2)}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)
