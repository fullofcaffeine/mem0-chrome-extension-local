#!/usr/bin/env python3
"""
Test script to demonstrate memory behavior with improved logging
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_memory_operations():
    print("🧪 Testing Memory Operations with Enhanced Logging")
    print("=" * 60)
    
    user_id = "test-user-enhanced-logging"
    
    # Test 1: Add pet information
    print("\n1️⃣ Adding pet information...")
    response = requests.post(f"{BASE_URL}/v1/memories/", json={
        "messages": [
            {"role": "user", "content": "I have a pet crocodile named Dilo"},
            {"role": "assistant", "content": "That's an unusual but interesting pet! Crocodiles require special care."}
        ],
        "user_id": user_id,
        "metadata": {"test": "pet_info", "provider": "Test"}
    })
    
    if response.status_code in [200, 201]:  # Accept both 200 and 201
        result = response.json()
        print(f"✅ Response: {result['message']}")
        if 'data' in result and 'results' in result['data']:
            print(f"📄 Results: {json.dumps(result['data']['results'], indent=2)}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    time.sleep(2)
    
    # Test 2: Add another pet
    print("\n2️⃣ Adding another pet...")
    response = requests.post(f"{BASE_URL}/v1/memories/", json={
        "messages": [
            {"role": "user", "content": "I also have a bird named Zooer"},
            {"role": "assistant", "content": "Birds make wonderful companions! What type of bird is Zooer?"}
        ],
        "user_id": user_id,
        "metadata": {"test": "another_pet", "provider": "Test"}
    })
    
    if response.status_code in [200, 201]:  # Accept both 200 and 201
        result = response.json()
        print(f"✅ Response: {result['message']}")
        if 'data' in result and 'results' in result['data']:
            print(f"📄 Results: {json.dumps(result['data']['results'], indent=2)}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    time.sleep(2)
    
    # Test 3: Add unrelated query (like Resident Evil)
    print("\n3️⃣ Adding unrelated query about Resident Evil...")
    response = requests.post(f"{BASE_URL}/v1/memories/", json={
        "messages": [
            {"role": "user", "content": "When is Resident Evil Requiem going to be released?"},
            {"role": "assistant", "content": "I don't have specific information about a Resident Evil game called 'Requiem'. Could you be thinking of a different title?"}
        ],
        "user_id": user_id,
        "metadata": {"test": "unrelated_query", "provider": "Test"}
    })
    
    if response.status_code in [200, 201]:  # Accept both 200 and 201
        result = response.json()
        print(f"✅ Response: {result['message']}")
        if 'data' in result and 'results' in result['data']:
            print(f"📄 Results: {json.dumps(result['data']['results'], indent=2)}")
            # Check if any DELETE events occurred
            for item in result['data']['results']:
                if isinstance(item, dict) and item.get('event') == 'DELETE':
                    print(f"🚨 DELETE detected: {item.get('memory', 'Unknown memory')}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # Test 4: Search for memories
    print("\n4️⃣ Searching for all memories...")
    response = requests.post(f"{BASE_URL}/v1/memories/search/", json={
        "query": "pets",
        "user_id": user_id,
        "limit": 10
    })
    
    if response.status_code == 200:
        result = response.json()
        memories = result.get('data', {}).get('results', [])
        print(f"✅ Found {len(memories)} memories")
        for i, memory in enumerate(memories, 1):
            if isinstance(memory, dict):
                print(f"  {i}. {memory.get('memory', 'No memory text')} (Score: {memory.get('score', 'N/A')})")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    response = requests.delete(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})
    if response.status_code == 200:
        print("✅ Test data cleaned up")
    
    print("\n✨ Test completed! Check the server logs for detailed memory operations.")

if __name__ == "__main__":
    try:
        test_memory_operations()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 
