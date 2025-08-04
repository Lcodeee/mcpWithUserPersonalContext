#!/usr/bin/env python3
"""
Test script for file loading functionality
"""
import requests
import json
import os

def test_file_loading():
    print("🧪 Testing File Loading Functionality")
    print("=" * 50)
    
    base_url = "http://mcp_server:8050"
    
    # בדיקת בריאות השרת
    print("\n1. Testing server health...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print("❌ Server health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # רשימת קבצים לבדיקה
    test_files = [
        "test_files/recipes.txt",
        "test_files/tech_notes.txt", 
        "test_files/travel_diary.txt"
    ]
    
    # טעינת קבצים
    print("\n2. Loading files into memory...")
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                response = requests.post(
                    f"{base_url}/load_file",
                    json={"file_path": file_path}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Loaded {file_path}")
                    print(f"   Content length: {result['content_length']} characters")
                else:
                    print(f"❌ Failed to load {file_path}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # בדיקת חיפוש
    print("\n3. Testing search functionality...")
    search_queries = [
        "איך מכינים פסטה?",
        "מה זה Docker?", 
        "איפה ביקרתי בחופשה?"
    ]
    
    for query in search_queries:
        try:
            response = requests.post(
                f"{base_url}/search_memories",
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                memories = result.get('memories', [])
                print(f"\n🔍 Query: {query}")
                print(f"   Found {len(memories)} relevant memories:")
                for i, memory in enumerate(memories[:2], 1):  # הצגת 2 הראשונים
                    print(f"   {i}. {memory[:100]}...")
            else:
                print(f"❌ Search failed for: {query}")
                
        except Exception as e:
            print(f"❌ Search error for '{query}': {e}")
    
    print("\n" + "=" * 50)
    print("🎉 File loading test completed!")

if __name__ == "__main__":
    test_file_loading()