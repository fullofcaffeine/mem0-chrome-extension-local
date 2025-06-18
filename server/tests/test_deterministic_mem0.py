#!/usr/bin/env python3
"""
Deterministic Tests for Local Mem0 Server
Tests API endpoints and infrastructure without LLM variability
"""

import requests
import json
import time
import sys
import uuid
from datetime import datetime

# Server configuration
BASE_URL = "http://localhost:8000"
USER_ID = f"test-user-{uuid.uuid4().hex[:8]}"  # Unique user per test run

def test_server_health():
    """Test 1: Server health and component status"""
    print("🔍 Test 1: Server Health")
    try:
        response = requests.get(f"{BASE_URL}/")
        data = response.json()
        
        assert response.status_code in [200, 201]
        assert data["status"] == "running"
        assert data["mem0_initialized"] == True
        assert "llm" in data["components"]
        assert "vector_store" in data["components"]
        assert "embeddings" in data["components"]
        
        print("✅ Server health check passed")
        print(f"   LLM: {data['components']['llm']}")
        print(f"   Vector Store: {data['components']['vector_store']}")
        print(f"   Embeddings: {data['components']['embeddings']}")
    except Exception as e:
        print(f"❌ Server health test failed: {e}")
        raise

def test_extension_verification():
    """Test 2: Extension verification endpoint"""
    print("\n🔍 Test 2: Extension Verification")
    try:
        response = requests.get(f"{BASE_URL}/v1/extension/")
        data = response.json()
        
        assert response.status_code in [200, 201]
        assert data["success"] == True
        assert data["message"] == "Extension verified"
        assert data["server_type"] == "local_mem0_with_rag"
        
        print("✅ Extension verification passed")
    except Exception as e:
        print(f"❌ Extension verification test failed: {e}")
        raise

def test_api_endpoints_structure():
    """Test 3: API endpoint structure (without LLM processing)"""
    print("\n🔍 Test 3: API Endpoint Structure")
    try:
        # Test search endpoint with empty query (should not process through LLM)
        search_response = requests.post(f"{BASE_URL}/v1/memories/search/", json={
            "query": "",  # Empty query to avoid LLM processing
            "user_id": USER_ID,
            "limit": 1
        })
        
        assert search_response.status_code in [200, 201]
        search_data = search_response.json()
        assert "success" in search_data
        assert "data" in search_data and "results" in search_data["data"]
        
        # Test health endpoint
        health_response = requests.get(f"{BASE_URL}/health")
        assert health_response.status_code in [200, 201]
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        
        print("✅ API endpoint structure tests passed")
    except Exception as e:
        print(f"❌ API endpoint structure test failed: {e}")
        raise

def test_qdrant_connectivity():
    """Test 4: Qdrant vector database connectivity"""
    print("\n🔍 Test 4: Qdrant Connectivity")
    try:
        # Test Qdrant directly
        qdrant_response = requests.get("http://localhost:6333/")
        assert qdrant_response.status_code in [200, 201]
        
        # Test collections endpoint
        collections_response = requests.get("http://localhost:6333/collections")
        assert collections_response.status_code in [200, 201]
        collections_data = collections_response.json()
        
        # Check if our mem0 collections exist
        collection_names = [col["name"] for col in collections_data.get("result", {}).get("collections", [])]
        assert "mem0_memories" in collection_names
        
        print("✅ Qdrant connectivity test passed")
        print(f"   Collections: {collection_names}")
    except Exception as e:
        print(f"❌ Qdrant connectivity test failed: {e}")
        raise

def test_ollama_connectivity():
    """Test 5: Ollama LLM connectivity"""
    print("\n🔍 Test 5: Ollama Connectivity")
    try:
        # Test Ollama version endpoint
        ollama_response = requests.get("http://localhost:11434/api/version")
        assert ollama_response.status_code in [200, 201]
        ollama_data = ollama_response.json()
        
        # Test if our model is available
        tags_response = requests.get("http://localhost:11434/api/tags")
        assert tags_response.status_code in [200, 201]
        tags_data = tags_response.json()
        
        model_names = [model["name"] for model in tags_data.get("models", [])]
        llama_models = [name for name in model_names if "llama" in name.lower()]
        
        print("✅ Ollama connectivity test passed")
        print(f"   Version: {ollama_data.get('version', 'unknown')}")
        print(f"   Available Llama models: {llama_models}")
    except Exception as e:
        print(f"❌ Ollama connectivity test failed: {e}")
        raise

