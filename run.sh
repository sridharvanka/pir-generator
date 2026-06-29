#!/bin/bash
# PIR Generator — startup script
# Usage: ANTHROPIC_API_KEY=sk-... ./run.sh

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "ERROR: ANTHROPIC_API_KEY is not set."
  echo "Usage: ANTHROPIC_API_KEY=sk-... ./run.sh"
  exit 1
fi

pip install -r requirements.txt -q
python app.py
