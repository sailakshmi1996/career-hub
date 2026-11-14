#!/bin/bash
set -e

# Deployment wrapper script for sailakshminl.netlify.app
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"
python3 "$SCRIPT_DIR/deploy_netlify.py"
