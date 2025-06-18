#!/usr/bin/env python3
"""
Comprehensive Mem0 Implementation Comparison and Quality Assessment
Tests memory quality, extraction capabilities, and compares approaches
"""

import requests
import json
import uuid
import time
from typing import List, Dict, Any
import pytest

# Advanced comparison tests - now fully supported by local server!

def test_local_mem0_quality():
    """Test the quality and capabilities of our local Mem0 implementation"""
    print("🧠 Testing Local Mem0 Implementation")
    print("=" * 60)
    
    user_id = f'quality-test-{uuid.uuid4().hex[:8]}'
    
    test_scenarios = [
        {
            "name": "Technical Preferences",
            "messages": [
                {"role": "user", "content": "I'm a senior Python developer who prefers FastAPI over Flask. I always use type hints and async/await patterns. My preferred database is PostgreSQL with SQLAlchemy ORM."},
                {"role": "assistant", "content": "Great choices! FastAPI's automatic API documentation and async support make it excellent for modern APIs. How do you handle database migrations with SQLAlchemy?"}
            ],
            "expected_concepts": ["python", "fastapi", "flask", "type hints", "async", "postgresql", "sqlalchemy"]
        },
        {
            "name": "Project Context",
            "messages": [
                {"role": "user", "content": "I'm building a microservices architecture for an e-commerce platform. Each service runs in Docker containers and communicates via gRPC. I use Redis for caching and Celery for background tasks."},
                {"role": "assistant", "content": "That's a solid architecture! How are you handling service discovery and load balancing between your microservices?"}
            ],
            "expected_concepts": ["microservices", "e-commerce", "docker", "grpc", "redis", "celery", "background tasks"]
        },
        {
            "name": "Personal Workflow",
            "messages": [
                {"role": "user", "content": "I work remotely from San Francisco and prefer using VS Code with the Python extension. I always write tests with pytest and use GitHub Actions for CI/CD."},
                {"role": "assistant", "content": "Remote work in San Francisco sounds great! Do you have any specific pytest fixtures or GitHub Actions workflows you find particularly useful?"}
            ],
            "expected_concepts": ["remote", "san francisco", "vscode", "python extension", "pytest", "github actions", "ci/cd"]
        },
        {
            "name": "Noise/Casual (Should Filter)",
            "messages": [
                {"role": "user", "content": "What's the weather like today? I hope it's sunny."},
                {"role": "assistant", "content": "I don't have access to current weather data, but you can check your local weather service for accurate information."}
            ],
            "expected_concepts": []
        }
    ]
    
    extraction_results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 Scenario {i}: {scenario['name']}")
        print(f"Input: {scenario['messages'][0]['content'][:80]}...")
        
        # Add memory
        start_time = time.time()
        response = requests.post('http://localhost:8000/v1/memories/', json={
            'messages': scenario['messages'],
            'user_id': user_id,
            'metadata': {'test': 'quality_assessment', 'scenario': scenario['name']}
        })
        processing_time = time.time() - start_time
        
        if response.status_code in [200, 201]:
            result = response.json()
            memories = result.get('data', {}).get('results', [])
            
            print(f"⏱️  Processing time: {processing_time:.1f}s")
            print(f"📊 Extracted {len(memories)} memories:")
            
            scenario_result = {
                'scenario': scenario['name'],
                'input_length': len(scenario['messages'][0]['content']),
                'processing_time': processing_time,
                'extracted_count': len(memories),
                'memories': [],
                'concept_coverage': 0
            }
            
            for j, memory in enumerate(memories):
                event = memory.get('event', 'UNKNOWN')
                memory_text = memory.get('memory', 'No memory')
                print(f"   {j+1}. [{event}] {memory_text}")
                
                scenario_result['memories'].append({
                    'event': event,
                    'text': memory_text,
                    'length': len(memory_text)
                })
            
            # Check concept coverage
            if scenario['expected_concepts']:
                all_memory_text = ' '.join([m['text'].lower() for m in scenario_result['memories']])
                found_concepts = [concept for concept in scenario['expected_concepts'] 
                                if concept.lower() in all_memory_text]
                scenario_result['concept_coverage'] = len(found_concepts) / len(scenario['expected_concepts'])
                scenario_result['found_concepts'] = found_concepts
                scenario_result['missing_concepts'] = [c for c in scenario['expected_concepts'] if c not in found_concepts]
                
                print(f"🎯 Concept coverage: {scenario_result['concept_coverage']:.1%}")
                print(f"✅ Found: {found_concepts}")
                if scenario_result['missing_concepts']:
                    print(f"❌ Missing: {scenario_result['missing_concepts']}")
            
            extraction_results.append(scenario_result)
        else:
            print(f"❌ Error: {response.status_code}")
    
    # Assert that the extraction was successful
    successful_extractions = sum(1 for r in extraction_results if r['extracted_count'] > 0)
    assert successful_extractions > 0, f"No memories were extracted from {len(extraction_results)} scenarios"
    
    # Assert concept coverage is reasonable  
    avg_concept_coverage = sum(r.get('concept_coverage', 0) for r in extraction_results) / len(extraction_results)
    assert avg_concept_coverage > 0.5, f"Average concept coverage {avg_concept_coverage:.1%} is too low"

