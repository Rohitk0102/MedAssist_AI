#!/usr/bin/env bash

set -euo pipefail

# Resolve directories
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$BASE_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}MedAssist AI - Starter${NC}"
echo "Base Dir: $BASE_DIR"

# Select python
if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

# Create venv if missing
if [ ! -d "$BASE_DIR/.venv" ]; then
  echo -e "${YELLOW}Creating virtual environment (.venv)...${NC}"
  "$PY" -m venv "$BASE_DIR/.venv"
fi

# Activate venv
source "$BASE_DIR/.venv/bin/activate"

# Upgrade pip and install requirements
echo -e "${YELLOW}Installing requirements...${NC}"
pip install -U pip >/dev/null
if [ -f "$BASE_DIR/requirements.txt" ]; then
  pip install -r "$BASE_DIR/requirements.txt"
fi

# Load .env if present
if [ -f "$BASE_DIR/.env" ]; then
  echo -e "${YELLOW}Loading .env...${NC}"
  set -a
  # shellcheck disable=SC1090
  source "$BASE_DIR/.env"
  set +a
fi

# Ensure PYTHONPATH includes workspace root so MedAssist_AI can be imported as a package
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH:-}"

usage() {
  cat <<EOF
Usage: ./start.sh [command]

Commands:
  setup-emr       Initialize SQLite EMR (patients.db) with sample data
  demo-emr        Run the EMR demo (non-interactive)
  demo-interactive Run the EMR interactive demo
  agent           Start the MedAssist AI scheduling agent
  status          Show EMR system status
  help            Show this help

Examples:
  ./start.sh setup-emr
  ./start.sh agent
  ./start.sh demo-emr
EOF
}

cmd="${1:-help}"

case "$cmd" in
  setup-emr)
    echo -e "${YELLOW}Initializing EMR system...${NC}"
    "$PY" -m MedAssist_AI.setup_emr setup | cat
    ;;
  demo-emr)
    echo -e "${YELLOW}Running EMR demo...${NC}"
    "$PY" -m MedAssist_AI.emr_demo | cat
    ;;
  demo-interactive)
    echo -e "${YELLOW}Running EMR interactive demo...${NC}"
    "$PY" -m MedAssist_AI.emr_demo interactive | cat
    ;;
  agent)
    echo -e "${YELLOW}Starting MedAssist AI agent...${NC}"
    "$PY" -c "import sys; sys.path.append('$PROJECT_ROOT'); import MedAssist_AI.agent as a; print('Agent loaded:', hasattr(a,'medassist_agent'))" | cat
    echo -e "${GREEN}Agent module is ready. Integrate via ADK or import MedAssist_AI.agent.medassist_agent in your app.${NC}"
    ;;
  status)
    echo -e "${YELLOW}Showing EMR system status...${NC}"
    "$PY" -m MedAssist_AI.setup_emr status | cat
    ;;
  help|*)
    usage
    ;;
esac


