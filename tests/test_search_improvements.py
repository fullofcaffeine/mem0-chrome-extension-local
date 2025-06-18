#!/usr/bin/env python3
"""
Test script to verify search improvements for general memory retrieval
"""

import asyncio
import aiohttp
import json

async def test_search_functionality():
    """Test the improved search functionality"""
    
    base_url = "http://localhost:8000"
    user_id = "test-search-user"
    
    # Test memories to add
    test_memories = [
        "I work as a software engineer at Google",
        "My favorite programming language is Python", 
        "I live in San Francisco",
        "I love playing tennis on weekends",
        "My car is a red Tesla Model 3",
        "I have a dog named Max",
        "I prefer tea over coffee",
        "I'm learning Spanish in my free time"
    ]
    
    print("🧪 Testing Enhanced Memory Search Functionality")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Add test memories
        print("📝 Adding test memories...")
        for i, memory in enumerate(test_memories):
            try:
                response = await session.post(
                    f"{base_url}/v1/memories/",
                    json={
                        "messages": [{"role": "user", "content": memory}],
                        "user_id": user_id
                    }
                )
                if response.status in [200, 201]:  # Accept both 200 and 201
                    print(f"  ✅ Added: {memory}")
                else:
                    print(f"  ❌ Failed to add: {memory}")
            except Exception as e:
                print(f"  ❌ Error adding '{memory}': {e}")
        
        print()
        
        # 2. Test various search queries
        test_queries = [
            "What do I do for work?",
            "Where do I live?",
            "What are my hobbies?", 
            "What programming languages do I know?",
            "What pets do I have?",
            "What car do I drive?",
            "What beverages do I prefer?",
            "What languages am I learning?"
        ]
        
        print("🔍 Testing search queries...")
        for query in test_queries:
            try:
                response = await session.post(
                    f"{base_url}/v1/memories/search/",
                    json={
                        "query": query,
                        "user_id": user_id,
                        "limit": 10
                    }
                )
                
                if response.status == 200:
                    data = await response.json()
                    results = data.get("data", {}).get("results", [])
                    print(f"\n📊 Query: '{query}'")
                    print(f"   Found {len(results)} memories:")
                    for i, result in enumerate(results[:3]):  # Show top 3
                        memory = result.get("memory", "No memory")
                        score = result.get("score", 0)
                        print(f"     {i+1}. (score: {score:.3f}) {memory}")
                    if len(results) > 3:
                        print(f"     ... and {len(results) - 3} more")
                else:
                    print(f"❌ Search failed for '{query}': {response.status}")
                    
            except Exception as e:
                print(f"❌ Error searching '{query}': {e}")
        
        print()
        
        # 3. Test all memories retrieval
        print("📋 Testing get all memories...")
        try:
            response = await session.get(
                f"{base_url}/v1/memories/",
                params={"user_id": user_id, "limit": 100}
            )
            
            if response.status == 200:
                data = await response.json()
                all_memories = data.get("data", {}).get("results", [])
                print(f"   Total memories stored: {len(all_memories)}")
                print("   All memories:")
                for i, memory in enumerate(all_memories):
                    memory_text = memory.get("memory", "No memory")
                    print(f"     {i+1}. {memory_text}")
            else:
                print(f"❌ Failed to get all memories: {response.status}")
                
        except Exception as e:
            print(f"❌ Error getting all memories: {e}")

    print("\n✅ Search functionality test completed!")

if __name__ == "__main__":
    asyncio.run(test_search_functionality()) 
