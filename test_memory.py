#!/usr/bin/env python3
"""
Test script for MCP-Mem0 memory functionality
Runs inside Docker container to test the HTTP API
"""
import requests
import json
import time

# Server URL (container network)
BASE_URL = "http://mcp_server:8050"

def test_memory_system():
    print("🧪 Testing MCP-Mem0 Memory System")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is healthy:", response.json())
        else:
            print("❌ Server health check failed:", response.status_code)
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Save memory - "I like pasta"
    print("\n2. Saving memory: 'I like pasta'...")
    try:
        memory_data = {
            "text": "I like pasta"
        }
        response = requests.post(f"{BASE_URL}/save_memory", json=memory_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Memory saved successfully!")
            print(f"   Response: {result}")
        else:
            print(f"❌ Failed to save memory: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error saving memory: {e}")
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Test 3: Search for food preferences
    print("\n3. Searching for food preferences...")
    try:
        search_data = {
            "query": "What food does the user like?"
        }
        response = requests.post(f"{BASE_URL}/search_memories", json=search_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Search completed!")
            print(f"   Found memories: {result}")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error searching memories: {e}")
    
    # Test 4: Get all memories
    print("\n4. Getting all memories...")
    try:
        response = requests.get(f"{BASE_URL}/get_all_memories")
        if response.status_code == 200:
            result = response.json()
            print("✅ Retrieved all memories!")
            print(f"   Total memories: {len(result.get('memories', []))}")
            for i, memory in enumerate(result.get('memories', []), 1):
                print(f"   Memory {i}: {memory}")
        else:
            print(f"❌ Failed to get memories: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error getting memories: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Memory system test completed!")

if __name__ == "__main__":
    test_memory_system()
