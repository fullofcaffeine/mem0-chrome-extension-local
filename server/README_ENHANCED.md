# Enhanced Local Mem0 Server

## 🎯 **What is This?**

The **Enhanced Local Mem0 Server** combines the best features from the official [mem0ai/mem0 server](https://github.com/mem0ai/mem0) with our local-specific enhancements. It provides a production-ready memory server that runs entirely on your machine using Ollama + Qdrant.

## 🚀 **Key Enhancements Over Original**

### ✅ **Official Mem0 Server Features Added**
- **Production-ready FastAPI architecture** with proper error handling
- **Enhanced Pydantic models** with comprehensive validation
- **Official API endpoints** (`/v1/memories`, `/v1/memories/search`, etc.)
- **OpenAPI documentation** with Swagger UI at `/docs`
- **Comprehensive health checks** and service monitoring
- **Statistics and analytics** endpoints
- **Authentication-ready** architecture (optional)

### ✅ **Our Local-Specific Enhancements Kept**
- **Ollama integration** for local LLM processing
- **Qdrant integration** for local vector storage
- **Relevance filtering** (0.4 threshold) to prevent irrelevant memories
- **Chrome extension compatibility** 
- **Complete privacy** - no external API calls

### ✅ **New Production Features**
- **Enhanced pagination** with proper metadata
- **Session ID tracking** for conversation management
- **Comprehensive logging** with structured output
- **Environment-based configuration**
- **Automated testing suite** with 12 comprehensive tests
- **Performance monitoring** and concurrency testing

## 📊 **Feature Comparison**

| Feature | Original Local | Enhanced Local | Official Server |
|---------|---------------|----------------|-----------------|
| **Core Functionality** |
| Memory CRUD Operations | ✅ | ✅ | ✅ |
| Semantic Search | ✅ | ✅ | ✅ |
| Chrome Extension Support | ✅ | ✅ | ❌ |
| **Local Infrastructure** |
| Ollama LLM Integration | ✅ | ✅ | ❌ |
| Qdrant Vector Store | ✅ | ✅ | ❌ |
| Relevance Filtering | ✅ | ✅ | ❌ |
| **Production Features** |
| Pydantic Validation | ❌ | ✅ | ✅ |
| OpenAPI Documentation | ❌ | ✅ | ✅ |
| Comprehensive Error Handling | ❌ | ✅ | ✅ |
| Health Check Endpoints | Basic | ✅ | ✅ |
| Statistics & Analytics | ❌ | ✅ | ✅ |
| **Advanced Features** |
| Enhanced Pagination | ❌ | ✅ | ✅ |
| Session Management | ❌ | ✅ | ✅ |
| Authentication Ready | ❌ | ✅ | ✅ |
| Automated Testing | ❌ | ✅ | ✅ |
| Performance Monitoring | ❌ | ✅ | ✅ |

## 🛠 **Installation & Setup**

### Prerequisites
- Python 3.8+
- Ollama installed and running
- Qdrant running in Docker
- Virtual environment activated

### Quick Start

```bash
# 1. Ensure services are running
brew services start ollama  # or: ollama serve
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

# 2. Start enhanced server
cd mem0-server
./start_enhanced_mem0.sh

# 3. View API documentation
open http://localhost:8000/docs
```

## 📚 **API Documentation**

### Enhanced Endpoints

#### **POST /v1/memories** - Create Memories
```json
{
  "messages": [
    {"role": "user", "content": "I love Python programming"},
    {"role": "assistant", "content": "Python is great!"}
  ],
  "user_id": "user123",
  "metadata": {"priority": "high"},
  "session_id": "session-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully created 2 memories",
  "data": {
    "memories_created": 2,
    "session_id": "session-uuid",
    "results": [...]
  },
  "timestamp": "2025-01-06T10:30:00Z"
}
```

#### **POST /v1/memories/search** - Enhanced Search
```json
{
  "query": "Python programming",
  "user_id": "user123",
  "limit": 5,
  "threshold": 0.4
}
```

**Response:**
```json
{
  "success": true,
  "message": "Found 3 relevant memories",
  "data": {
    "results": [...],
    "total_found": 5,
    "filtered_out": 2,
    "threshold_used": 0.4
  }
}
```

#### **GET /v1/memories** - Paginated Retrieval
```bash
GET /v1/memories?user_id=user123&limit=10&offset=0
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [...],
    "pagination": {
      "total": 25,
      "limit": 10,
      "offset": 0,
      "has_more": true
    }
  }
}
```

#### **GET /v1/stats** - Statistics
```json
{
  "success": true,
  "data": {
    "user_id": "user123",
    "total_memories": 15,
    "server_uptime": 3600.5
  }
}
```

### Health & Status Endpoints

- **GET /** - Server status and capabilities
- **GET /health** - Comprehensive health check
- **GET /v1/extension/** - Chrome extension verification

## 🧪 **Testing**

### Automated Test Suite

Run the comprehensive test suite:

```bash
cd mem0-server
python3 tests/test_enhanced_server.py
```

**Test Coverage:**
1. ✅ Server health and status
2. ✅ Root endpoint with enhanced info
3. ✅ Chrome extension compatibility
4. ✅ Enhanced memory creation with validation
5. ✅ Advanced search with relevance filtering
6. ✅ Pagination and memory retrieval
7. ✅ Statistics and analytics
8. ✅ Error handling and validation
9. ✅ Full CRUD operations
10. ✅ Legacy endpoint compatibility
11. ✅ Performance and concurrency
12. ✅ API documentation generation

### Manual Testing

```bash
# Test memory creation
curl -X POST http://localhost:8000/v1/memories \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"I love FastAPI"}],"user_id":"test"}'

# Test search with threshold
curl -X POST http://localhost:8000/v1/memories/search \
  -H "Content-Type: application/json" \
  -d '{"query":"FastAPI","user_id":"test","threshold":0.4}'

# Test pagination
curl "http://localhost:8000/v1/memories?user_id=test&limit=5&offset=0"

# Test stats
curl "http://localhost:8000/v1/stats?user_id=test"
```

## 🔧 **Configuration**

### Environment Variables

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export QDRANT_HOST="localhost"
export QDRANT_PORT="6333"
export LLM_MODEL="llama3.1:latest"
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

### Server Options

```bash
# Custom host and port
./start_enhanced_mem0.sh 127.0.0.1 8080

# Debug mode
python3 enhanced_local_mem0.py --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## 🎯 **Use Cases**

### 1. **Local AI Development**
- Build AI applications with persistent memory
- Test memory-enhanced LLM interactions
- Develop context-aware chatbots

### 2. **Chrome Extension Backend**
- Store memories across ChatGPT, Claude, Perplexity
- Cross-platform memory sharing
- Private, local memory management

### 3. **Production-Ready Deployment**
- Use as backend for AI applications
- API integration with existing systems
- Comprehensive monitoring and logging

## 🚀 **Performance**

### **Benchmarks**
- **Memory Creation:** ~500ms average
- **Search Operations:** ~200ms average  
- **Concurrent Requests:** 5+ simultaneous (tested)
- **Relevance Filtering:** <50ms additional overhead

### **Scalability**
- **Memory Storage:** Limited by Qdrant disk space
- **Concurrent Users:** Scales with hardware
- **Search Performance:** O(log n) with Qdrant indexing

## 🔒 **Security**

### **Current Security**
- No authentication required (local development)
- CORS enabled for local development
- All data stored locally

### **Production Security Options**
```python
# Enable Bearer token authentication
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials
```

## 🐛 **Troubleshooting**

### Common Issues

**1. Server won't start**
```bash
# Check if services are running
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:6333/collections  # Qdrant
```

**2. Memory creation fails**
```bash
# Check Ollama model
ollama list
ollama pull llama3.1:latest  # If missing
```

**3. Search returns no results**
- Wait 2-3 seconds after creating memories (indexing delay)
- Lower search threshold: `"threshold": 0.2`
- Check user_id matches between creation and search

**4. Tests fail**
```bash
# Ensure server is running first
./start_enhanced_mem0.sh
# Then run tests in separate terminal
python3 tests/test_enhanced_server.py
```

## 📋 **Migration from Original**

### **Zero-Effort Migration**
The enhanced server is **100% backward compatible**:

1. Stop original server: `Ctrl+C`
2. Start enhanced server: `./start_enhanced_mem0.sh`
3. All existing Chrome extension functionality works unchanged
4. Existing memories are preserved in Qdrant

### **New Features Available Immediately**
- Enhanced API responses at same endpoints
- Swagger UI documentation at `/docs`
- Statistics endpoint at `/v1/stats`
- Improved error messages and validation

## 🤝 **Contributing**

### **Architecture**
- **FastAPI** - Modern async Python framework
- **Pydantic** - Data validation and settings management
- **Mem0** - Core memory management library
- **Ollama** - Local LLM inference
- **Qdrant** - Vector similarity search

### **Code Structure**
```
mem0-server/
├── enhanced_local_mem0.py      # Main server implementation
├── start_enhanced_mem0.sh      # Startup script  
├── tests/
│   └── test_enhanced_server.py # Comprehensive test suite
└── README_ENHANCED.md          # This documentation
```

## 📄 **License**

Same as the main project - follows the original repository's licensing.

---

## 🎉 **Ready to Try?**

```bash
cd mem0-server
./start_enhanced_mem0.sh
open http://localhost:8000/docs
```

**The enhanced server gives you the best of both worlds:**
- 🏠 **Local privacy** with Ollama + Qdrant
- 🏭 **Production features** from official mem0 server
- 🔧 **Chrome extension compatibility** maintained
- 📈 **Enhanced performance** and monitoring

**Perfect for developers who want enterprise-grade features with complete local control!** 🚀 
