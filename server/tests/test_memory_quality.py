#!/usr/bin/env python3
"""
Test Memory Quality - Examine what gets stored by local Mem0
"""

import requests
import json
import uuid

def test_memory_quality():
    """Test what memories get stored and their quality"""
    user_id = f'quality-test-{uuid.uuid4().hex[:8]}'
    
    # Test cases with different types of content
    test_cases = [
        {
            "name": "Professional Background",
            "messages": [
                {"role": "user", "content": "I am a senior Python developer who loves using FastAPI for building APIs. I work at a fintech startup in San Francisco and prefer using PostgreSQL as my database."},
                {"role": "assistant", "content": "That's great! FastAPI is excellent for building high-performance APIs. How do you handle database migrations in your PostgreSQL setup?"}
            ]
        },
        {
            "name": "Personal Preferences", 
            "messages": [
                {"role": "user", "content": "I really hate when code doesn't have proper type hints. I always use mypy for static type checking and black for code formatting."},
                {"role": "assistant", "content": "Type hints definitely make code more maintainable! Do you have any specific mypy configuration you prefer?"}
            ]
        },
        {
            "name": "Project Context",
            "messages": [
                {"role": "user", "content": "I'm currently building a microservices architecture using Docker containers. Each service has its own PostgreSQL database and they communicate via REST APIs."},
                {"role": "assistant", "content": "That sounds like a solid architecture! Are you using any service mesh or API gateway for inter-service communication?"}
            ]
        },
        {
            "name": "Casual Chat (Should Filter)",
            "messages": [
                {"role": "user", "content": "How's the weather today?"},
                {"role": "assistant", "content": "I don't have access to current weather data, but you can check your local weather service for accurate information."}
            ]
        }
    ]
    
    print("🧪 Testing Memory Quality")
    print("=" * 60)
    
    all_memories = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n📝 Test Case {i+1}: {test_case['name']}")
        print(f"Input: {test_case['messages'][0]['content'][:100]}...")
        
        # Add memory
        response = requests.post('http://localhost:8000/v1/memories/', json={
            'messages': test_case['messages'],
            'user_id': user_id,
            'metadata': {'test': 'quality_check', 'case': test_case['name']}
        })
        
        if response.status_code in [200, 201]:
            result = response.json()
            
            # Examine what was extracted
            if 'data' in result and 'results' in result['data']:
                memories = result['data']['results']
                print(f"📊 Extracted {len(memories)} memories:")
                
                for j, memory in enumerate(memories):
                    event = memory.get('event', 'UNKNOWN')
                    memory_text = memory.get('memory', 'No memory text')
                    print(f"   {j+1}. [{event}] {memory_text}")
                    all_memories.append({
                        'test_case': test_case['name'],
                        'event': event,
                        'memory': memory_text,
                        'input_length': len(test_case['messages'][0]['content']),
                        'memory_length': len(memory_text)
                    })
            else:
                print("   ⚠️  No memories extracted")
        else:
            print(f"   ❌ Error: {response.status_code}")
    
    # Get all stored memories
    print(f"\n📋 Retrieving all memories for user: {user_id}")
    memories_response = requests.get(f'http://localhost:8000/v1/memories/?user_id={user_id}')
    
    if memories_response.status_code in [200, 201]:
        all_stored = memories_response.json()
        stored_memories = all_stored.get('data', {}).get('results', [])
        
        print(f"💾 Total stored memories: {len(stored_memories)}")
        
        # Analyze memory quality
        print("\n🔍 Memory Quality Analysis:")
        print("=" * 40)
        
        for memory in stored_memories:
            memory_text = memory.get('memory', 'No memory')
            memory_id = memory.get('id', 'unknown')
            print(f"Memory ID: {memory_id}")
            print(f"Content: {memory_text}")
            print(f"Length: {len(memory_text)} characters")
            print("-" * 40)
        
        # Test semantic search
        print("\n🔍 Testing Semantic Search:")
        search_queries = [
            "What programming language does the user prefer?",
            "What database does the user use?", 
            "Where does the user work?",
            "What are the user's code formatting preferences?"
        ]
        
        for query in search_queries:
            search_response = requests.post('http://localhost:8000/v1/memories/search/', json={
                'query': query,
                'user_id': user_id,
                'limit': 3
            })
            
            if search_response.status_code in [200, 201]:
                search_results = search_response.json().get('data', {}).get('results', [])
                print(f"\nQuery: '{query}'")
                print(f"Results: {len(search_results)}")
                
                for result in search_results[:2]:  # Show top 2
                    score = result.get('score', 0)
                    memory_text = result.get('memory', 'No memory')
                    print(f"  Score: {score:.3f} | {memory_text[:80]}...")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test data for user: {user_id}")
    requests.delete(f'http://localhost:8000/v1/memories/?user_id={user_id}')
    
    # Assert that some memories were extracted
    assert len(all_memories) > 0, "No memories were extracted from test cases"

