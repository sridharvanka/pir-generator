import os
import json
import sys
from flask import Flask, request, Response, send_from_directory
from agents import extractor, analyst, writer

app = Flask(__name__, static_folder="static")

# ── Static frontend ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# ── SSE pipeline endpoint ─────────────────────────────────────────────────────

def event(name: str, data) -> str:
    """Format a Server-Sent Event."""
    payload = json.dumps(data) if not isinstance(data, str) else data
    return f"event: {name}\ndata: {payload}\n\n"

@app.route("/generate", methods=["POST"])
def generate():
    slack_thread = request.json.get("slack_thread", "").strip()
    if not slack_thread:
        return {"error": "slack_thread is required"}, 400

    def stream():
        try:
            # ── Step 1: Extractor ──────────────────────────────────────────
            yield event("step", {"step": "extractor", "status": "running",
                                  "label": "Extracting facts from Slack thread..."})
            extracted = extractor.run(slack_thread)
            yield event("step", {"step": "extractor", "status": "done",
                                  "label": "Extraction complete",
                                  "data": extracted})

            # ── Step 2: Analyst ────────────────────────────────────────────
            yield event("step", {"step": "analyst", "status": "running",
                                  "label": "Analyzing root cause and contributing factors..."})
            analysis = analyst.run(extracted)
            yield event("step", {"step": "analyst", "status": "done",
                                  "label": "Analysis complete",
                                  "data": analysis})

            # ── Step 3: Writer ─────────────────────────────────────────────
            yield event("step", {"step": "writer", "status": "running",
                                  "label": "Writing PIR document..."})
            pir_markdown = writer.run(extracted, analysis)
            yield event("step", {"step": "writer", "status": "done",
                                  "label": "PIR ready",
                                  "data": {"markdown": pir_markdown}})

            yield event("done", {"message": "Pipeline complete"})

        except Exception as e:
            yield event("error", {"message": str(e)})

    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    print("PIR Generator running at http://localhost:5001")
    app.run(port=5001, debug=False)
