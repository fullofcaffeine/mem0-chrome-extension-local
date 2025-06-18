"""
Configuration for local mem0 setup
"""
import os

# Mem0 Configuration
MEM0_CONFIG = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "max_tokens": 1500,
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small"
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "mem0_local",
            "path": "./chroma_db",
        }
    },
}

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG = True

# Default user for Chrome extension
DEFAULT_USER_ID = "chrome-extension-user"

# OpenAI API Key (you'll need to set this)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here") 