def test_semantic_search_quality():
    """Test the quality of semantic search"""
    print(f"\n🔍 Testing Semantic Search Quality")
    print("=" * 60)
    
    user_id = f'search-test-{uuid.uuid4().hex[:8]}'
    
    # First, add some test memories
    test_memories = [
        "I'm a senior Python developer who prefers FastAPI over Flask. I always use type hints and async/await patterns. My preferred database is PostgreSQL with SQLAlchemy ORM.",
        "I'm building a microservices architecture for an e-commerce platform. Each service runs in Docker containers and communicates via gRPC. I use Redis for caching and Celery for background tasks.",
        "I work remotely from San Francisco and prefer using VS Code with the Python extension. I always write tests with pytest and use GitHub Actions for CI/CD."
    ]
    
    for memory_text in test_memories:
        requests.post('http://localhost:8000/v1/memories/', json={
            'messages': [{"role": "user", "content": memory_text}],
            'user_id': user_id
        })
    
    import time
    time.sleep(3)  # Wait for indexing
    
    search_tests = [
        {
            "query": "What programming languages does the user know?",
            "expected_keywords": ["python", "fastapi", "flask"]
        },
        {
            "query": "What databases does the user use?",
            "expected_keywords": ["postgresql", "redis"]
        },
        {
            "query": "What is the user's development environment?",
            "expected_keywords": ["vscode", "python extension", "pytest"]
        },
        {
            "query": "What architecture patterns does the user prefer?",
            "expected_keywords": ["microservices", "docker", "grpc"]
        },
        {
            "query": "Where does the user work?",
            "expected_keywords": ["san francisco", "remote"]
        }
    ]
    
    search_results = []
    
    for test in search_tests:
        print(f"\n❓ Query: '{test['query']}'")
        
        response = requests.post('http://localhost:8000/v1/memories/search/', json={
            'query': test['query'],
            'user_id': user_id,
            'limit': 5
        })
        
        if response.status_code in [200, 201]:
            results = response.json().get('data', {}).get('results', [])
            print(f"📊 Found {len(results)} results:")
            
            relevant_count = 0
            for i, result in enumerate(results[:3]):  # Show top 3
                score = result.get('score', 0)
                memory = result.get('memory', 'No memory')
                
                # Check relevance
                is_relevant = any(keyword.lower() in memory.lower() 
                                for keyword in test['expected_keywords'])
                if is_relevant:
                    relevant_count += 1
                
                relevance = "✅" if is_relevant else "❌"
                print(f"   {i+1}. {relevance} Score: {score:.3f} | {memory}")
            
            quality = relevant_count / min(len(results), 3) if results else 0
            print(f"🎯 Search quality: {quality:.1%} ({relevant_count}/{min(len(results), 3)} relevant)")
            
            search_results.append({
                'query': test['query'],
                'result_count': len(results),
                'relevant_count': relevant_count,
                'quality': quality,
                'top_score': results[0].get('score', 0) if results else 0
            })
        else:
            print(f"❌ Search failed: {response.status_code}")
    
    # Cleanup
    requests.delete(f'http://localhost:8000/v1/memories/?user_id={user_id}')
    
    # Assert that search quality is reasonable
    avg_quality = sum(r['quality'] for r in search_results) / len(search_results) if search_results else 0
    assert avg_quality > 0.3, f"Average search quality {avg_quality:.1%} is too low"

