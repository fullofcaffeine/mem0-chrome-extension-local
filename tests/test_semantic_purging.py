#!/usr/bin/env python3
"""
Test script for semantic memory purging functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_semantic_purging():
    print("🧪 Testing Semantic Memory Purging")
    print("=" * 60)
    
    user_id = "test-semantic-purging"
    
    # Test 1: Setup - Add multiple pet-related memories
    print("\n1️⃣ Setting up pet memories...")
    
    pet_memories = [
        "I have a dog named Max",
        "My cat Luna loves to sleep on my bed", 
        "I feed my pets every morning at 7 AM",
        "My dog Max is a Golden Retriever"
    ]
    
    for i, memory in enumerate(pet_memories):
        response = requests.post(f"{BASE_URL}/v1/memories/", json={
            "messages": [{"role": "user", "content": memory}],
            "user_id": user_id,
            "metadata": {"test": f"setup_{i}", "provider": "Test"}
        })
        
        if response.status_code in [200, 201]:
            result = response.json()
            operations = result.get('data', {}).get('results', [])
            print(f"  ✅ Added: '{memory}' ({len(operations)} operations)")
        else:
            print(f"  ❌ Failed to add: '{memory}' - {response.status_code}")
        
        time.sleep(2)
    
    # Check what memories we have
    print("\n📋 Current memories before purging:")
    response = requests.get(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})
    if response.status_code == 200:
        memories = response.json().get('data', {}).get('results', [])
        for i, memory in enumerate(memories, 1):
            print(f"  {i}. {memory.get('memory', 'No memory text')}")
        print(f"Total: {len(memories)} memories")
    else:
        print("❌ Failed to get memories")
    
    # Test 2: Semantic purging - "I don't have any pets"
    print("\n2️⃣ Testing semantic purging with 'I don't have any pets'...")
    response = requests.post(f"{BASE_URL}/v1/memories/", json={
        "messages": [{"role": "user", "content": "I don't have any pets"}],
        "user_id": user_id,
        "metadata": {"test": "semantic_purge", "provider": "Test"}
    })
    
    if response.status_code in [200, 201]:
        result = response.json()
        operations = result.get('data', {}).get('results', [])
        print(f"📄 Operations: {len(operations)}")
        
        deletions_approved = 0
        deletions_rejected = 0
        
        for op in operations:
            event = op.get('event', '')
            memory_text = op.get('memory', '')
            
            if event == 'DELETE':
                print(f"🗑️ LLM APPROVED deletion: '{memory_text}'")
                deletions_approved += 1
            elif event == 'NONE' and 'protection_reason' in op:
                print(f"🛡️ LLM REJECTED deletion: '{memory_text}'")
                print(f"📝 Reason: {op.get('protection_reason')}")
                deletions_rejected += 1
            elif event == 'ADD':
                print(f"➕ ADDED: '{memory_text}'")
            elif event == 'UPDATE':
                print(f"🔄 UPDATED: '{memory_text}'")
            else:
                print(f"❓ OTHER ({event}): '{memory_text}'")
        
        print(f"\n📊 Summary: {deletions_approved} deletions approved, {deletions_rejected} rejected")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    time.sleep(3)
    
    # Test 3: Check remaining memories
    print("\n3️⃣ Checking remaining memories after purging...")
    response = requests.get(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})
    if response.status_code == 200:
        memories = response.json().get('data', {}).get('results', [])
        print(f"✅ Found {len(memories)} memories remaining:")
        for i, memory in enumerate(memories, 1):
            print(f"  {i}. {memory.get('memory', 'No memory text')}")
        
        # Check if pet-related memories were properly purged
        pet_keywords = ['pet', 'dog', 'cat', 'max', 'luna', 'feed']
        remaining_pet_memories = []
        for memory in memories:
            memory_text = memory.get('memory', '').lower()
            if any(keyword in memory_text for keyword in pet_keywords):
                remaining_pet_memories.append(memory.get('memory'))
        
        if remaining_pet_memories:
            print(f"⚠️ WARNING: {len(remaining_pet_memories)} pet-related memories still exist:")
            for pet_mem in remaining_pet_memories:
                print(f"    - {pet_mem}")
        else:
            print("✅ SUCCESS: All pet-related memories were properly purged!")
            
    else:
        print(f"❌ Error getting memories: {response.status_code}")
    
    # Test 4: Search functionality should find the new "no pets" memory
    print("\n4️⃣ Testing search for pet-related queries...")
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
        print(f"❌ Search error: {response.status_code}")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    response = requests.delete(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})
    if response.status_code == 200:
        print("✅ Test data cleaned up")
    
    print("\n✨ Semantic Purging Test completed!")

def test_partial_semantic_purging():
    print("\n🧪 Testing Partial Semantic Purging")
    print("=" * 60)
    
    user_id = "test-partial-purging"
    
    # Setup mixed memories
    print("\n1️⃣ Setting up mixed memories...")
    
    mixed_memories = [
        "I have a dog named Rex",
        "I work as a software engineer",
        "My favorite food is pizza",
        "I live in New York",
        "My dog Rex is 3 years old"
    ]
    
    for memory in mixed_memories:
        requests.post(f"{BASE_URL}/v1/memories/", json={
            "messages": [{"role": "user", "content": memory}],
            "user_id": user_id,
            "metadata": {"test": "mixed_setup"}
        })
        time.sleep(1.5)
    
    # Test partial purging - change job
    print("\n2️⃣ Testing partial purging: 'I quit my job and now work as a teacher'...")
    response = requests.post(f"{BASE_URL}/v1/memories/", json={
        "messages": [{"role": "user", "content": "I quit my job and now work as a teacher"}],
        "user_id": user_id,
        "metadata": {"test": "job_change"}
    })
    
    if response.status_code in [200, 201]:
        result = response.json()
        operations = result.get('data', {}).get('results', [])
        
        print(f"📄 Operations: {len(operations)}")
        for op in operations:
            event = op.get('event', '')
            memory_text = op.get('memory', '')
            
            if event == 'DELETE':
                print(f"🗑️ LLM APPROVED deletion: '{memory_text}'")
            elif event == 'ADD':
                print(f"➕ ADDED: '{memory_text}'")
    
    # Check final state
    print("\n3️⃣ Final memory state:")
    response = requests.get(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})
    if response.status_code == 200:
        memories = response.json().get('data', {}).get('results', [])
        for memory in memories:
            print(f"  - {memory.get('memory', 'No memory text')}")
    
    # Cleanup
    requests.delete(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})
    print("✅ Partial purging test completed")

def test_contradiction_scenarios():
    print("\n🧪 Testing Various Contradiction Scenarios")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Pet ownership contradiction",
            "setup": ["I have a dog named Buddy"],
            "contradiction": "I don't have any pets",
            "expect_deletion": True
        },
        {
            "name": "Location contradiction", 
            "setup": ["I live in California"],
            "contradiction": "I moved to Texas last month",
            "expect_deletion": True
        },
        {
            "name": "Job contradiction",
            "setup": ["I work as a doctor"],
            "contradiction": "I'm unemployed right now",
            "expect_deletion": True
        },
        {
            "name": "Relationship contradiction",
            "setup": ["I'm married to Sarah"],
            "contradiction": "I'm single and looking for someone to date",
            "expect_deletion": True
        },
        {
            "name": "Non-contradiction (additional info)",
            "setup": ["I like pizza"],
            "contradiction": "I also enjoy pasta",
            "expect_deletion": False
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        user_id = f"test-contradiction-{i}"
        print(f"\n{i}️⃣ Testing: {scenario['name']}")
        
        # Setup
        for setup_mem in scenario['setup']:
            requests.post(f"{BASE_URL}/v1/memories/", json={
                "messages": [{"role": "user", "content": setup_mem}],
                "user_id": user_id
            })
            time.sleep(1)
        
        # Test contradiction
        response = requests.post(f"{BASE_URL}/v1/memories/", json={
            "messages": [{"role": "user", "content": scenario['contradiction']}],
            "user_id": user_id
        })
        
        if response.status_code in [200, 201]:
            operations = response.json().get('data', {}).get('results', [])
            deletions = [op for op in operations if op.get('event') == 'DELETE']
            
            if scenario['expect_deletion']:
                if deletions:
                    print(f"  ✅ PASS: Deletion detected as expected")
                    for deletion in deletions:
                        print(f"    🗑️ Deleted: {deletion.get('memory')}")
                else:
                    print(f"  ❌ FAIL: Expected deletion but none occurred")
            else:
                if deletions:
                    print(f"  ❌ FAIL: Unexpected deletion occurred")
                    for deletion in deletions:
                        print(f"    🗑️ Unexpected deletion: {deletion.get('memory')}")
                else:
                    print(f"  ✅ PASS: No deletion as expected")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})

if __name__ == "__main__":
    try:
        test_semantic_purging()
        test_partial_semantic_purging()
        test_contradiction_scenarios()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 
