# 🧠 Mem0 Chrome Extension - Local RAG Edition

A **fully local** Chrome extension that brings intelligent memory capabilities to your AI conversations. Built on the [original Mem0 Chrome Extension](https://github.com/mem0ai/mem0-chrome-extension) with complete local processing - no API keys required, complete privacy guaranteed.

**🔬 Experimental Note**: This project was created as an experiment to provide a self-contained mem0 server for clients that don't support MCP (Model Context Protocol) and for users who prefer local processing over cloud-based solutions. This work predates the availability of the [OpenMemory MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory), which now provides official MCP support for memory capabilities.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Built with Mem0](https://img.shields.io/badge/built%20with-Mem0-purple.svg)](https://mem0.ai/)

## 🎯 What This Is

This project transforms AI conversations across multiple platforms by adding intelligent memory that:
- **Remembers** important details from your conversations
- **Understands** context and relationships using local AI
- **Retrieves** relevant memories when needed
- **Works** across ChatGPT, Claude, Perplexity, Grok, and DeepSeek
- **Stays** completely private on your machine

## 🏗️ Architecture

```
Chrome Extension ←→ Local Mem0 Server ←→ Ollama (LLM) + Qdrant (Vector DB)
                                      ↘ HuggingFace Embeddings (Local)
```

**Key Components:**
- **Chrome Extension**: Captures conversations and injects relevant memories
- **Local Mem0 Server**: Official mem0 library configured for local processing
- **Ollama**: Local LLM for intelligent memory extraction and processing
- **Qdrant**: Local vector database for semantic memory search
- **HuggingFace**: Local embedding models for text vectorization

## 📁 Repository Structure

```
mem0-chrome-extension-local/
├── 📁 docs/                          # Documentation
├── 📁 extension/                     # Chrome Extension
│   ├── 📁 chatgpt/                   # ChatGPT content scripts
│   ├── 📁 claude/                    # Claude content scripts  
│   ├── 📁 deepseek/                  # DeepSeek content scripts
│   ├── 📁 grok/                      # Grok content scripts
│   ├── 📁 perplexity/                # Perplexity content scripts
│   ├── 📁 icons/                     # Extension icons
│   ├── 📄 manifest.json              # Extension manifest
│   ├── 📄 popup.html                 # Extension popup UI
│   ├── 📄 popup.js                   # Popup functionality
│   ├── 📄 sidebar.js                 # Memory sidebar
│   └── 📄 background.js              # Background service worker
├── 📁 server/                        # Local Mem0 Server
│   ├── 📁 scripts/                   # CLI scripts and utilities
│   │   ├── 📄 setup_env.py           # Environment setup
│   │   ├── 📄 start_mem0.py          # Server startup
│   │   ├── 📄 run_tests.py           # Test runner
│   │   ├── 📄 list_memories.py       # Memory explorer
│   │   ├── 📄 start_mem0.sh          # Legacy shell script
│   │   └── 📄 run_tests.sh           # Test runner shell script
│   ├── 📁 tests/                     # Server tests
│   ├── 📁 hf_models/                 # HuggingFace models cache
│   ├── 📁 qdrant_storage/            # Qdrant vector database storage
│   ├── 📄 local_mem0_with_rag.py     # Main server application
│   ├── 📄 config.py                  # Server configuration
│   ├── 📄 configure_local.py         # Local configuration setup
│   ├── 📄 deterministic_llm_config.py # LLM configuration
│   ├── 📄 setup_env.py               # Environment setup (legacy)
│   └── 📄 README_ENHANCED.md         # Enhanced server documentation
├── 📁 tests/                         # Integration tests
│   ├── 📄 test_memory_behavior.py    # Memory system tests
│   ├── 📄 test_individual_memories.py # Individual memory tests
│   ├── 📄 test_search_improvements.py # Search functionality tests
│   ├── 📄 conftest.py                # Test configuration
│   └── 📄 pytest.ini                 # Test settings
├── 📁 mem0_chrome_extension.egg-info/ # Package metadata
├── 📄 README.md                      # This file
├── 📄 pyproject.toml                 # Project configuration & CLI commands
├── 📄 LICENSE                        # MIT License
└── 📄 .gitignore                     # Git ignore rules
```

### 📖 Directory Explanations

| Directory | Purpose | Why It Exists |
|-----------|---------|---------------|
| **`extension/`** | Contains all Chrome extension files organized by platform | Clean separation of browser extension code from server code |
| **`server/`** | Local Mem0 server implementation with RAG capabilities | Isolates server logic, making it potentially reusable for other interfaces |
| **`server/scripts/`** | CLI utilities and management scripts | Provides convenient command-line tools for setup, testing, and management |
| **`tests/`** | Integration and end-to-end tests | Tests the full system including Chrome extension + server interactions |
| **`docs/`** | Additional documentation (when needed) | Keeps the main README focused while providing detailed guides |

## 🚀 Quick Setup

### Prerequisites

- **macOS** (M2/Intel) or **Linux** (Windows via WSL)
- **Python 3.8+** 
- **Google Chrome**
- **Docker** (for Qdrant vector database)
- **Homebrew** (macOS) or package manager

### 1. Install System Dependencies

```bash
# Install Ollama (Local LLM)
brew install ollama

# Install Docker (for Qdrant)
brew install docker
# OR: Download Docker Desktop from docker.com

# Start Docker if not running
open -a Docker  # macOS
```

### 2. Setup Project Environment

```bash
# Clone this repository
git clone <repository-url>
cd mem0-chrome-extension-local

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the project in editable mode (this enables CLI commands)
pip install -e .

# Alternative: Install dependencies manually if above fails
pip install mem0ai fastapi uvicorn qdrant-client ollama sentence-transformers pytest pytest-asyncio httpx click rich requests
```

### 3. Verify CLI Commands Installation

```bash
# Test if CLI commands are available
mem0-setup --help

# If command not found, make sure you're in the virtual environment:
source .venv/bin/activate  # Reactivate if needed
pip install -e .           # Reinstall if needed
```

### 4. Setup Environment and Dependencies

```bash
# Run environment setup (checks and installs dependencies)
mem0-setup

# If CLI command fails, use Python directly:
python server/scripts/setup_env.py
```

### 5. Download AI Model

```bash
# Start Ollama service
brew services start ollama
# OR: ollama serve  (if brew services doesn't work)

# Download recommended model (8GB, ~5 minutes)
ollama pull llama3.1:latest

# Verify model is available
ollama list
```

### 6. Start the Server

```bash
# Activate virtual environment first
source .venv/bin/activate

# Start server with dependency checking
mem0-start --check-deps

# Alternative if CLI command fails:
python server/scripts/start_mem0.py --check-deps

# Manual server start (if scripts fail):
cd server
python local_mem0_with_rag.py
```

**Server Startup Verification:**
- 🌐 **Server**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- ❤️ **Health Check**: http://localhost:8000/health

### 7. Install Chrome Extension

1. **Open Chrome Extensions page**: Navigate to `chrome://extensions/` in your browser
2. **Enable Developer mode**: Toggle the **"Developer mode"** switch (top-right corner)
3. **Load the extension**: Click **"Load unpacked"** button
4. **Select extension folder**: Browse to your project and select the **`extension/`** folder
5. **Verify installation**: The Mem0 extension should now appear in your Chrome toolbar! 🎉

**Troubleshooting:**
- If you don't see the extension icon, click the puzzle piece icon in Chrome's toolbar
- Make sure the server is running (`mem0-start`) before using the extension
- Check the extension's console (Extensions page → Details → Inspect views) for any errors

## 🚨 Troubleshooting Setup Issues

### CLI Commands Not Found
```bash
# Ensure you're in the virtual environment
source .venv/bin/activate

# Reinstall the package
pip install -e .

# Verify installation
pip list | grep mem0-chrome-extension-local
```

### Server Won't Start
```bash
# Check if ports are available
lsof -i :8000  # Should be empty
lsof -i :6333  # Should show Qdrant if running

# Start services manually
brew services start ollama
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant

# Check service health
curl http://localhost:11434/api/version  # Ollama
curl http://localhost:6333/           # Qdrant
```

### Dependency Issues
```bash
# Clean install
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

### Extension Not Working
1. **Check server is running**: Visit http://localhost:8000/health
2. **Check browser console**: F12 → Console tab
3. **Verify extension permissions**: Extensions page → Details → Permissions
4. **Test API manually**:
   ```bash
   curl -X POST http://localhost:8000/v1/memories/search/ \
     -H "Content-Type: application/json" \
     -d '{"query":"test","user_id":"test","limit":5}'
   ```

## 🛠️ CLI Commands (Python's npm equivalent!)

This project includes npm-style commands using Python entry points:

```bash
# Setup environment and dependencies
mem0-setup [--force] [--python python3.11]

# Start the server with dependency checking
mem0-start [--check-deps] [--dev] [--port 8000]

# Run tests with various options
mem0-test [--type all|unit|integration|server] [--verbose] [--coverage] [--fail-fast] [--no-deps]

# Explore stored memories
mem0-list [--user-id USER] [--limit NUM] [--search "query"] [--format table|json|text] [--server URL] [--full]
```

**Example Usage:**
```bash
# Set up everything from scratch
mem0-setup --force

# Start server in development mode with dependency checks
mem0-start --check-deps --dev

# Run only integration tests with verbose output
mem0-test --type integration --verbose

# Search for memories about "Python programming" with full text
mem0-list --search "Python programming" --format table --full
```

## 🧪 Testing Your Setup

```bash
# Run comprehensive test suite
mem0-test --type all --verbose

# Test specific components
mem0-test --type server     # Server functionality
mem0-test --type integration # End-to-end tests
```

**Test Results:**
- ✅ **Infrastructure Tests**: API connectivity, dependencies
- ✅ **Memory Processing**: LLM extraction and storage  
- ✅ **Search Functionality**: Semantic search and retrieval
- ✅ **Extension Integration**: Chrome extension compatibility

## 🎮 Using the Extension

### Supported Platforms
- ✅ **ChatGPT** (chat.openai.com, chatgpt.com)
- ✅ **Claude** (claude.ai)
- ✅ **Perplexity** (perplexity.ai)
- ✅ **Grok** (grok.com, x.ai/grok)
- ✅ **DeepSeek** (chat.deepseek.com)

### How It Works
1. **Automatic**: Extension captures conversations as you chat
2. **Intelligent**: Local LLM extracts key information and insights
3. **Contextual**: Relevant memories are injected into new conversations
4. **Private**: Everything happens on your machine

### Controls
- **Sidebar**: Click the Mem0 icon to view/manage memories
- **Search**: Semantic search through your memory database
- **Manual**: Add/edit/delete memories manually
- **Keyboard**: `Ctrl+M` (or `Cmd+M`) to trigger memory injection

## ⚙️ Configuration

### Model Options

| Model | Size | RAM Required | Speed | Quality |
|-------|------|--------------|-------|---------|
| `llama3.1:8b` | 8GB | 16GB+ | Fast | Good |
| `gemma2:9b` | 9GB | 18GB+ | Fast | Very Good |
| `qwen2.5:7b` | 7GB | 14GB+ | Very Fast | Good |
| `llama3.1:70b` | 70GB | 64GB+ | Slow | Excellent |

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 16GB | 32GB+ |
| **Storage** | 20GB free | 50GB+ |
| **CPU** | 4 cores | 8+ cores |

## 🔧 Development

### Project Setup for Contributors

```bash
# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run code formatting
black .
isort .

# Type checking
mypy server/
```

### Architecture Notes

This is a **monorepo** containing:
1. **Chrome Extension** - Browser integration for multiple AI platforms
2. **Local Server** - Mem0-powered memory processing with RAG
3. **CLI Tools** - Management and utility scripts
4. **Tests** - Comprehensive test coverage

The design emphasizes:
- **Privacy**: All processing local, no external API calls
- **Modularity**: Clear separation between browser and server code
- **Usability**: Simple setup with intelligent defaults
- **Extensibility**: Easy to add new AI platforms or features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `mem0-test --type all`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Mem0](https://mem0.ai/) for the original chrome extension and memory framework
- [Ollama](https://ollama.ai/) for local LLM infrastructure
- [Qdrant](https://qdrant.tech/) for vector database capabilities
- [HuggingFace](https://huggingface.co/) for embedding models

---

**🚨 Privacy Notice**: This extension processes your conversations locally on your machine. No data is sent to external servers. All AI processing happens through your local Ollama installation.
