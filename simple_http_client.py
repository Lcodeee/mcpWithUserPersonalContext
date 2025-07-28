#!/usr/bin/env python3
"""
Simple HTTP Client for MCP-Mem0 API
-----------------------------------
Simple client that connects to HTTP API and uses Gemini with memory.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import httpx
    import google.generativeai as genai
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.markdown import Markdown
    from rich.table import Table
    from rich.spinner import Spinner
    from rich.live import Live
except ImportError as e:
    print(f"❌ Missing library: {e}")
    print("🔧 Install with: pip install google-generativeai httpx rich")
    sys.exit(1)

# Configuration
console = Console()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY_HERE')
HTTP_API_URL = "http://localhost:8050"

class SimpleHTTPMemoryClient:
    """Simple HTTP client for MCP-Mem0 API"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def test_connection(self) -> bool:
        """Test connection to HTTP API"""
        try:
            response = await self.client.get(f"{self.api_url}/")
            return response.status_code == 200
        except Exception as e:
            console.print(f"❌ [red]Connection failed:[/red] {e}")
            return False
    
    async def save_memory(self, text: str) -> bool:
        """Save information to memory"""
        try:
            response = await self.client.post(
                f"{self.api_url}/save_memory",
                json={"text": text}
            )
            if response.status_code == 200:
                result = response.json()
                console.print(f"✅ [green]Memory saved:[/green] {result.get('message', 'Success')}")
                return True
            else:
                console.print(f"❌ [red]Failed to save memory:[/red] {response.status_code} - {response.text}")
                return False
        except Exception as e:
            console.print(f"❌ [red]Error saving memory:[/red] {e}")
            return False
    
    async def search_memories(self, query: str, limit: int = 3) -> List[str]:
        """Search memories"""
        try:
            response = await self.client.post(
                f"{self.api_url}/search_memories",
                json={"query": query, "limit": limit}
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("memories", [])
            else:
                console.print(f"❌ [red]Failed to search memories:[/red] {response.status_code} - {response.text}")
                return []
        except Exception as e:
            console.print(f"❌ [red]Error searching memories:[/red] {e}")
            return []
    
    async def get_all_memories(self) -> List[str]:
        """Get all memories"""
        try:
            response = await self.client.get(f"{self.api_url}/get_all_memories")
            if response.status_code == 200:
                result = response.json()
                return result.get("memories", [])
            else:
                console.print(f"❌ [red]Failed to get memories:[/red] {response.status_code} - {response.text}")
                return []
        except Exception as e:
            console.print(f"❌ [red]Error getting memories:[/red] {e}")
            return []
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

class GeminiWithMemory:
    """Gemini client with memory functionality"""
    
    def __init__(self, api_key: str, memory_client: SimpleHTTPMemoryClient):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.memory_client = memory_client
        self.conversation_history = []
    
    async def chat_with_memory(self, user_message: str) -> str:
        """Chat with Gemini using memory for context"""
        
        # Search for relevant memories
        console.print("🔍 [yellow]Searching memories...[/yellow]")
        relevant_memories = await self.memory_client.search_memories(user_message, limit=5)
        
        # Build context from memories
        memory_context = ""
        if relevant_memories:
            console.print(f"💭 [blue]Found {len(relevant_memories)} relevant memories[/blue]")
            memory_context = "\n\nRelevant memories:\n" + "\n".join([f"- {memory}" for memory in relevant_memories])
        else:
            console.print("📝 [yellow]No relevant memories found[/yellow]")
        
        # Create prompt with memory context
        full_prompt = f"""You are a helpful AI assistant with access to memory. 
        
User message: {user_message}
{memory_context}

Please respond helpfully, and if the user shares new information about themselves or preferences, make sure to save it to memory."""

        # Get response from Gemini
        console.print("🤖 [cyan]Getting response from Gemini...[/cyan]")
        try:
            response = self.model.generate_content(full_prompt)
            ai_response = response.text
            
            # Save the interaction to memory if it contains new information
            if self._should_save_to_memory(user_message):
                await self.memory_client.save_memory(f"User said: {user_message}")
            
            return ai_response
            
        except Exception as e:
            return f"❌ Error generating response: {e}"
    
    def _should_save_to_memory(self, message: str) -> bool:
        """Determine if a message should be saved to memory"""
        # Simple heuristic - save if message contains personal information indicators
        memory_indicators = [
            "i like", "i love", "i hate", "i prefer", "my favorite",
            "i am", "i'm", "i work", "i live", "my name is",
            "remember", "don't forget", "important to me"
        ]
        return any(indicator in message.lower() for indicator in memory_indicators)

async def main():
    """Main function"""
    console.print(Panel.fit("🚀 Simple Gemini + Memory Client", style="bold green"))
    
    # Initialize memory client
    memory_client = SimpleHTTPMemoryClient(HTTP_API_URL)
    
    # Test connection
    console.print("🔌 Testing connection to memory API...")
    if not await memory_client.test_connection():
        console.print("❌ [red]Cannot connect to memory API. Make sure the server is running.[/red]")
        return
    
    console.print("✅ [green]Connected to memory API![/green]")
    
    # Initialize Gemini client
    gemini_client = GeminiWithMemory(GEMINI_API_KEY, memory_client)
    
    console.print("\n💬 [yellow]You can start chatting! Type 'quit' to exit, 'memories' to see all memories.[/yellow]\n")
    
    try:
        while True:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'memories':
                memories = await memory_client.get_all_memories()
                if memories:
                    table = Table(title="All Memories")
                    table.add_column("Memory", style="cyan")
                    for memory in memories:
                        table.add_row(memory)
                    console.print(table)
                else:
                    console.print("📝 [yellow]No memories found[/yellow]")
                continue
            
            # Get AI response
            with console.status("[bold green]Thinking..."):
                ai_response = await gemini_client.chat_with_memory(user_input)
            
            # Display response
            console.print(f"\n[bold green]AI:[/bold green]")
            console.print(Markdown(ai_response))
            
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n❌ [red]Error:[/red] {e}")
    finally:
        await memory_client.close()

if __name__ == "__main__":
    asyncio.run(main())
