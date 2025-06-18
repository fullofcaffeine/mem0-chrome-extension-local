#!/bin/bash

# Unified launcher for the local Mem0 stack (vector DB + FastAPI RAG server)
# Usage:  ./scripts/start_mem0.sh
#
# The script assumes the following repo layout:
#   ├── mem0_env/                # Python venv created by setup_env.py
#   ├── mem0-server/
#   │     └── local_mem0_with_rag.py
#   └── scripts/start_mem0.sh (this file)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/mem0_env"
SERVER_DIR="$ROOT_DIR/mem0-server"

printf "\n🚀  Starting local Mem0 stack (FastAPI + Qdrant + Ollama)\n"
printf "========================================================\n"

# Kill previous Mem0 server if still running (avoid port conflicts during tests)
pkill -f local_mem0_with_rag.py 2>/dev/null || true
lsof -ti tcp:8000 | xargs kill -9 2>/dev/null || true

# ---------------------------------------------------------------------------
# Ensure Python virtual-env exists ------------------------------------------------
# ---------------------------------------------------------------------------
if [[ ! -d "$VENV_DIR" ]]; then
  echo "❌  Virtual environment not found at $VENV_DIR"
  echo "➡️   Run:  python mem0-server/setup_env.py"
  exit 1
fi

# Activate env
source "$VENV_DIR/bin/activate"
printf "✅  Virtual environment activated (python: $(python -V))\n"

# ---------------------------------------------------------------------------
# Pre-warm Hugging Face embedder model (MiniLM) so Mem0 starts offline
# ---------------------------------------------------------------------------
MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
HF_CACHE_DIR="$SERVER_DIR/hf_models"
export HF_HOME="$HF_CACHE_DIR"
export MODEL_NAME="$MODEL_NAME"

if [[ ! -d "$HF_CACHE_DIR" ]]; then
  mkdir -p "$HF_CACHE_DIR"
fi

# Warm-up in a subshell so the here-doc doesn't break the main script
( python - <<'PY'
from pathlib import Path
import sys, traceback
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    sys.exit(1)

import os
model_name = os.environ['MODEL_NAME']
model_dir = Path(os.environ['HF_HOME']) / ('models--' + '-'.join(model_name.split('/')))
if not model_dir.exists():
    try:
        print('🔄  Downloading HF embedding model for offline cache…')
        SentenceTransformer(model_name)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
PY
 ) || echo "⚠️  Embedding model warm-up failed (will download at runtime)."

# ---------------------------------------------------------------------------
# Ensure Ollama is up -----------------------------------------------------------
# ---------------------------------------------------------------------------
printf "🔍  Checking Ollama status...\n"
if ! curl -s http://localhost:11434/api/version > /dev/null; then
  echo "⏳  Ollama not detected. Attempting to start with 'brew services start ollama'..."
  brew services start ollama || true
  sleep 5
fi
if curl -s http://localhost:11434/api/version > /dev/null; then
  echo "✅  Ollama is running"
else
  echo "⚠️  Ollama still not responding. Continuing anyway — embeddings may fail."
fi

# ---------------------------------------------------------------------------
# Ensure Qdrant is up -----------------------------------------------------------
# ---------------------------------------------------------------------------
printf "🔍  Checking Qdrant status...\n"
if ! curl -s http://localhost:6333/ > /dev/null; then
  echo "⏳  Qdrant not detected. Launching Docker container..."
  docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
    -v "$SERVER_DIR/qdrant_storage:/qdrant/storage:z" qdrant/qdrant
  sleep 10
fi
curl -s http://localhost:6333/ > /dev/null && echo "✅  Qdrant is running"

# ---------------------------------------------------------------------------
# Start FastAPI server ----------------------------------------------------------
# ---------------------------------------------------------------------------
printf "\n🎯  All components ready! Launching API server...\n"
cd "$SERVER_DIR"
exec python3 local_mem0_with_rag.py 
