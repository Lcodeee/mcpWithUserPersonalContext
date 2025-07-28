#!/usr/bin/env python3
"""
Test Drive for MCP-Mem0 Memory System
Comprehensive demonstration of memory capabilities
"""
import requests
import json
import time

BASE_URL = "http://mcp_server:8050"

def save_memory(text):
    response = requests.post(f"{BASE_URL}/save_memory", json={"text": text})
    return response.json() if response.status_code == 200 else None

def search_memories(query, limit=3):
    response = requests.post(f"{BASE_URL}/search_memories", json={"query": query, "limit": limit})
    return response.json() if response.status_code == 200 else None

def get_all_memories():
    response = requests.get(f"{BASE_URL}/get_all_memories")
    return response.json() if response.status_code == 200 else None

def test_drive():
    print("🚗 MCP-Mem0 Test Drive")
    print("=" * 50)
    
    # Store personal preferences
    print("\n📝 Storing personal information...")
    memories = [
        "My name is Alex and I'm a software engineer",
        "I love Italian food, especially carbonara and tiramisu",
        "I work remotely from San Francisco",
        "My favorite programming languages are Python and TypeScript",
        "I have a cat named Whiskers who loves to sit on my keyboard",
        "I'm learning Spanish and can speak basic conversational phrases",
        "I prefer dark roast coffee and drink 3 cups per day"
    ]
    
    for memory in memories:
        result = save_memory(memory)
        if result:
            print(f"✅ Saved: {memory[:50]}...")
        time.sleep(1)
    
    # Test semantic search capabilities
    print("\n🔍 Testing semantic search...")
    
    queries = [
        "What programming languages does the user know?",
        "Tell me about the user's pet",
        "What are the user's food preferences?",
        "Where does the user work?",
        "What languages is the user learning?"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        result = search_memories(query)
        if result and result.get('memories'):
            for memory in result['memories']:
                print(f"   💡 {memory}")
        else:
            print("   ❌ No relevant memories found")
    
    # Show all stored memories
    print("\n📚 All stored memories:")
    all_memories = get_all_memories()
    if all_memories and all_memories.get('memories'):
        for i, memory in enumerate(all_memories['memories'], 1):
            print(f"   {i}. {memory}")
    
    print("\n" + "=" * 50)
    print("🎉 Test drive completed!")

if __name__ == "__main__":
    test_drive()