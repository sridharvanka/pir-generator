import anthropic
import json

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a Verifier agent. Your job is to fact-check a Post-Incident Review document against the original Slack thread that generated it.

Rules:
- The Slack thread is ground truth. Only what is explicitly stated or clearly implied in the thread counts as evidence.
- Distinguish between: HALLUCINATION (claim has no basis in the thread), MISATTRIBUTION (right fact, wrong person/time), FALSE_CERTAINTY (estimate presented as fact), UNSUPPORTED_INFERENCE (Analyst conclusion not evidenced in thread).
- Reasonable analytical inferences are acceptable — flag them as notes, not critical issues.
- For every finding, quote the exact PIR claim and the exact thread evidence (or note its absence).
- Be calibrated: not every inference is a hallucination. Focus on material factual errors.
- Output valid JSON only."""

VERIFICATION_SCHEMA = """
{
  "overall_confidence": "high|medium|low",
  "confidence_rationale": "string",
  "findings": [
    {
      "severity": "critical|warning|note",
      "type": "hallucination|misattribution|false_certainty|unsupported_inference|verified",
      "pir_section": "string (e.g. 'Timeline', 'Root Cause', 'Customer Impact')",
      "claim": "string (exact claim from PIR)",
      "thread_evidence": "string (supporting quote from thread, or 'Not found in thread')",
      "recommendation": "string (how to fix or caveat this)"
    }
  ],
  "verified_facts": ["string (key facts confirmed accurate — quote both PIR claim and thread source)"],
  "missing_from_pir": ["string (material facts in thread that PIR omitted)"],
  "summary": "string (2-3 sentence overall assessment)"
}
"""

def run(slack_thread: str, pir_markdown: str) -> dict:
    prompt = f"""Fact-check this PIR document against the original Slack thread.

Follow this JSON schema exactly:
{VERIFICATION_SCHEMA}

ORIGINAL SLACK THREAD (ground truth):
{slack_thread}

PIR DOCUMENT TO VERIFY:
{pir_markdown}"""

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
