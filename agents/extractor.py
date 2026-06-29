import anthropic
import json

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an Extractor agent. Your only job is to pull structured facts from a Slack incident thread.
Do NOT interpret, explain, or reason. Extract only what is explicitly stated.
When something is uncertain or approximate, flag it with "approximate: true".
Output valid JSON only — no prose, no markdown fences."""

EXTRACTION_SCHEMA = """
{
  "incident_title": "string",
  "incident_date": "string",
  "channel": "string",
  "participants": [
    { "handle": "string", "role": "string or null" }
  ],
  "timeline": [
    {
      "timestamp": "HH:MM UTC",
      "actor": "string (person or system)",
      "event": "string (what happened, factual)",
      "approximate": true/false
    }
  ],
  "signals": [
    {
      "metric": "string",
      "value": "string",
      "timestamp": "string or null",
      "approximate": true/false
    }
  ],
  "systems_involved": ["string"],
  "root_cause_stated": "string or null (verbatim from thread, if explicitly stated)",
  "resolution_action": "string or null",
  "impact_numbers": [
    { "description": "string", "value": "string", "approximate": true/false }
  ],
  "action_items_mentioned": ["string"],
  "explicit_gaps": ["string (things the thread suggests happened but doesn't detail)"]
}
"""

def run(slack_thread: str) -> dict:
    prompt = f"""Extract all structured facts from this Slack incident thread.
Follow this JSON schema exactly:
{EXTRACTION_SCHEMA}

SLACK THREAD:
{slack_thread}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if model adds them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)
