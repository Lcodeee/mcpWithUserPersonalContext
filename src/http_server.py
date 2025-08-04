#!/usr/bin/env python3
"""
HTTP API Server for MCP-Mem0 functionality
-------------------------------------------
Creates an HTTP REST API wrapper around the MCP memory functionality.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import uvicorn
import json
import os
import json as json_lib

from utils import get_mem0_client

load_dotenv()

# Default user ID for memory operations
DEFAULT_USER_ID = "user"

# Initialize Mem0 client
mem0_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the Mem0 client on startup"""
    global mem0_client
    try:
        print("🔄 Starting Mem0 client initialization...")
        print(f"📊 DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")
        print(f"🔑 LLM_PROVIDER: {os.environ.get('LLM_PROVIDER', 'NOT SET')}")
        print(f"🔑 LLM_API_KEY: {'SET' if os.environ.get('LLM_API_KEY') else 'NOT SET'}")
        
        mem0_client = get_mem0_client()
        print(f"✅ Mem0 client initialized successfully")
        yield
    except Exception as e:
        print(f"❌ Failed to initialize Mem0 client: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Cleanup if needed
        pass

# Create FastAPI app
app = FastAPI(
    title="MCP-Mem0 HTTP API",
    description="HTTP API for MCP memory storage and retrieval",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class SaveMemoryRequest(BaseModel):
    text: str

class SearchMemoryRequest(BaseModel):
    query: str
    limit: int = 3

# API endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "MCP-Mem0 HTTP API is running"}

@app.post("/save_memory")
async def save_memory(request: SaveMemoryRequest):
    """Save information to long-term memory"""
    try:
        messages = [{"role": "user", "content": request.text}]
        result = mem0_client.add(messages, user_id=DEFAULT_USER_ID)
        return {
            "success": True,
            "message": f"Successfully saved memory: {request.text[:100]}..." if len(request.text) > 100 else f"Successfully saved memory: {request.text}",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving memory: {str(e)}")

@app.get("/get_all_memories")
async def get_all_memories():
    """Get all stored memories for the user"""
    try:
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
        return {
            "success": True,
            "memories": flattened_memories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memories: {str(e)}")

@app.post("/search_memories")
async def search_memories(request: SearchMemoryRequest):
    """Search memories using semantic search"""
    try:
        memories = mem0_client.search(request.query, user_id=DEFAULT_USER_ID, limit=request.limit)
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
        return {
            "success": True,
            "memories": flattened_memories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching memories: {str(e)}")
    



@app.get("/list_files")
async def list_files(directory: str = "test_files"):
    """List available files in directory"""
    try:
        if not os.path.exists(directory):
            return {"files": [], "message": f"Directory {directory} not found"}
        
        files = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                files.append({
                    "name": file,
                    "path": file_path,
                    "size": os.path.getsize(file_path)
                })
        
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {e}")

    

# @app.post("/load_file")
# async def load_file_endpoint(request: dict):
#     """Load text from file and save to memory"""
#     try:
#         file_path = request.get("file_path")
#         if not file_path:
#             raise HTTPException(status_code=400, detail="file_path is required")
        
#         # בדיקה שהקובץ קיים
#         if not os.path.exists(file_path):
#             raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
#         # קריאת הקובץ
#         with open(file_path, 'r', encoding='utf-8') as file:
#             content = file.read()
        
#         if not content.strip():
#             raise HTTPException(status_code=400, detail="File is empty")
        
#         # שמירה בזיכרון עם מידע על המקור
#         memory_text = f"[File: {file_path}]\n{content}"
        
#         # שימוש בלקוח הזיכרון הקיים
#         global mem0_client
#         if mem0_client is None:
#             mem0_client = get_mem0_client()
        
#         messages = [{"role": "user", "content": memory_text}]
#         print(f"🔍 DEBUG: About to save memory with user_id={DEFAULT_USER_ID}")
#         print(f"🔍 DEBUG: Memory text length: {len(memory_text)}")
#         print(f"🔍 DEBUG: Messages format: {messages}")
#         result = mem0_client.add(messages, user_id=DEFAULT_USER_ID)
#         print(f"🔍 DEBUG: Result from mem0_client.add: {result}")
        
#         return {
#             "success": True,
#             "message": f"Successfully loaded file: {file_path}",
#             "file_path": file_path,
#             "content_length": len(content),
#             "result": result
#         }
        
#     except Exception as e:
#         print(f"Error loading file: {e}")
#         raise HTTPException(status_code=500, detail=f"Error loading file: {e}")

@app.post("/load_file_simple")
async def load_file_simple(request: dict):
    """Load text from file and save to memory - simple working version"""
    try:
        file_path = request.get("file_path")
        if not file_path:
            raise HTTPException(status_code=400, detail="file_path is required")
        
        # Read the file directly
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        if file_path.endswith('.json'):
            try:
                data = json_lib.loads(content)
                content = json_lib.dumps(data, indent=2, ensure_ascii=False)
            except:
                pass 
            
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Use the exact same approach as save_memory - just pass content directly
        messages = [{"role": "user", "content": content}]
        result = mem0_client.add(messages, user_id=DEFAULT_USER_ID)
        
        return {
            "success": True,
            "message": f"Successfully loaded file: {file_path}",
            "file_path": file_path,
            "content_length": len(content),
            "result": result
        }
        
    except Exception as e:
        print(f"Error loading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading file: {e}")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8050"))
    )
