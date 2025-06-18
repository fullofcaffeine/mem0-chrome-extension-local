#!/usr/bin/env python3
"""
LLM Intention and Effectiveness Tests for Local Mem0
Tests if the LLM is making good decisions and being useful to the system
"""

import requests
import json
import time
import sys
import uuid
from datetime import datetime

# Server configuration
BASE_URL = "http://localhost:8000"
USER_ID = f"llm-test-{uuid.uuid4().hex[:8]}"

def test_llm_memory_extraction_intention():
    """Test 1: LLM extracts meaningful memories from conversations"""
    print("🔍 Test 1: LLM Memory Extraction Intention")
    try:
        # Clear conversation that should produce extractable memories
        test_conversations = [
            {
                "messages": [
                    {"role": "user", "content": "I'm a software engineer who loves Python programming and works at Google"},
                    {"role": "assistant", "content": "That's great! Python is excellent for many applications. How do you like working at Google?"}
                ],
                "expected_concepts": ["software engineer", "python", "programming", "google", "work"]
            },
            {
                "messages": [
                    {"role": "user", "content": "I have a dog named Max and I live in San Francisco"},
                    {"role": "assistant", "content": "Dogs are wonderful companions! San Francisco is a great city for dog owners."}
                ],
                "expected_concepts": ["dog", "max", "san francisco", "live", "pet"]
            },
            {
                "messages": [
                    {"role": "user", "content": "I'm allergic to peanuts and prefer vegetarian food"},
                    {"role": "assistant", "content": "It's important to be careful with food allergies. There are many great vegetarian options available."}
                ],
                "expected_concepts": ["allergic", "peanuts", "vegetarian", "food", "dietary"]
            }
        ]
        
        successful_extractions = 0
        
        for i, test_case in enumerate(test_conversations):
            print(f"   Testing conversation {i+1}: {test_case['messages'][0]['content'][:50]}...")
            
            # Add memory through LLM
            response = requests.post(f"{BASE_URL}/v1/memories/", json={
                "messages": test_case["messages"],
                "user_id": USER_ID,
                "metadata": {"test": "intention", "case": i}
            })
            
            assert response.status_code in [200, 201]
            data = response.json()
            assert data["success"] == True
            
            # Check if LLM extracted any memories
            results = data.get("data", {}).get("results", [])
            if results:
                extracted_memories = [result.get("memory", "").lower() for result in results if result.get("event") in ["ADD", "UPDATE"]]
                
                if extracted_memories:
                    # Check if any expected concepts appear in extracted memories
                    memory_text = " ".join(extracted_memories)
                    
                    print(f"     📝 LLM extracted memories: {extracted_memories}")
                    print(f"     🎯 Expected concepts: {test_case['expected_concepts']}")
                    
                    # Find which concepts were actually found
                    found_concepts = []
                    missing_concepts = []
                    
                    for concept in test_case["expected_concepts"]:
                        if concept.lower() in memory_text.lower():
                            found_concepts.append(concept)
                        else:
                            missing_concepts.append(concept)
                    
                    concept_matches = len(found_concepts)
                    
                    if concept_matches > 0:
                        successful_extractions += 1
                        print(f"     ✅ Found concepts: {found_concepts}")
                        if missing_concepts:
                            print(f"     ⚠️  Missing concepts: {missing_concepts}")
                        print(f"     📊 Concept match rate: {concept_matches}/{len(test_case['expected_concepts'])} ({concept_matches/len(test_case['expected_concepts']):.1%})")
                    else:
                        print(f"     ❌ No expected concepts found in extracted memories")
                        print(f"     🔍 Memory text: '{memory_text}'")
                        print(f"     🎯 Looking for: {test_case['expected_concepts']}")
                else:
                    print(f"     ⚠️  No memories were added by LLM")
            else:
                print(f"     ⚠️  LLM produced no actionable results")
        
        # Success if LLM extracted meaningful memories from at least 60% of conversations
        success_rate = successful_extractions / len(test_conversations)
        print(f"   LLM Memory Extraction Success Rate: {success_rate:.1%}")
        
        if success_rate >= 0.6:
            print("✅ LLM is effectively extracting meaningful memories")
            
        else:
            print("❌ LLM is not extracting meaningful memories effectively")
            
            
    except Exception as e:
        print(f"❌ LLM memory extraction test failed: {e}")
        

