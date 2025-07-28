# MCP-Mem0: Long-Term Memory for AI Agents

A Model Context Protocol (MCP) server integrated with Mem0 for providing AI agents with persistent memory capabilities using Gemini LLM and PostgreSQL vector storage.

## Quick Start

1. **Start the system:**
   ```bash
   docker-compose up postgres_mem0 -d
   docker-compose up mcp_server -d
   ```

2. **Test memory storage:**
   ```bash
   docker-compose exec gemini_client python -c "
   import requests
   response = requests.post('http://mcp_server:8050/save_memory', json={'text': 'I love vanilla ice cream'})
   if response.status_code == 200:
       result = response.json()
       print('💾 Memory saved:', result.get('message', 'Success'))
       print('📋 Details:', result.get('result', {}))
   else:
       print('❌ Failed:', response.text)
   "
   ```

3. **Search memories:**
   ```bash
   docker-compose exec gemini_client python -c "
   import requests
   response = requests.post('http://mcp_server:8050/search_memories', json={'query': 'What desserts do I like?'})
   if response.status_code == 200:
       result = response.json()
       print('🧠 Found memories:', result.get('memories', []))
   else:
       print('❌ Failed:', response.text)
   "
   ```

## Testing Options

### 1. Basic Memory Test
```bash
docker-compose exec gemini_client python test_memory.py
```

### 2. Comprehensive Test Drive
```bash
docker-compose exec gemini_client python test_drive.py
```

### 3. Interactive Demo
```bash
docker-compose exec -it gemini_client python interactive-demo-test.py
```

## API Endpoints

- **POST** `/save_memory` - Store information
- **POST** `/search_memories` - Search with semantic matching
- **GET** `/get_all_memories` - Retrieve all stored memories
- **GET** `/` - Health check

## Configuration

Set your Gemini API key in `.env`:
```env
LLM_API_KEY=your_gemini_api_key_here
```

## Architecture

- **LLM**: Gemini 2.0 Flash Exp
- **Embeddings**: HuggingFace sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: PostgreSQL with pgvector
- **Transport**: HTTP API (port 8050)

## MCP Client Integration

### SSE Configuration
```json
{
  "mcpServers": {
    "mem0": {
      "transport": "sse",
      "url": "http://localhost:8050/sse"
    }
  }
}
```

The system is ready for integration with Claude Desktop, Windsurf, or any MCP-compatible client.