def test_embeddings_functionality():
    """Test 6: Embeddings generation (deterministic)"""
    print("\n🔍 Test 6: Embeddings Functionality")
    try:
        # Test with a fixed, simple text that should always produce the same embedding
        test_text = "hello world"
        
        # We can't directly test the embeddings API, but we can test that search
        # with the same query returns consistent structure
        search_response_1 = requests.post(f"{BASE_URL}/v1/memories/search/", json={
            "query": test_text,
            "user_id": USER_ID,
            "limit": 1
        })
        
        search_response_2 = requests.post(f"{BASE_URL}/v1/memories/search/", json={
            "query": test_text,
            "user_id": USER_ID,
            "limit": 1
        })
        
        assert search_response_1.status_code in [200, 201]
        assert search_response_2.status_code in [200, 201]
        
        data_1 = search_response_1.json()
        data_2 = search_response_2.json()
        
        # Structure should be identical
        assert data_1.keys() == data_2.keys()
        assert data_1["success"] == data_2["success"]
        
        print("✅ Embeddings functionality test passed")
    except Exception as e:
        print(f"❌ Embeddings functionality test failed: {e}")
        raise

def test_memory_crud_operations():
    """Test 7: Memory CRUD operations (deterministic parts)"""
    print("\n🔍 Test 7: Memory CRUD Operations")
    try:
        # Test that we can call the add memory endpoint
        # (We won't validate the LLM-processed results, just the API response structure)
        add_response = requests.post(f"{BASE_URL}/v1/memories/", json={
            "messages": [
                {"role": "user", "content": "deterministic test message"},
                {"role": "assistant", "content": "deterministic test response"}
            ],
            "user_id": USER_ID,
            "metadata": {"test": "deterministic", "timestamp": "2024-01-01T00:00:00Z"}
        })
        
        assert add_response.status_code in [200, 201]  # Accept both 200 and 201
        add_data = add_response.json()
        assert add_data["success"] == True
        assert "message" in add_data
        assert "data" in add_data and "results" in add_data["data"]
        
        # Test search structure (not content)
        search_response = requests.post(f"{BASE_URL}/v1/memories/search/", json={
            "query": "deterministic",
            "user_id": USER_ID,
            "limit": 5
        })
        
        assert search_response.status_code in [200, 201]
        search_data = search_response.json()
        assert search_data["success"] == True
        assert "data" in search_data and "results" in search_data["data"]
        
        # Validate result structure (if any results exist)
        if search_data["data"].get("results"):
            for result in search_data["data"]["results"]:
                assert "id" in result
                assert "memory" in result
                assert "score" in result
                assert "user_id" in result
                assert result["user_id"] == USER_ID
        
        print("✅ Memory CRUD operations test passed")
    except Exception as e:
        print(f"❌ Memory CRUD operations test failed: {e}")
        raise

def test_api_error_handling():
    """Test 8: API error handling"""
    print("\n🔍 Test 8: API Error Handling")
    try:
        # Test invalid endpoint
        invalid_response = requests.get(f"{BASE_URL}/invalid/endpoint")
        assert invalid_response.status_code == 404
        
        # Test malformed JSON
        malformed_response = requests.post(f"{BASE_URL}/v1/memories/search/", 
                                         data="invalid json",
                                         headers={"Content-Type": "application/json"})
        assert malformed_response.status_code == 422
        
        # Test missing required fields
        missing_fields_response = requests.post(f"{BASE_URL}/v1/memories/search/", json={})
        assert missing_fields_response.status_code == 422
        
        print("✅ API error handling test passed")
    except Exception as e:
        print(f"❌ API error handling test failed: {e}")
        raise

def run_deterministic_tests():
    """Run all deterministic tests"""
    print("🧠 Deterministic Local Mem0 Test Suite")
    print("=" * 50)
    print(f"Using unique test user: {USER_ID}")
    print("=" * 50)
    
    tests = [
        test_server_health,
        test_extension_verification,
        test_api_endpoints_structure,
        test_qdrant_connectivity,
        test_ollama_connectivity,
        test_embeddings_functionality,
        test_memory_crud_operations,
        test_api_error_handling
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All deterministic tests passed!")
        print("🔧 Your local Mem0 infrastructure is working correctly!")
    else:
        print("⚠️  Some tests failed. Infrastructure issues detected.")
    
    print("\n📝 Note: These tests validate infrastructure and APIs,")
    print("   not LLM output variability (which is expected).")
    
    return passed == total

if __name__ == "__main__":
    success = run_deterministic_tests()
    sys.exit(0 if success else 1) 
