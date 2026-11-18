#!/usr/bin/env bash
# Start Hungry Frog (creates the Python environment the first time)
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv && .venv/bin/pip install -q pygame-ce
fi
exec .venv/bin/python hungry_frog.py
