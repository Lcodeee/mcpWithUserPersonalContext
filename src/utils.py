from mem0 import Memory
import os
import google.generativeai as genai

def get_mem0_client():
    """Get a configured Mem0 client instance - USING GEMINI EVERYWHERE LLM IS NEEDED."""
    print("🔄 Starting Mem0 client initialization with GEMINI EVERYWHERE...")
    
    # Get environment variables
    database_url = os.getenv('DATABASE_URL', 'postgresql://mem0_user:mem0_password@localhost:5432/mem0_db')
    llm_provider = os.getenv('LLM_PROVIDER', 'gemini').lower()
    gemini_api_key = os.getenv('LLM_API_KEY', '')
    llm_model = os.getenv('LLM_CHOICE', 'gemini-2.0-flash-exp')
    
    print(f"📊 DATABASE_URL: {database_url}")
    print(f"🔑 LLM_PROVIDER: {llm_provider}")
    print(f"🔑 LLM_MODEL: {llm_model}")
    print(f"🔑 GEMINI_API_KEY: {'SET' if gemini_api_key else 'NOT SET'}")
    
    print("🔄 Setting up Mem0 client configuration with PURE GEMINI...")
    
    # Configure Google Generative AI
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        print("✅ Configured Google Generative AI with Gemini API key")
    
    # Configuration using PURE GEMINI - NO OPENAI ANYWHERE!
    config = {
        "llm": {
            "provider": "gemini",
            "config": {
                "model": llm_model,
                "api_key": gemini_api_key,
                "temperature": 0.2,
                "max_tokens": 2000
            }
        },
        "embedder": {
            "provider": "huggingface",
            "config": {
                "model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        },
        "vector_store": {
            "provider": "supabase",
            "config": {
                "connection_string": database_url,
                "collection_name": "mem0_test",
                "embedding_model_dims": 384
            }
        }
    }
    
    print("📋 Config summary - PURE GEMINI EVERYWHERE:")
    print(f"   - LLM provider: {llm_provider} (PURE GEMINI)")
    print(f"   - LLM model: {llm_model}")
    print(f"   - Embedder provider: huggingface")  
    print(f"   - Vector store provider: supabase")
    print(f"   - Database URL: {database_url[:50]}...")
    
    try:
        print("🔄 Creating Memory client with PURE GEMINI...")
        client = Memory.from_config(config)
        print("✅ Memory client created successfully with PURE GEMINI!")
        return client
        
    except Exception as e:
        print(f"❌ Failed to create Memory client: {e}")
        print(f"❌ Full error: {str(e)}")
        raise Exception(f"Failed to initialize Mem0 client: {e}")

# Global variable to store the mem0 client
mem0_client = None