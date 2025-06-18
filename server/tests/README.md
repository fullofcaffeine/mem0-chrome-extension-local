# Local Mem0 Test Suite

This directory contains comprehensive tests for the local Mem0 implementation.

## 🚀 Quick Start

```bash
# From project root, run comprehensive tests
source mem0_env/bin/activate
cd mem0-server/tests
python3 test_comprehensive.py
```

## 📁 Test Files

### Core Test Suites
- **`test_comprehensive.py`** - Combined test suite (recommended)
- **`test_deterministic_mem0.py`** - Infrastructure tests (100% reliable)  
- **`test_llm_intention.py`** - LLM effectiveness tests (integration/E2E)

### Quality Assessment Tests
- **`test_quality_focused.py`** - Focused memory quality demonstration
- **`test_memory_quality.py`** - Detailed memory extraction analysis

### Documentation
- **`TESTING_GUIDE.md`** - Comprehensive testing documentation
- **`MEMORY_QUALITY_ANALYSIS.md`** - Memory quality assessment and comparison

## 🎯 Test Philosophy

Our tests use **intention-based validation** rather than exact output matching:
- ✅ Tests if LLM makes good decisions
- ✅ Validates memory extraction quality  
- ✅ Checks semantic usefulness
- ❌ Doesn't test exact text outputs (which are non-deterministic)

## 📊 Expected Results

**Infrastructure Tests:** 100% pass rate (deterministic)  
**LLM Tests:** 80%+ pass rate (excellent), 60%+ acceptable  
**Overall System:** EXCELLENT or GOOD status

## 🔧 Prerequisites

1. **All services running:**
   ```bash
   cd ../  # Go to mem0-server directory
   ./start_local_mem0_rag.sh
   ```

2. **Virtual environment activated:**
   ```bash
   source ../../mem0_env/bin/activate
   ```

3. **Model downloaded:**
   ```bash
   ollama list  # Should show llama3.1:latest
   ```

## 🧠 What Gets Tested

### Memory Quality
- Intelligent fact extraction from conversations
- Smart filtering of irrelevant content (weather, greetings)
- Contextual decision making (ADD/UPDATE/DELETE operations)
- Semantic search effectiveness

### System Integration  
- Server health and API functionality
- Qdrant vector database connectivity
- Ollama LLM service integration
- HuggingFace embeddings processing
- End-to-end conversation processing

### Performance
- Response times (10-20s expected for local LLM)
- Memory extraction efficiency
- Search accuracy and relevance

For detailed testing information, see `TESTING_GUIDE.md`. 
