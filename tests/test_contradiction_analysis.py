#!/usr/bin/env python3
"""
Test script to analyze why some semantic contradictions work and others fail
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_specific_contradictions():
    print("🔍 Analyzing Why Some Contradictions Fail")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Pet contradiction (WORKING)",
            "setup": "I have a dog named Buddy",
            "contradiction": "I don't have any pets",
            "expected": "SHOULD DELETE"
        },
        {
            "name": "Location contradiction (FAILING)", 
            "setup": "I live in California",
            "contradiction": "I moved to Texas last month",
            "expected": "SHOULD DELETE"
        },
        {
            "name": "Job contradiction (FAILING)",
            "setup": "I work as a doctor", 
            "contradiction": "I'm unemployed right now",
            "expected": "SHOULD DELETE"
        },
        {
            "name": "Relationship contradiction (WORKING)",
            "setup": "I'm married to Sarah",
            "contradiction": "I'm single and looking for someone to date", 
            "expected": "SHOULD DELETE"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        user_id = f"analysis-{i}"
        print(f"\n{i}️⃣ Testing: {case['name']}")
        print(f"📝 Setup: '{case['setup']}'")
        print(f"⚡ Contradiction: '{case['contradiction']}'")
        
        # Setup memory
        setup_response = requests.post(f"{BASE_URL}/v1/memories/", json={
            "messages": [{"role": "user", "content": case['setup']}],
            "user_id": user_id
        })
        
        if setup_response.status_code in [200, 201]:
            time.sleep(2)
            
            # Check what memory was actually created
            memories_response = requests.get(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})
            if memories_response.status_code == 200:
                memories = memories_response.json().get('data', {}).get('results', [])
                print(f"💾 Actual memory created: '{memories[0].get('memory', 'None') if memories else 'None'}'")
            
            # Test contradiction
            contradict_response = requests.post(f"{BASE_URL}/v1/memories/", json={
                "messages": [{"role": "user", "content": case['contradiction']}],
                "user_id": user_id
            })
            
            if contradict_response.status_code in [200, 201]:
                result = contradict_response.json()
                operations = result.get('data', {}).get('results', [])
                
                deletions = [op for op in operations if op.get('event') == 'DELETE']
                protected = [op for op in operations if op.get('event') == 'NONE' and 'protection_reason' in op]
                
                if deletions:
                    print(f"✅ SUCCESS: Deletion occurred as expected")
                    for deletion in deletions:
                        print(f"   🗑️ Deleted: {deletion.get('memory')}")
                elif protected:
                    print(f"❌ FAILURE: Memory was protected")
                    for protection in protected:
                        print(f"   🛡️ Protected: {protection.get('memory')}")
                        print(f"   📝 Reason: {protection.get('protection_reason', 'No reason')}")
                else:
                    print(f"❓ UNCLEAR: No deletions or protections, just other operations:")
                    for op in operations:
                        print(f"   {op.get('event', 'UNKNOWN')}: {op.get('memory', 'No memory text')}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})

def test_memory_extraction_patterns():
    print("\n🧪 Testing Memory Extraction Patterns")
    print("=" * 60)
    
    test_inputs = [
        "I work as a doctor",
        "I live in California", 
        "I have a dog named Buddy",
        "I'm married to Sarah"
    ]
    
    for i, input_text in enumerate(test_inputs, 1):
        user_id = f"extraction-{i}"
        print(f"\n{i}️⃣ Input: '{input_text}'")
        
        response = requests.post(f"{BASE_URL}/v1/memories/", json={
            "messages": [{"role": "user", "content": input_text}],
            "user_id": user_id
        })
        
        if response.status_code in [200, 201]:
            # Check what memory was extracted
            time.sleep(1)
            memories_response = requests.get(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})
            if memories_response.status_code == 200:
                memories = memories_response.json().get('data', {}).get('results', [])
                if memories:
                    print(f"   📄 Extracted: '{memories[0].get('memory', 'None')}'")
                    
                    # Check if the extracted memory contains key information
                    extracted = memories[0].get('memory', '').lower()
                    original = input_text.lower()
                    
                    if 'doctor' in original and 'doctor' not in extracted:
                        print(f"   ⚠️ WARNING: 'doctor' lost in extraction")
                    if 'california' in original and 'california' not in extracted:
                        print(f"   ⚠️ WARNING: 'california' lost in extraction")
                    if 'buddy' in original and 'buddy' not in extracted:
                        print(f"   ⚠️ WARNING: 'buddy' lost in extraction")
                    if 'sarah' in original and 'sarah' not in extracted:
                        print(f"   ⚠️ WARNING: 'sarah' lost in extraction")
                else:
                    print(f"   ❌ No memory extracted!")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/v1/memories/", params={"user_id": user_id})

if __name__ == "__main__":
    try:
        test_specific_contradictions()
        test_memory_extraction_patterns()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 
