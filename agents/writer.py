import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a Writer agent. You produce polished, professional Post-Incident Review documents.

Style rules:
- Blameless language throughout — no individual blame, systems and processes only
- Clear, direct prose — no jargon unless technical precision requires it
- Flag approximate figures with "(estimated)"
- Flag inferred findings with "(inferred)"
- Open questions must appear as open questions, not assertions
- Use past tense for what happened, present tense for recommendations
- Output the full PIR as markdown"""

PIR_TEMPLATE = """# Post-Incident Review: {title}

**Date:** {date}
**Severity:** {severity}
**Duration:** {duration} minutes
**Status:** Resolved

---

## Summary

{summary paragraph — 3-5 sentences covering what happened, impact, and resolution}

---

## Timeline

| Time (UTC) | Event |
|------------|-------|
{timeline rows}

---

## Root Cause Analysis

### Trigger
{trigger}

### Root Cause
{root_cause}

### Causal Chain
{numbered causal chain}

---

## Contributing Factors

{contributing factors as prose paragraphs, grouped by type}

---

## Customer Impact

{impact section}

---

## Detection & Response

### How it was detected
{detection}

### Time to detect
{TTD} minutes

### Time to resolve
{TTR} minutes

---

## What Went Well

{bulleted list}

---

## Action Items

| Priority | Description | Type | Owner (Role) |
|----------|-------------|------|--------------|
{action item rows}

---

## Open Questions

{open questions as numbered list}

---

## Lessons Learned

{2-3 paragraph synthesis of key takeaways, written for a broad engineering audience}
"""

import json

def run(extracted: dict, analysis: dict) -> str:
    prompt = f"""Write a complete Post-Incident Review document using the extracted facts and analysis below.
Follow the PIR template structure. Use markdown formatting.
Write in blameless, professional prose throughout.

EXTRACTED FACTS:
{json.dumps(extracted, indent=2)}

ANALYSIS:
{json.dumps(analysis, indent=2)}

TEMPLATE STRUCTURE TO FOLLOW:
{PIR_TEMPLATE}

Produce the full PIR document now."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=6000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text
