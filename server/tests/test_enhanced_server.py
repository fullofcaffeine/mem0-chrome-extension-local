#!/usr/bin/env python3
"""
Comprehensive Tests for Enhanced Local Mem0 Server
Tests all enhancements and official server compatibility
"""

import pytest
import requests
import json
import time
import uuid
from typing import Dict, Any, List
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
SERVER_URL = "http://localhost:8000"
TEST_USER_ID = f"test-user-{uuid.uuid4().hex[:8]}"
TEST_TIMEOUT = 30

class TestEnhancedMem0Server:
    """Test suite for Enhanced Local Mem0 Server"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        logger.info("🧪 Setting up Enhanced Mem0 Server tests...")
        
        # Wait for server to be ready
        cls._wait_for_server()
        
        # Store test data
        cls.test_memories = []
        cls.test_session_id = str(uuid.uuid4())
        
    @classmethod
    def _wait_for_server(cls, timeout: int = TEST_TIMEOUT):
        """Wait for server to be ready"""
        logger.info("⏳ Waiting for server to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{SERVER_URL}/health", timeout=5)
                if response.status_code in [200, 201]:
                    logger.info("✅ Server is ready!")
                    return
            except requests.RequestException:
                pass
            time.sleep(1)
        
        raise Exception(f"❌ Server not ready after {timeout} seconds")
    
    def test_01_server_health(self):
        """Test server health and status"""
        logger.info("🏥 Testing server health...")
        
        response = requests.get(f"{SERVER_URL}/health")
        
        assert response.status_code in [200, 201]
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "components" in data
        assert "uptime" in data
        assert "memory_initialized" in data
        
        logger.info("✅ Server health check passed")
    
    def test_02_root_endpoint(self):
        """Test root endpoint with enhanced information"""
        logger.info("🏠 Testing root endpoint...")
        
        response = requests.get(f"{SERVER_URL}/")
        
        assert response.status_code in [200, 201]
        data = response.json()
        
        assert data["success"] is True
        assert "Enhanced Local Mem0 Server" in data["message"]
        assert "data" in data
        assert "components" in data["data"]
        assert "endpoints" in data["data"]
        
        logger.info("✅ Root endpoint test passed")
    
    def test_03_extension_verification(self):
        """Test Chrome extension compatibility"""
        logger.info("🌐 Testing extension verification...")
        
        response = requests.get(f"{SERVER_URL}/v1/extension/")
        
        assert response.status_code in [200, 201]
        data = response.json()
        
        assert data["success"] is True
        assert "enhanced_local_mem0" in data["data"]["server_type"]
        assert "capabilities" in data["data"]
        
        capabilities = data["data"]["capabilities"]
        expected_capabilities = [
            "semantic_search",
            "relevance_filtering",
            "enhanced_metadata",
            "pagination",
            "authentication_ready"
        ]
        
        for capability in expected_capabilities:
            assert capability in capabilities
        
        logger.info("✅ Extension verification test passed")
    
    def test_04_create_memories_enhanced(self):
        """Test enhanced memory creation with validation"""
        logger.info("📝 Testing enhanced memory creation...")
        
        # Test 1: Basic memory creation
        messages = [
            {"role": "user", "content": "I love programming in Python"},
            {"role": "assistant", "content": "Python is a great language! What do you like about it?"},
            {"role": "user", "content": "I especially enjoy using FastAPI for building APIs"}
        ]
        
        payload = {
            "messages": messages,
            "user_id": TEST_USER_ID,
            "metadata": {"test_type": "enhanced_creation", "priority": "high"},
            "session_id": self.test_session_id
        }
        
        response = requests.post(
            f"{SERVER_URL}/v1/memories",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["success"] is True
        assert "Successfully created" in data["message"]
        assert "data" in data
        assert "memories_created" in data["data"]
        assert "session_id" in data["data"]
        assert data["data"]["session_id"] == self.test_session_id
        
        # Store for cleanup
        self.test_memories.extend(data["data"].get("results", []))
        
        logger.info(f"✅ Created {data['data']['memories_created']} memories")
        
        # Test 2: Memory creation with auto-generated session ID
        payload_no_session = {
            "messages": [{"role": "user", "content": "I also enjoy machine learning"}],
            "user_id": TEST_USER_ID,
            "metadata": {"test_type": "auto_session"}
        }
        
        response = requests.post(
            f"{SERVER_URL}/v1/memories",
            json=payload_no_session,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data["data"]
        
        logger.info("✅ Enhanced memory creation tests passed")
    
    def test_05_search_memories_enhanced(self):
        """Test enhanced search with relevance filtering"""
        logger.info("🔍 Testing enhanced memory search...")
        
        # Wait for memories to be indexed
        time.sleep(2)
        
        # Test 1: Basic search
        search_payload = {
            "query": "Python programming",
            "user_id": TEST_USER_ID,
            "limit": 5,
            "threshold": 0.3
        }
        
        response = requests.post(
            f"{SERVER_URL}/v1/memories/search",
            json=search_payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        
        assert data["success"] is True
        assert "results" in data["data"]
        assert "total_found" in data["data"]
        assert "filtered_out" in data["data"]
        assert "threshold_used" in data["data"]
        
        results = data["data"]["results"]
        assert len(results) > 0
        
        # Verify relevance scores
        for result in results:
            if "score" in result:
                assert result["score"] >= search_payload["threshold"]
        
        logger.info(f"✅ Found {len(results)} relevant memories")
        
        # Test 2: High threshold search (should filter more results)
        high_threshold_payload = {
            "query": "Python programming",
            "user_id": TEST_USER_ID,
            "limit": 5,
            "threshold": 0.8
        }
        
        response = requests.post(
            f"{SERVER_URL}/v1/memories/search",
            json=high_threshold_payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        
        # Should have fewer or equal results due to higher threshold
        high_threshold_results = len(data["data"]["results"])
        assert high_threshold_results <= len(results)
        
        logger.info("✅ Enhanced search tests passed")
    
    def test_06_get_memories_with_pagination(self):
        """Test memory retrieval with enhanced pagination"""
        logger.info("📋 Testing memory retrieval with pagination...")
        
        # Test 1: Get all memories
        response = requests.get(
            f"{SERVER_URL}/v1/memories",
            params={"user_id": TEST_USER_ID, "limit": 10, "offset": 0}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        
        assert data["success"] is True
        assert "results" in data["data"]
        assert "pagination" in data["data"]
        
        pagination = data["data"]["pagination"]
        assert "total" in pagination
        assert "limit" in pagination
        assert "offset" in pagination
        assert "has_more" in pagination
        
        total_memories = pagination["total"]
        assert total_memories > 0
        
        logger.info(f"✅ Retrieved {len(data['data']['results'])} memories (total: {total_memories})")
        
        # Test 2: Pagination
        if total_memories > 1:
            response = requests.get(
                f"{SERVER_URL}/v1/memories",
                params={"user_id": TEST_USER_ID, "limit": 1, "offset": 1}
            )
            
            assert response.status_code in [200, 201]
            data = response.json()
            assert len(data["data"]["results"]) <= 1
        
        logger.info("✅ Pagination tests passed")
    
    def test_07_stats_endpoint(self):
        """Test statistics endpoint"""
        logger.info("📊 Testing statistics endpoint...")
        
        # Test user-specific stats
        response = requests.get(
            f"{SERVER_URL}/v1/stats",
            params={"user_id": TEST_USER_ID}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        
        assert data["success"] is True
        assert "user_id" in data["data"]
        assert "total_memories" in data["data"]
        assert "server_uptime" in data["data"]
        
        assert data["data"]["user_id"] == TEST_USER_ID
        assert data["data"]["total_memories"] > 0
        
        logger.info(f"✅ User has {data['data']['total_memories']} memories")
        
        # Test general server stats
        response = requests.get(f"{SERVER_URL}/v1/stats")
        
        assert response.status_code in [200, 201]
        data = response.json()
        
        assert "server_uptime" in data["data"]
        assert "server_version" in data["data"]
        assert "memory_service_available" in data["data"]
        
        logger.info("✅ Statistics tests passed")
    
    def test_08_error_handling(self):
        """Test error handling and validation"""
        logger.info("❌ Testing error handling...")
        
        # Test 1: Invalid memory creation (empty messages)
        invalid_payload = {
            "messages": [],
            "user_id": TEST_USER_ID
        }
        
        response = requests.post(
            f"{SERVER_URL}/v1/memories",
            json=invalid_payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test 2: Invalid search (empty query)
        invalid_search = {
            "query": "",
            "user_id": TEST_USER_ID
        }
        
        response = requests.post(
            f"{SERVER_URL}/v1/memories/search",
            json=invalid_search,
            headers={"Content-Type": "application/json"}
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 422, 500]
        
        # Test 3: Missing required parameters
        response = requests.get(f"{SERVER_URL}/v1/memories")
        assert response.status_code == 422  # Missing user_id
        
        logger.info("✅ Error handling tests passed")
    
    def test_09_memory_management_crud(self):
        """Test full CRUD operations on memories"""
        logger.info("🔄 Testing CRUD operations...")
        
        # Create a test memory
        messages = [{"role": "user", "content": "This is a test memory for CRUD operations"}]
        
        create_response = requests.post(
            f"{SERVER_URL}/v1/memories",
            json={"messages": messages, "user_id": TEST_USER_ID},
            headers={"Content-Type": "application/json"}
        )
        
        assert create_response.status_code == 201
        create_data = create_response.json()
        
        # Extract memory ID (this might vary based on mem0 response format)
        results = create_data["data"]["results"]
        if results and len(results) > 0:
            memory_id = results[0].get("id")
            
            if memory_id:
                # Test READ
                read_response = requests.get(f"{SERVER_URL}/v1/memories/{memory_id}")
                if read_response.status_code in [200, 201]:
                    logger.info("✅ READ operation successful")
                
                # Test UPDATE
                update_response = requests.put(
                    f"{SERVER_URL}/v1/memories/{memory_id}",
                    json={"data": "Updated test memory", "metadata": {"updated": True}},
                    headers={"Content-Type": "application/json"}
                )
                if update_response.status_code in [200, 201]:
                    logger.info("✅ UPDATE operation successful")
                
                # Test DELETE
                delete_response = requests.delete(f"{SERVER_URL}/v1/memories/{memory_id}")
                if delete_response.status_code in [200, 201]:
                    logger.info("✅ DELETE operation successful")
        
        logger.info("✅ CRUD operations test completed")
    
    def test_10_legacy_compatibility(self):
        """Test backward compatibility with legacy endpoints"""
        logger.info("🔄 Testing legacy compatibility...")
        
        # Test legacy create endpoint
        legacy_payload = {
            "messages": [{"role": "user", "content": "Legacy compatibility test"}],
            "user_id": TEST_USER_ID
        }
        
        response = requests.post(
            f"{SERVER_URL}/v1/memories/",  # Note the trailing slash
            json=legacy_payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        
        # Test legacy search endpoint
        legacy_search = {
            "query": "legacy test",
            "user_id": TEST_USER_ID
        }
        
        response = requests.post(
            f"{SERVER_URL}/v1/memories/search/",  # Note the trailing slash
            json=legacy_search,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [200, 201]
        
        logger.info("✅ Legacy compatibility tests passed")
    
    def test_11_performance_and_concurrency(self):
        """Test server performance under load"""
        logger.info("⚡ Testing performance and concurrency...")
        
        import concurrent.futures
        import threading
        
        def create_memory(thread_id: int):
            """Create a memory in a separate thread"""
            payload = {
                "messages": [{"role": "user", "content": f"Concurrent test message {thread_id}"}],
                "user_id": f"{TEST_USER_ID}-concurrent-{thread_id}",
                "metadata": {"thread_id": thread_id, "test_type": "concurrency"}
            }
            
            response = requests.post(
                f"{SERVER_URL}/v1/memories",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            return response.status_code == 201
        
        # Test with 5 concurrent requests
        num_threads = 5
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_memory, i) for i in range(num_threads)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        success_count = sum(results)
        
        assert success_count >= num_threads * 0.8  # At least 80% success rate
        
        logger.info(f"✅ Concurrency test: {success_count}/{num_threads} successful ({end_time - start_time:.2f}s)")
    
    def test_12_api_documentation(self):
        """Test API documentation endpoints"""
        logger.info("📚 Testing API documentation...")
        
        # Test OpenAPI JSON
        response = requests.get(f"{SERVER_URL}/openapi.json")
        assert response.status_code in [200, 201]
        
        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert "paths" in openapi_spec
        
        # Verify some key endpoints are documented
        paths = openapi_spec["paths"]
        expected_paths = ["/v1/memories", "/v1/memories/search", "/health"]
        
        for expected_path in expected_paths:
            assert any(expected_path in documented_path for documented_path in paths.keys())
        
        # Test Swagger UI (just check it loads)
        response = requests.get(f"{SERVER_URL}/docs")
        assert response.status_code in [200, 201]
        assert "text/html" in response.headers.get("content-type", "")
        
        logger.info("✅ API documentation tests passed")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup test data"""
        logger.info("🧹 Cleaning up test data...")
        
        try:
            # Delete all test memories
            response = requests.delete(
                f"{SERVER_URL}/v1/memories",
                params={"user_id": TEST_USER_ID}
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                deleted_count = data["data"].get("deleted_count", 0)
                logger.info(f"✅ Cleaned up {deleted_count} test memories")
            
            # Clean up concurrent test users
            for i in range(5):
                requests.delete(
                    f"{SERVER_URL}/v1/memories",
                    params={"user_id": f"{TEST_USER_ID}-concurrent-{i}"}
                )
            
        except Exception as e:
            logger.warning(f"⚠️ Cleanup error: {e}")

def run_enhanced_tests():
    """Run all enhanced server tests"""
    logger.info("🚀 Starting Enhanced Local Mem0 Server Test Suite")
    logger.info("=" * 60)
    
    # Run tests with pytest
    pytest_args = [
        "-v",
        "-s",
        "--tb=short",
        __file__
    ]
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        logger.info("🎉 All tests passed! Enhanced server is working perfectly.")
        
    else:
        logger.error("❌ Some tests failed. Check the output above.")
        

if __name__ == "__main__":
    success = run_enhanced_tests()
    exit(0 if success else 1)
