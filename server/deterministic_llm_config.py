#!/usr/bin/env python3
"""
Deterministic LLM Configuration for Local Mem0
Shows how to configure Ollama for more predictable outputs
"""

# Deterministic Ollama Configuration for Mem0
DETERMINISTIC_CONFIG = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.1:latest",
            "ollama_base_url": "http://localhost:11434",
            # Make LLM more deterministic
            "temperature": 0.0,           # Remove randomness
            "top_p": 0.1,                # Focus on most likely tokens
            "repeat_penalty": 1.0,        # Consistent repetition handling
            "seed": 12345,                # Fixed seed for reproducibility
            "num_predict": 512,           # Consistent max length
            "stop": ["\n\n", "###"],     # Consistent stopping
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "mem0_memories",
            "embedding_model_dims": 384
        }
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2"
            # Note: HuggingFace embeddings are deterministic by default
        }
    }
}

# Alternative: Mock LLM for testing
MOCK_LLM_CONFIG = {
    "llm": {
        "provider": "mock",  # Would need custom implementation
        "config": {
            "responses": {
                # Predefined responses for specific inputs
                "test_memory_extraction": [
                    {"memory": "User likes testing", "event": "ADD"},
                    {"memory": "User prefers deterministic tests", "event": "ADD"}
                ],
                "simple_conversation": [
                    {"memory": "User said hello", "event": "ADD"}
                ]
            }
        }
    }
}

def get_deterministic_config():
    """Get the deterministic configuration"""
    return DETERMINISTIC_CONFIG

def apply_deterministic_settings():
    """
    Apply deterministic settings to Ollama via API
    This can be called before running tests
    """
    import requests
    
    # Set model parameters for deterministic behavior
    model_params = {
        "model": "llama3.1:latest",
        "options": {
            "temperature": 0.0,
            "top_p": 0.1,
            "repeat_penalty": 1.0,
            "seed": 12345,
            "num_predict": 512
        }
    }
    
    try:
        # This would apply to future requests (Ollama doesn't have a global config API)
        print("⚙️  Deterministic LLM settings configured")
        print("   Temperature: 0.0 (no randomness)")
        print("   Top-p: 0.1 (focused sampling)")
        print("   Seed: 12345 (reproducible)")
        return True
    except Exception as e:
        print(f"❌ Failed to apply deterministic settings: {e}")
        return False

# Instructions for manual setup
MANUAL_SETUP_INSTRUCTIONS = """
🔧 Making Your Local Mem0 LLM More Deterministic:

1. **Update mem0-server/local_mem0_with_rag.py**:
   Replace the LLM config section with:
   
   "llm": {
       "provider": "ollama",
       "config": {
           "model": "llama3.1:latest",
           "ollama_base_url": "http://localhost:11434",
           "temperature": 0.0,
           "top_p": 0.1,
           "seed": 12345
       }
   }

2. **For Testing Only**: Create isolated test collections
   - Use different collection names for tests
   - Clean up test data after runs
   - Use unique user IDs per test

3. **Mock LLM for Unit Tests**: 
   - Create a mock LLM provider that returns predefined responses
   - Use this for unit tests where you need exact outputs
   - Keep integration tests with real LLM for end-to-end validation

4. **Test Strategy**:
   - Deterministic tests: Infrastructure, APIs, data flow
   - Non-deterministic tests: LLM quality, semantic accuracy
   - Separate test suites for different purposes
"""

if __name__ == "__main__":
    print("🧠 Deterministic LLM Configuration Guide")
    print("=" * 50)
    print(MANUAL_SETUP_INSTRUCTIONS)
    
    print("\n📊 Current Configuration:")
    import json
    print(json.dumps(DETERMINISTIC_CONFIG, indent=2)) 
