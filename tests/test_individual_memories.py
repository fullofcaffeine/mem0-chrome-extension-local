#!/usr/bin/env python3
"""
Test individual memory addition to avoid consolidation issues
"""

import asyncio
import aiohttp
import json

async def test_individual_memory_storage():
    """Test adding memories individually to see how many get stored"""
    
    base_url = "http://localhost:8000"
    user_id = "test-individual-user"
    
    # Test memories - completely unrelated topics
    test_memories = [
        {"content": "I have a pet dog named Max", "topic": "pets"},
        {"content": "I work at Google as an engineer", "topic": "work"}, 
        {"content": "I live in San Francisco", "topic": "location"},
        {"content": "I drive a red Tesla Model 3", "topic": "car"},
        {"content": "I prefer tea over coffee", "topic": "beverages"},
        {"content": "I love playing tennis", "topic": "hobbies"},
        {"content": "My favorite color is blue", "topic": "preferences"},
        {"content": "I speak English and Spanish", "topic": "languages"}
    ]
    
    print("🧪 Testing Individual Memory Storage")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Clear any existing memories first
        print("🗑️ Clearing existing memories...")
        try:
            await session.delete(f"{base_url}/v1/memories/?user_id={user_id}")
            print("  ✅ Cleared existing memories")
        except:
            print("  ⚠️ No existing memories to clear")
        
        print()
        
        # Add memories one by one with delays
        print("📝 Adding memories individually...")
        for i, memory_info in enumerate(test_memories):
            try:
                print(f"  Adding: {memory_info['content']}")
                
                response = await session.post(
                    f"{base_url}/v1/memories/",
                    json={
                        "messages": [{"role": "user", "content": memory_info["content"]}],
                        "user_id": user_id
                    }
                )
                
                if response.status in [200, 201]:  # Accept both 200 and 201 for successful creation
                    data = await response.json()
                    if data.get("data") and data["data"].get("results"):
                        ops = data["data"]["results"]
                        print(f"    ✅ Operations: {len(ops)}")
                        for op in ops:
                            event = op.get("event", "")
                            memory = op.get("memory", "")[:50]
                            print(f"      {event}: {memory}")
                    else:
                        print(f"    ✅ Added successfully")
                else:
                    print(f"    ❌ Failed: {response.status}")
                
                # Wait between additions to avoid consolidation
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        print()
        
        # Check how many memories are actually stored
        print("📊 Checking stored memories...")
        try:
            response = await session.get(f"{base_url}/v1/memories/?user_id={user_id}")
            
            if response.status == 200:
                data = await response.json()
                memories = data.get("data", {}).get("results", [])
                print(f"  📈 Total memories stored: {len(memories)}")
                print("  📋 Stored memories:")
                for i, memory in enumerate(memories):
                    print(f"    {i+1}. {memory.get('memory', 'No memory')}")
            else:
                print(f"  ❌ Failed to get memories: {response.status}")
                
        except Exception as e:
            print(f"  ❌ Error getting memories: {e}")
        
        print()
        
        # Test searches for each topic
        print("🔍 Testing topic-specific searches...")
        search_tests = [
            ("pets", "What pets do I have?"),
            ("work", "Where do I work?"), 
            ("location", "Where do I live?"),
            ("car", "What car do I drive?"),
            ("beverages", "What drinks do I prefer?"),
            ("hobbies", "What sports do I play?"),
            ("preferences", "What's my favorite color?"),
            ("languages", "What languages do I speak?")
        ]
        
        for topic, query in search_tests:
            try:
                response = await session.post(
                    f"{base_url}/v1/memories/search/",
                    json={
                        "query": query,
                        "user_id": user_id,
                        "limit": 5
                    }
                )
                
                if response.status == 200:
                    data = await response.json()
                    results = data.get("data", {}).get("results", [])
                    print(f"  🔍 '{query}' → {len(results)} results")
                    for result in results[:2]:  # Show top 2
                        memory = result.get("memory", "")[:60]
                        score = result.get("score", 0)
                        print(f"    - (score: {score:.3f}) {memory}")
                else:
                    print(f"  ❌ Search failed for '{query}': {response.status}")
                    
            except Exception as e:
                print(f"  ❌ Error searching '{query}': {e}")

    print("\n✅ Individual memory test completed!")

if __name__ == "__main__":
    asyncio.run(test_individual_memory_storage()) 