def test_full_conversation_processing():
    """Test how well the system handles full conversations"""
    print(f"\n🗨️ Testing Full Conversation Processing")
    print("=" * 60)
    
    user_id = f'conversation-test-{uuid.uuid4().hex[:8]}'
    
    # Multi-turn technical conversation
    conversation = [
        {"role": "user", "content": "I'm having trouble with my FastAPI application. The JWT authentication isn't working properly."},
        {"role": "assistant", "content": "JWT issues can be tricky. Are you using a specific library like python-jose or PyJWT?"},
        {"role": "user", "content": "I'm using PyJWT with RS256 algorithm. The token generation works but validation fails."},
        {"role": "assistant", "content": "RS256 requires both private and public keys. Are you sure you're using the correct public key for validation?"},
        {"role": "user", "content": "Ah, that might be it! I'm using the same key for both. Let me try with separate keys."},
        {"role": "assistant", "content": "Exactly! For RS256, you need an RSA key pair - private key for signing, public key for verification."},
        {"role": "user", "content": "Perfect! Now it works. I'll add some error handling for expired tokens too."},
        {"role": "assistant", "content": "Great idea! You might also want to implement token refresh logic for better user experience."}
    ]
    
    print(f"📝 Processing {len(conversation)} message conversation...")
    
    response = requests.post('http://localhost:8000/v1/memories/', json={
        'messages': conversation,
        'user_id': user_id,
        'metadata': {'test': 'full_conversation', 'message_count': len(conversation)}
    })
    
    if response.status_code in [200, 201]:
        result = response.json()
        memories = result.get('data', {}).get('results', [])
        
        print(f"📊 Extracted {len(memories)} memories:")
        
        for i, memory in enumerate(memories):
            event = memory.get('event', 'UNKNOWN')
            memory_text = memory.get('memory', 'No memory')
            print(f"   {i+1}. [{event}] {memory_text}")
        
        # Test context preservation
        print(f"\n🔍 Testing context preservation:")
        
        context_queries = [
            "What authentication method is the user using?",
            "What problem was the user facing?",
            "What library is the user using for JWT?",
            "What algorithm is being used?",
            "What was the solution to the problem?"
        ]
        
        context_scores = []
        for query in context_queries:
            search_response = requests.post('http://localhost:8000/v1/memories/search/', json={
                'query': query,
                'user_id': user_id,
                'limit': 2
            })
            
            if search_response.status_code in [200, 201]:
                search_results = search_response.json().get('data', {}).get('results', [])
                top_score = search_results[0].get('score', 0) if search_results else 0
                context_scores.append(top_score)
                
                print(f"❓ '{query}'")
                if search_results:
                    top_result = search_results[0]
                    print(f"   Score: {top_score:.3f} | {top_result.get('memory', 'No memory')[:60]}...")
                else:
                    print(f"   No results found")
        
        avg_context_score = sum(context_scores) / len(context_scores) if context_scores else 0
        print(f"\n📊 Average context preservation score: {avg_context_score:.3f}")
        
        # Cleanup
        requests.delete(f'http://localhost:8000/v1/memories/?user_id={user_id}')
        
        # Assert that conversation processing was successful
        assert len(memories) > 0, "No memories extracted from conversation"
        assert avg_context_score > 0.08, f"Context preservation score {avg_context_score:.3f} is too low"
    else:
        assert False, f"Error processing conversation: {response.status_code}"

def analyze_local_vs_mcp_approaches():
    """Analyze the differences between local implementation and MCP approach"""
    print(f"\n🔬 Local Mem0 vs MCP Server Analysis")
    print("=" * 60)
    
    comparison = {
        "Local Chrome Extension (Our Implementation)": {
            "Memory Type": "Conversational memories + facts + preferences",
            "Processing": "Full LLM extraction with context understanding",
            "Storage": "Qdrant vector database with semantic search",
            "Platforms": "ChatGPT, Claude, Perplexity, Grok, DeepSeek (web browsers)",
            "Use Case": "Cross-platform conversation memory sharing",
            "Memory Format": "Natural language extracted facts",
            "Search": "Semantic similarity search",
            "Privacy": "100% local processing",
            "Intelligence": "Context-aware memory extraction and decision making"
        },
        "MCP Server (github.com/mem0ai/mem0-mcp)": {
            "Memory Type": "Coding preferences + code snippets + patterns",
            "Processing": "Structured code preference storage",
            "Storage": "Mem0 API (cloud or local)",
            "Platforms": "Cursor IDE (via MCP protocol)",
            "Use Case": "Persistent coding preferences and patterns",
            "Memory Format": "Structured coding information",
            "Search": "Search through coding preferences",
            "Privacy": "Depends on Mem0 API configuration",
            "Intelligence": "Code-specific preference management"
        }
    }
    
    print("📊 Feature Comparison:")
    for category, details in comparison.items():
        print(f"\n🔹 {category}:")
        for feature, value in details.items():
            print(f"   {feature}: {value}")
    
    print(f"\n🎯 Complementary Use Cases:")
    print("   ✅ Local Extension: Web-based AI conversations with memory")
    print("   ✅ MCP Server: IDE-based coding with persistent preferences")
    print("   ✅ Combined: Unified memory across web AI + development environment")
    
    return comparison

