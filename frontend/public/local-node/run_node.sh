#!/usr/bin/env bash
# ACASO Local Node launcher (Linux/macOS). Edit the two values below.
export ACASO_URL="https://contest-ready-app.preview.emergentagent.com"
export ACASO_KEY="PASTE_YOUR_AGENT_BRIDGE_KEY_HERE"
ROOT="$HOME/ACASO"
mkdir -p "$ROOT"
exec python3 "$(dirname "$0")/acaso_node.py" --root "$ROOT" --shell --browser