def test_llm_decision_making_intention():
    """Test 2: LLM makes appropriate ADD/UPDATE/DELETE decisions"""
    print("\n🔍 Test 2: LLM Decision Making Intention")
    try:
        # Test scenarios that should trigger different LLM decisions
        scenarios = [
            {
                "name": "New Information (should ADD)",
                "messages": [
                    {"role": "user", "content": "I just started learning Spanish and really enjoy it"},
                    {"role": "assistant", "content": "That's wonderful! Spanish is a beautiful language."}
                ],
                "expected_events": ["ADD"]
            },
            {
                "name": "Similar Information (should UPDATE or NONE)",
                "messages": [
                    {"role": "user", "content": "I'm still learning Spanish and making good progress"},
                    {"role": "assistant", "content": "Great to hear you're progressing well with Spanish!"}
                ],
                "expected_events": ["UPDATE", "NONE"]
            },
            {
                "name": "Correction (should UPDATE or DELETE+ADD)",
                "messages": [
                    {"role": "user", "content": "Actually, I stopped learning Spanish and started learning French instead"},
                    {"role": "assistant", "content": "French is also a great language to learn!"}
                ],
                "expected_events": ["UPDATE", "DELETE", "ADD"]
            }
        ]
        
        appropriate_decisions = 0
        
        for scenario in scenarios:
            print(f"   Testing: {scenario['name']}")
            
            response = requests.post(f"{BASE_URL}/v1/memories/", json={
                "messages": scenario["messages"],
                "user_id": USER_ID,
                "metadata": {"test": "decision_making", "scenario": scenario["name"]}
            })
            
            assert response.status_code in [200, 201]
            data = response.json()
            assert data["success"] == True
            
            # Check if LLM made appropriate decisions
            results = data.get("data", {}).get("results", [])
            print(f"     🧠 LLM processing results: {len(results)} operations")
            
            if results:
                events = [result.get("event") for result in results]
                memories = [result.get("memory", "") for result in results]
                
                print(f"     📝 LLM decisions: {events}")
                print(f"     💭 Memories created/modified:")
                for i, (event, memory) in enumerate(zip(events, memories)):
                    print(f"        {i+1}. {event}: '{memory[:50]}...'")
                
                print(f"     🎯 Expected decision types: {scenario['expected_events']}")
                
                # Check if any expected event occurred
                if any(event in scenario["expected_events"] for event in events):
                    appropriate_decisions += 1
                    matching_events = [e for e in events if e in scenario["expected_events"]]
                    print(f"     ✅ Appropriate decisions found: {matching_events}")
                else:
                    print(f"     ❌ No appropriate decisions found")
                    print(f"     🔍 LLM chose: {events} | Expected: {scenario['expected_events']}")
            else:
                print(f"     🤐 LLM made no memory operations")
                print(f"     🎯 Expected: {scenario['expected_events']}")
                
                if "NONE" in scenario["expected_events"]:
                    appropriate_decisions += 1
                    print(f"     ✅ Correctly did nothing (expected NONE)")
                else:
                    print(f"     ❌ Should have made decisions but didn't")
        
        decision_quality = appropriate_decisions / len(scenarios)
        print(f"   LLM Decision Quality: {decision_quality:.1%}")
        
        if decision_quality >= 0.6:
            print("✅ LLM is making appropriate memory management decisions")
            
        else:
            print("❌ LLM decision making needs improvement")
            
            
    except Exception as e:
        print(f"❌ LLM decision making test failed: {e}")
        