def generate_comprehensive_report(extraction_results, search_results, conversation_stats, comparison):
    """Generate a comprehensive quality assessment report"""
    print(f"\n📋 Comprehensive Quality Assessment Report")
    print("=" * 60)
    
    # Memory extraction quality
    total_scenarios = len(extraction_results)
    successful_extractions = sum(1 for r in extraction_results if r['extracted_count'] > 0)
    avg_processing_time = sum(r['processing_time'] for r in extraction_results) / total_scenarios
    avg_concept_coverage = sum(r.get('concept_coverage', 0) for r in extraction_results) / total_scenarios
    
    print(f"🧠 Memory Extraction Quality:")
    print(f"   Success Rate: {successful_extractions}/{total_scenarios} ({successful_extractions/total_scenarios:.1%})")
    print(f"   Average Processing Time: {avg_processing_time:.1f}s")
    print(f"   Average Concept Coverage: {avg_concept_coverage:.1%}")
    
    # Search quality
    avg_search_quality = sum(r['quality'] for r in search_results) / len(search_results)
    avg_search_score = sum(r['top_score'] for r in search_results) / len(search_results)
    
    print(f"\n🔍 Semantic Search Quality:")
    print(f"   Average Relevance: {avg_search_quality:.1%}")
    print(f"   Average Top Score: {avg_search_score:.3f}")
    
    # Conversation processing
    memories_extracted, context_score = conversation_stats
    print(f"\n🗨️ Conversation Processing:")
    print(f"   Memories from full conversation: {memories_extracted}")
    print(f"   Context preservation score: {context_score:.3f}")
    
    # Overall assessment
    overall_score = (successful_extractions/total_scenarios + avg_concept_coverage + avg_search_quality + min(context_score, 1.0)) / 4
    
    print(f"\n🎯 Overall Quality Score: {overall_score:.1%}")
    
    if overall_score >= 0.8:
        print("🎉 EXCELLENT: Local Mem0 implementation is highly effective")
    elif overall_score >= 0.6:
        print("✅ GOOD: Local Mem0 implementation is adequately effective")
    else:
        print("⚠️ NEEDS IMPROVEMENT: Consider tuning LLM parameters")
    
    print(f"\n💡 Recommendations:")
    if avg_processing_time > 30:
        print("   - Consider using a smaller/faster LLM model")
    if avg_concept_coverage < 0.7:
        print("   - Tune LLM prompts for better concept extraction")
    if avg_search_quality < 0.7:
        print("   - Improve embedding model or search thresholds")
    
    print(f"\n🔗 Integration Recommendation:")
    print("   ✅ Local Extension + MCP Server = Complete AI Memory System")
    print("   - Use BOTH implementations for maximum coverage")
    print("   - Local extension for web AI conversations")
    print("   - MCP server for Cursor IDE integration")
    print("   - Shared local Mem0 instance for unified memory")

def main():
    try:
        print("🧠 Comprehensive Mem0 Quality Assessment")
        print("=" * 80)
        
        # Test local implementation quality
        extraction_results, user_id = test_local_mem0_quality()
        
        # Test semantic search
        search_results = test_semantic_search_quality(user_id)
        
        # Test full conversation processing
        conversation_stats = test_full_conversation_processing()
        
        # Analyze approaches
        comparison = analyze_local_vs_mcp_approaches()
        
        # Generate comprehensive report
        generate_comprehensive_report(extraction_results, search_results, conversation_stats, comparison)
        
        # Cleanup
        print(f"\n🧹 Cleaning up test data...")
        requests.delete(f'http://localhost:8000/v1/memories/?user_id={user_id}')
        
        print("\n" + "=" * 80)
        print("🎯 Comprehensive Assessment Complete!")
        
    except Exception as e:
        print(f"❌ Error during assessment: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
