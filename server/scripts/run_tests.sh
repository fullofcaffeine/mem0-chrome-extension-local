#!/bin/bash
# Run the Python test-suite against a fresh instance of the local Mem0 server.
#
# The script will:
#   1. Launch scripts/start_mem0.sh in the background.
#   2. Wait until the /health endpoint responds (max 40s).
#   3. Execute pytest (unit + integration tests).
#   4. Terminate the background server and report results.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
START_SCRIPT="$ROOT_DIR/scripts/start_mem0.sh"
SERVER_URL="http://localhost:8000/health"

if [[ ! -x "$START_SCRIPT" ]]; then
  echo "❌ Cannot execute $START_SCRIPT. Make sure it exists and is chmod +x."
  exit 1
fi

# ---------------------------------------------------------------------------
# 1. Launch server in background
# ---------------------------------------------------------------------------

printf "🚀  Launching Mem0 server in background for tests...\n"
MEM0_TEST_MODE=1 "$START_SCRIPT" &
SERVER_PID=$!
trap 'echo "\n🛑  Stopping Mem0 server (PID $SERVER_PID)"; kill $SERVER_PID 2>/dev/null || true' EXIT

# ---------------------------------------------------------------------------
# 2. Wait for health endpoint
# ---------------------------------------------------------------------------
MAX_WAIT=40
until curl -s "$SERVER_URL" > /dev/null; do
  [[ $MAX_WAIT -le 0 ]] && { echo "❌  Server did not start within expected time"; exit 1; }
  printf "."; sleep 2; MAX_WAIT=$((MAX_WAIT-2))
done
printf "\n✅  Server is up. Running tests...\n"

# ---------------------------------------------------------------------------
# 3. Run pytest (inside virtual-env)
# ---------------------------------------------------------------------------
VENV_DIR="$ROOT_DIR/mem0_env"

PYTEST="$VENV_DIR/bin/pytest"
if [[ -x "$PYTEST" ]]; then
  cd "$ROOT_DIR"
  "$PYTEST" -q
else
  echo "⚠️  pytest not found in virtual env – falling back to python -m pytest"
  "$VENV_DIR/bin/python" -m pytest -q
fi

# Result captured by trap cleanup on exit 