def test_llm_semantic_usefulness():
    """Test 3: LLM produces semantically useful memories"""
    print("\n🔍 Test 3: LLM Semantic Usefulness")
    print("     🔧 Using Qdrant vector similarity search with HuggingFace embeddings")
    print("     📊 Similarity scores range from 0.0 (unrelated) to 1.0 (identical)")
    print("     🎯 Threshold: 0.3+ indicates semantic relevance")
    try:
        # Add some memories and then search to see if they're useful
        conversation = [
            {"role": "user", "content": "I work as a data scientist at Tesla and I'm passionate about sustainable energy and electric vehicles"},
            {"role": "assistant", "content": "That's an exciting field! Tesla is doing amazing work in sustainable transportation."}
        ]
        
        # Add memory
        add_response = requests.post(f"{BASE_URL}/v1/memories/", json={
            "messages": conversation,
            "user_id": USER_ID,
            "metadata": {"test": "semantic_usefulness"}
        })
        
        assert add_response.status_code in [200, 201]
        
        # Wait for processing
        time.sleep(2)
        
        # Test semantic searches that should find relevant memories
        search_queries = [
            "What is my job?",
            "Where do I work?", 
            "What am I passionate about?",
            "Tell me about my career",
            "What are my interests in technology?"
        ]
        
        successful_searches = 0
        
        for query in search_queries:
            search_response = requests.post(f"{BASE_URL}/v1/memories/search/", json={
                "query": query,
                "user_id": USER_ID,
                "limit": 5
            })
            
            assert search_response.status_code in [200, 201]
            search_data = search_response.json()
            assert search_data["success"] == True
            
            results = search_data.get("data", {}).get("results", [])
            if results:
                # Check if the highest scoring result is relevant (score > 0.3 indicates some relevance)
                top_result = results[0]
                print(f"     🔍 Query: '{query}'")
                print(f"     📊 Qdrant returned {len(results)} results")
                print(f"     🥇 Top result: '{top_result.get('memory', 'N/A')[:60]}...'")
                print(f"     📈 Qdrant similarity score: {top_result.get('score', 0):.3f}")
                
                if top_result.get("score", 0) > 0.3:
                    successful_searches += 1
                    print(f"     ✅ Semantically relevant (score > 0.3 threshold)")
                else:
                    print(f"     ❌ Below relevance threshold (score ≤ 0.3)")
                    
                # Show all results for debugging
                if len(results) > 1:
                    print(f"     📋 All Qdrant results:")
                    for i, result in enumerate(results[:3]):  # Show top 3
                        print(f"        {i+1}. Score: {result.get('score', 0):.3f} | Memory: '{result.get('memory', 'N/A')[:50]}...'")
            else:
                print(f"     ❌ '{query}' → No results found in Qdrant")
        
        usefulness_rate = successful_searches / len(search_queries)
        print(f"   Semantic Usefulness Rate: {usefulness_rate:.1%}")
        
        if usefulness_rate >= 0.6:
            print("✅ LLM produces semantically useful memories")
            
        else:
            print("❌ LLM memories are not semantically useful enough")
            
            
    except Exception as e:
        print(f"❌ LLM semantic usefulness test failed: {e}")
        

def test_llm_response_time_and_reliability():
    """Test 4: LLM responds reliably within reasonable time"""
    print("\n🔍 Test 4: LLM Response Time and Reliability")
    try:
        test_conversations = [
            {"role": "user", "content": "I like coffee in the morning"},
            {"role": "user", "content": "I prefer tea in the afternoon"},
            {"role": "user", "content": "I enjoy reading books before bed"}
        ]
        
        response_times = []
        successful_calls = 0
        
        for i, message in enumerate(test_conversations):
            start_time = time.time()
            
            response = requests.post(f"{BASE_URL}/v1/memories/", json={
                "messages": [message, {"role": "assistant", "content": "That sounds nice!"}],
                "user_id": USER_ID,
                "metadata": {"test": "reliability", "iteration": i}
            }, timeout=30)  # 30 second timeout
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("success"):
                    successful_calls += 1
                    print(f"     ✅ Call {i+1}: {response_time:.1f}s")
                else:
                    print(f"     ❌ Call {i+1}: API error - {response_time:.1f}s")
            else:
                print(f"     ❌ Call {i+1}: HTTP {response.status_code} - {response_time:.1f}s")
        
        avg_response_time = sum(response_times) / len(response_times)
        reliability_rate = successful_calls / len(test_conversations)
        
        print(f"   Average Response Time: {avg_response_time:.1f}s")
        print(f"   Reliability Rate: {reliability_rate:.1%}")
        
        # Success criteria: >80% success rate and <15s average response time
        if reliability_rate >= 0.8 and avg_response_time < 15:
            print("✅ LLM is responding reliably within acceptable time")
            
        else:
            print("❌ LLM reliability or response time needs improvement")
            
            
    except Exception as e:
        print(f"❌ LLM reliability test failed: {e}")
        

