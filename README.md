# userInfoMcp - MCP Memory Server

A Model Context Protocol (MCP) server with persistent memory using Gemini AI and PostgreSQL.

## Quick Start

**Prerequisites:** Docker Desktop and a Gemini API key

1. **Clone and setup:**
   ```bash
   git clone https://github.com/Lcodeee/mcpWithUserPersonalContext.git
   cd mcpWithUserPersonalContext
   cp .env.example .env
   ```

2. **Add your Gemini API key to `.env`:**
   ```env
   LLM_API_KEY=your_gemini_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Start the system:**
   ```bash
   docker-compose up -d
   ```

4. **Wait 2 minutes for initialization, then test:**
   ```bash
   docker-compose exec gemini_client python test_memory.py
   ```
or test interactively
   ```bash
   docker-compose exec gemini_client python interactive-demo-test.py
   ```

5. **Chat with Gemini using MCP memory:**
   ```bash
   docker-compose exec gemini_client python advanced_gemini_client.py
   ```
   This starts an interactive chat where Gemini can:
   - Remember your conversations
   - Search through your stored memories
   - Answer questions using your personal context
   - Save new information automatically

6. **Save conversations to files:**
   In the interactive chat, use these commands:
   - `!start_session <name>` - Start recording conversation to markdown file
   - `!stop_session` - Stop recording and save to `/conversations/` folder
   - `!export_session` - Export current session without stopping
   - `!list_sessions` - Show all saved conversation files

    **Features:**
   - Conversations saved as readable markdown files
   - Files stored in local `conversations/` folder (not committed to git)
   - Timestamped entries with full conversation history
   - Survives container restarts

   **Example running:**:
   Lees-MacBook-Pro:myserver Lee$ 
   docker-compose exec gemini_client python advanced_gemini_client.py
    ╭────────────────────────────────────────────────────────╮
    │                                                        │
    │                                                        │
    │  🤖 Advanced Gemini + MCP-Mem0 Client                  │
    │                                                        │
    │  Smart AI assistant with long-term memory              │
    │  Powered by Google Gemini 2.0 Flash + MCP Memory       │
    │  Server                                                │
    │                                                        │
    │  ✨ Features:                                          │
    │  • Smart conversation with Gemini                      │
    │  • Automatic memory of all conversations               │
    │  • Search in previous memories                         │
    │  • Relevant context for every question                 │
    │                                                        │
    │                                                        │
    ╰────────────────────────────────────────────────────────╯

    🔄 Checking MCP server connection...
    ❌ Connection failed: All connection attempts failed
    ⚠️ MCP server not accessible, using simulation mode
    🤖 Initializing Gemini...
    ✅ Ready to chat!

    💡 Type !help for commands or just start asking questions!
    🚪 Type 'exit' to quit


    🗣️ Your question: !start_session travel_to_paris


    ✅ Started session: 
    session_2025-08-04_22-38_travel_to_paris

    🗣️ Your question: 
      plan a trip for me to paris, according to my hobbies and food prefrences
  

7. **Stop the system properly:**
   ```bash
   docker-compose down
   ```
   This command:
   - Stops all running containers gracefully
   - Removes containers but keeps your data
   - Preserves all memories in the database
   - Ensures clean restart next time

   **Note:** Your memories are permanently stored and will be available when you restart!




## What it does

- **Saves memories** with semantic understanding
- **Searches memories** using natural language
- **Retrieves all memories** for context
- **Persists data** in PostgreSQL with vector search

## MCP Integration

Connect to Claude Desktop or other MCP clients:

```json
{
  "mcpServers": {
    "memory": {
      "transport": "sse",
      "url": "http://localhost:8050/sse"
    }
  }
}
```

## API Endpoints

- `GET /` - Health check
- `POST /save_memory` - Store information
- `POST /search_memories` - Find relevant memories  
- `GET /get_all_memories` - Get all stored memories

## Configuration

Edit `.env` file:
- `LLM_API_KEY` - Your Gemini API key (required)
- `PORT` - Server port (default: 8050)
- `DATABASE_URL` - PostgreSQL connection (auto-configured)

## Architecture

- **LLM:** Gemini 2.0 Flash
- **Embeddings:** HuggingFace sentence-transformers
- **Database:** PostgreSQL with pgvector
- **Transport:** HTTP/SSE

## Troubleshooting

- **Server not responding:** Wait 2+ minutes for initialization
- **API quota exceeded:** Gemini free tier has daily limits
- **Port conflicts:** Change PORT in .env file

That's it! The system handles everything else automatically.