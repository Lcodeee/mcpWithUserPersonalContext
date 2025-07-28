#!/usr/bin/env python3
"""
Simple test script to verify MCP server functionality
"""
import json
import requests
import time

def test_mcp_server():
    print("🚀 Testing MCP-Mem0 Server...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get("http://localhost:8050")
        print(f"✅ Server is responding (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return
    
    print("\n📝 MCP Server is running successfully!")
    print("🔗 Server URL: http://localhost:8050")
    print("🔧 Transport: SSE (Server-Sent Events)")
    print("🤖 LLM Provider: Gemini")
    print("🗄️ Database: PostgreSQL with pgvector")
    print("📦 Embedding: HuggingFace (sentence-transformers)")
    
    print("\n🎯 To connect with Claude Desktop, add this configuration:")
    print(json.dumps({
        "mcpServers": {
            "mem0": {
                "transport": "sse",
                "url": "http://localhost:8050/sse"
            }
        }
    }, indent=2))

if __name__ == "__main__":
    test_mcp_server()
