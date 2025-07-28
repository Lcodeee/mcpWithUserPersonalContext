#!/usr/bin/env python3
"""
Interactive Demo Test for MCP-Mem0 Memory System
Talk with the system, add memories, and test recall
"""
import requests
import json

BASE_URL = "http://mcp_server:8050"

def save_memory(text):
    response = requests.post(f"{BASE_URL}/save_memory", json={"text": text})
    if response.status_code == 200:
        result = response.json()
        print(f"💾 Memory saved: {result.get('message', 'Success')}")
        return True
    else:
        print(f"❌ Failed to save: {response.text}")
        return False

def search_memories(query):
    response = requests.post(f"{BASE_URL}/search_memories", json={"query": query})
    if response.status_code == 200:
        result = response.json()
        memories = result.get('memories', [])
        if memories:
            print("🧠 I remember:")
            for memory in memories:
                print(f"   • {memory}")
        else:
            print("🤔 I don't have any memories about that.")
        return memories
    else:
        print(f"❌ Search failed: {response.text}")
        return []

def get_all_memories():
    response = requests.get(f"{BASE_URL}/get_all_memories")
    if response.status_code == 200:
        result = response.json()
        memories = result.get('memories', [])
        print(f"📚 Total memories: {len(memories)}")
        for i, memory in enumerate(memories, 1):
            print(f"   {i}. {memory}")
        return memories
    else:
        print(f"❌ Failed to get memories: {response.text}")
        return []

def interactive_demo():
    print("🤖 MCP-Mem0 Interactive Demo")
    print("=" * 50)
    print("Commands:")
    print("  'remember <text>' - Save a memory")
    print("  'recall <query>' - Search memories")
    print("  'show all' - Show all memories")
    print("  'quit' - Exit")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'show all':
                get_all_memories()
            elif user_input.lower().startswith('remember '):
                text = user_input[9:]  # Remove 'remember '
                save_memory(text)
            elif user_input.lower().startswith('recall '):
                query = user_input[7:]  # Remove 'recall '
                search_memories(query)
            else:
                # Treat as a question/query
                search_memories(user_input)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    interactive_demo()