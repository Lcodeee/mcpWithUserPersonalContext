#!/usr/bin/env python3
"""
Ad-hoc test: Read file and call save_memory endpoint directly
"""
import requests
import json

def test_file_via_save_endpoint():
    print("🧪 Testing file loading via save_memory endpoint")
    
    # Read the file directly
    try:
        with open('test_files/recipes.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"📁 Read file content ({len(content)} chars):")
        print(f"   {content[:100]}...")
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return
    
    # Call save_memory endpoint with file content
    try:
        response = requests.post(
            "http://mcp_server:8050/save_memory",
            json={"text": content}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully saved via save_memory endpoint!")
            print(f"   Message: {result['message']}")
            print(f"   Result: {result['result']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error calling save_memory: {e}")

if __name__ == "__main__":
    test_file_via_save_endpoint()