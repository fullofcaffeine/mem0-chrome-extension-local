#!/usr/bin/env python3
"""
Test script for LLM-based memory deletion reasoning
"""

import requests
import json
import time
import asyncio

BASE_URL = "http://localhost:8000"

def test_llm_deletion_reasoning():
    print("🧪 Testing LLM-Based Memory Deletion Reasoning")
    print("=" * 60)
    
    user_id = "test-llm-reasoning"
    
    # Test 1: Add initial pet information
    print("\n1️⃣ Adding initial pet information...")
    response = requests.post(f"{BASE_URL}/v1/memories/", json={
        "messages": [
            {"role": "user", "content": "I have a pet dog named Max"}
        ],
        "user_id": user_id,
        "metadata": {"test": "initial_pet", "provider": "Test"}
    })
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✅ Response: {result['message']}")
        print(f"📄 Operations: {len(result.get('data', {}).get('results', []))}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    time.sleep(3)
    
    # Test 2: Update pet information (should be legitimate update)
    print("\n2️⃣ Updating pet information (legitimate update)...")
    response = requests.post(f"{BASE_URL}/v1/memories/", json={
        "messages": [
            {"role": "user", "content": "Actually, my dog's name is Bruno, not Max. I made a mistake earlier."}
        ],
        "user_id": user_id,
        "metadata": {"test": "legitimate_update", "provider": "Test"}
    })
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✅ Response: {result['message']}")
        operations = result.get('data', {}).get('results', [])
        print(f"📄 Operations: {len(operations)}")
        
        # Check if LLM approved any deletions
        for op in operations:
            if op.get('event') == 'DELETE':
                print(f"🗑️ LLM APPROVED deletion: {op.get('memory')}")
            elif op.get('event') == 'NONE' and 'protection_reason' in op:
                print(f"🛡️ LLM REJECTED deletion: {op.get('memory')}")
                print(f"📝 Reason: {op.get('protection_reason')}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    time.sleep(3)
    
    # Test 3: Add unrelated information (should NOT delete pet info)
    print("\n3️⃣ Adding unrelated information (should protect pet info)...")
    response = requests.post(f"{BASE_URL}/v1/memories/", json={
        "messages": [
            {"role": "user", "content": "What's the weather like today in San Francisco?"}
        ],
        "user_id": user_id,
        "metadata": {"test": "unrelated_query", "provider": "Test"}
    })
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✅ Response: {result['message']}")
        operations = result.get('data', {}).get('results', [])
        print(f"📄 Operations: {len(operations)}")
        
        # Check protection reasoning
        for op in operations:
            if op.get('event') == 'DELETE':
                print(f"🗑️ LLM APPROVED deletion: {op.get('memory')}")
            elif op.get('event') == 'NONE' and 'protection_reason' in op:
                print(f"🛡️ LLM REJECTED deletion: {op.get('memory')}")
                print(f"📝 Reason: {op.get('protection_reason')}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    time.sleep(3)
    
    # Test 4: Check what memories remain
    print("\n4️⃣ Checking remaining memories...")
    response = requests.get(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})
    
    if response.status_code == 200:
        result = response.json()
        memories = result.get('data', {}).get('results', [])
        print(f"✅ Found {len(memories)} memories:")
        for i, memory in enumerate(memories, 1):
            print(f"  {i}. {memory.get('memory', 'No memory text')}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # Test 5: Test search functionality
    print("\n5️⃣ Testing search with remaining memories...")
    response = requests.post(f"{BASE_URL}/v1/memories/search/", json={
        "query": "What pets do I have?",
        "user_id": user_id,
        "limit": 5
    })
    
    if response.status_code == 200:
        result = response.json()
        memories = result.get('data', {}).get('results', [])
        print(f"✅ Search found {len(memories)} relevant memories:")
        for memory in memories:
            print(f"  - {memory.get('memory', 'No memory text')} (Score: {memory.get('score', 'N/A'):.3f})")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    response = requests.delete(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})
    if response.status_code == 200:
        print("✅ Test data cleaned up")
    
    print("\n✨ LLM Deletion Reasoning Test completed!")
    print("📋 Check server logs for detailed LLM reasoning and decisions.")

def test_deletion_protection_edge_cases():
    print("\n🧪 Testing Deletion Protection Edge Cases")
    print("=" * 60)
    
    user_id = "test-edge-cases"
    
    # Test contradictory information
    print("\n1️⃣ Testing contradictory information handling...")
    
    # Add initial info
    requests.post(f"{BASE_URL}/v1/memories/", json={
        "messages": [{"role": "user", "content": "I live in New York"}],
        "user_id": user_id,
        "metadata": {"test": "initial_location"}
    })
    
    time.sleep(2)
    
    # Add contradictory info
    response = requests.post(f"{BASE_URL}/v1/memories/", json={
        "messages": [{"role": "user", "content": "I moved to California last month"}],
        "user_id": user_id,
        "metadata": {"test": "updated_location"}
    })
    
    if response.status_code in [200, 201]:
        result = response.json()
        operations = result.get('data', {}).get('results', [])
        print(f"📄 Operations: {len(operations)}")
        
        for op in operations:
            if op.get('event') == 'DELETE':
                print(f"🗑️ LLM approved deletion of outdated info: {op.get('memory')}")
            elif op.get('event') == 'NONE' and 'protection_reason' in op:
                print(f"🛡️ LLM protected: {op.get('memory')}")
                print(f"📝 Reason: {op.get('protection_reason')}")
    
    # Cleanup
    requests.delete(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})
    print("✅ Edge case test completed")

if __name__ == "__main__":
    try:
        test_llm_deletion_reasoning()
        test_deletion_protection_edge_cases()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 