def test_full_chat_storage():
    """Test if we can store full conversations"""
    print("\n🗨️ Testing Full Chat Storage")
    print("=" * 60)
    
    user_id = f'chat-test-{uuid.uuid4().hex[:8]}'
    
    # Simulate a multi-turn conversation
    full_conversation = [
        {"role": "user", "content": "I need help with my Python project. I'm building a web scraper."},
        {"role": "assistant", "content": "I'd be happy to help! What library are you using for web scraping?"},
        {"role": "user", "content": "I'm using requests and BeautifulSoup, but I'm having issues with rate limiting."},
        {"role": "assistant", "content": "For rate limiting, you can add delays between requests using time.sleep() or implement exponential backoff."},
        {"role": "user", "content": "That makes sense. I'm also storing the scraped data in a MySQL database."},
        {"role": "assistant", "content": "Great choice! Are you using any ORM like SQLAlchemy, or raw SQL queries?"}
    ]
    
    # Add the full conversation
    response = requests.post('http://localhost:8000/v1/memories/', json={
        'messages': full_conversation,
        'user_id': user_id,
        'metadata': {'test': 'full_chat', 'conversation_length': len(full_conversation)}
    })
    
    if response.status_code in [200, 201]:
        result = response.json()
        print("✅ Full conversation processed")
        
        # Check what memories were extracted
        if 'data' in result and 'results' in result['data']:
            memories = result['data']['results']
            print(f"📊 Extracted {len(memories)} memories from {len(full_conversation)} messages:")
            
            for memory in memories:
                event = memory.get('event', 'UNKNOWN')
                memory_text = memory.get('memory', 'No memory')
                print(f"  [{event}] {memory_text}")
    
    # Test if conversation context is preserved in search
    print("\n🔍 Testing conversation context preservation:")
    context_queries = [
        "What is the user building?",
        "What libraries is the user using?",
        "What database is the user using?",
        "What problem is the user facing?"
    ]
    
    for query in context_queries:
        search_response = requests.post('http://localhost:8000/v1/memories/search/', json={
            'query': query,
            'user_id': user_id,
            'limit': 2
        })
        
        if search_response.status_code in [200, 201]:
            results = search_response.json().get('data', {}).get('results', [])
            print(f"Query: '{query}' -> {len(results)} results")
            for result in results:
                score = result.get('score', 0)
                memory = result.get('memory', 'No memory')
                print(f"  {score:.3f}: {memory[:60]}...")
    
    # Cleanup
    requests.delete(f'http://localhost:8000/v1/memories/?user_id={user_id}')

if __name__ == "__main__":
    try:
        print("🧠 Local Mem0 Memory Quality Assessment")
        print("=" * 60)
        
        # Test basic memory quality
        memories = test_memory_quality()
        
        # Test full chat storage
        test_full_chat_storage()
        
        print("\n" + "=" * 60)
        print("🎯 Memory Quality Assessment Complete")
        
    except Exception as e:
        print(f"❌ Error: {e}") 