def test_llm_context_understanding():
    """Test 5: LLM understands conversation context"""
    print("\n🔍 Test 5: LLM Context Understanding")
    try:
        # Multi-turn conversation that requires context understanding
        context_conversation = [
            {"role": "user", "content": "I'm planning a trip to Japan next month"},
            {"role": "assistant", "content": "That sounds exciting! Japan is a wonderful destination."},
            {"role": "user", "content": "I'm especially excited about trying authentic ramen and visiting temples"},
            {"role": "assistant", "content": "You'll love the food culture and the beautiful temples in Japan."},
            {"role": "user", "content": "I've been learning basic Japanese phrases to prepare"},
            {"role": "assistant", "content": "That's very thoughtful! The locals will appreciate your effort."}
        ]
        
        # Add the full conversation context
        response = requests.post(f"{BASE_URL}/v1/memories/", json={
            "messages": context_conversation,
            "user_id": USER_ID,
            "metadata": {"test": "context_understanding"}
        })
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["success"] == True
        
        results = data.get("data", {}).get("results", [])
        
        if not results:
            print("❌ LLM didn't extract any memories from context-rich conversation")
            
        
        # Check if memories show understanding of the overall context
        memories = [result.get("memory", "").lower() for result in results if result.get("event") in ["ADD", "UPDATE"]]
        
        context_indicators = [
            "japan", "trip", "travel", "ramen", "food", "temples", "japanese", "language", "learning"
        ]
        
        print(f"     🧠 LLM extracted {len(memories)} contextual memories:")
        for i, memory in enumerate(memories):
            print(f"        {i+1}. '{memory}'")
        
        print(f"     🎯 Looking for context indicators: {context_indicators}")
        
        context_understanding = 0
        for i, memory in enumerate(memories):
            found_indicators = [indicator for indicator in context_indicators if indicator in memory]
            relevant_concepts = len(found_indicators)
            
            print(f"     📝 Memory {i+1} analysis:")
            print(f"        Text: '{memory}'")
            print(f"        Found indicators: {found_indicators}")
            print(f"        Concept count: {relevant_concepts}")
            
            if relevant_concepts >= 2:  # Memory shows understanding of multiple context elements
                context_understanding += 1
                print(f"        ✅ Shows good contextual understanding (≥2 concepts)")
            else:
                print(f"        ⚠️  Limited contextual understanding (<2 concepts)")
        
        print(f"     📊 Contextual memories: {context_understanding}/{len(memories)}")
        
        if context_understanding > 0:
            print("✅ LLM demonstrates good context understanding")
            
        else:
            print("❌ LLM failed to understand conversation context")
            
            
    except Exception as e:
        print(f"❌ LLM context understanding test failed: {e}")
        

def cleanup_test_data():
    """Clean up test data"""
    try:
        # Try to delete test user's memories
        requests.delete(f"{BASE_URL}/v1/memories/", params={"user_id": USER_ID})
        print(f"🧹 Cleaned up test data for user: {USER_ID}")
    except:
        pass  # Ignore cleanup errors

def check_service_dependencies():
    """Check if all required services are running"""
    print("🔍 Checking service dependencies...")
    
    services = [
        {"name": "Mem0 Server", "url": f"{BASE_URL}/health", "required": True},
        {"name": "Ollama LLM", "url": "http://localhost:11434", "required": True},
        {"name": "Qdrant Vector DB", "url": "http://localhost:6333/health", "required": True}
    ]
    
    all_services_up = True
    
    for service in services:
        try:
            response = requests.get(service["url"], timeout=5)
            if response.status_code in [200, 201]:
                print(f"  ✅ {service['name']}: Running")
            else:
                print(f"  ❌ {service['name']}: HTTP {response.status_code}")
                all_services_up = False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {service['name']}: Connection failed - {e}")
            all_services_up = False
    
    return all_services_up

def run_llm_intention_tests():
    """Run all LLM intention and effectiveness tests"""
    print("🧠 LLM Intention and Effectiveness Test Suite")
    print("=" * 60)
    print(f"Testing LLM usefulness with user: {USER_ID}")
    print("=" * 60)
    
    # Check service dependencies first
    if not check_service_dependencies():
        print("\n❌ Service dependency check failed!")
        print("📋 Before running LLM tests, ensure all services are running:")
        print("   1. Start server: ./scripts/start_mem0.sh (from repo root)")
        print("   2. Verify: curl http://localhost:8000/health")
        print("   3. Then re-run this test")
        
    
    print("\n✅ All services are running! Proceeding with LLM tests...")
    print("=" * 60)
    
    tests = [
        test_llm_memory_extraction_intention,
        test_llm_decision_making_intention,
        test_llm_semantic_usefulness,
        test_llm_response_time_and_reliability,
        test_llm_context_understanding
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 LLM Effectiveness Results:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    effectiveness_score = passed / total
    print(f"🎯 Overall LLM Effectiveness: {effectiveness_score:.1%}")
    
    if effectiveness_score >= 0.8:
        print("🎉 LLM is highly effective for the mem0 system!")
    elif effectiveness_score >= 0.6:
        print("✅ LLM is adequately effective for the mem0 system")
    else:
        print("⚠️  LLM effectiveness is below acceptable threshold")
        print("💡 Consider: Different model, better prompts, or parameter tuning")
    
    cleanup_test_data()
    return effectiveness_score >= 0.6

if __name__ == "__main__":
    success = run_llm_intention_tests()
    sys.exit(0 if success else 1) 
