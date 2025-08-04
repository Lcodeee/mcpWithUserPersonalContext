#!/usr/bin/env python3
"""
Advanced Gemini + MCP-Mem0 Client
----------------------------------
Advanced client that connects to MCP server and uses Gemini with memory.
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
MCP_SERVER_URL = "http://localhost:8050"

class RealMCPClient:
    """Real client to connect with MCP-Mem0 server via HTTP"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def test_connection(self) -> bool:
        """Test connection to MCP server"""
        try:
            response = await self.client.get(f"{self.server_url}/")
            return response.status_code in [200, 404]  # 404 is OK, means server is running
        except Exception as e:
            console.print(f"❌ [red]Connection failed:[/red] {e}")
            return False
    
    async def save_memory(self, text: str) -> Dict[str, Any]:
        """Save memory via MCP server"""
        try:
            console.print(f"💾 [green]Saving memory:[/green] {text[:80]}{'...' if len(text) > 80 else ''}")
            
            # Call the MCP server tool
            payload = {
                "method": "tools/call",
                "params": {
                    "name": "save_memory",
                    "arguments": {
                        "text": text
                    }
                }
            }
            
            response = await self.client.post(
                f"{self.server_url}/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {"status": "success", "message": result.get("content", "Memory saved successfully")}
            else:
                return {"status": "error", "message": f"Server returned {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def search_memories(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search memories via MCP server"""
        try:
            console.print(f"🔍 [blue]Searching memories for:[/blue] {query}")
            
            # Call the MCP server tool
            payload = {
                "method": "tools/call",
                "params": {
                    "name": "search_memories",
                    "arguments": {
                        "query": query,
                        "limit": limit
                    }
                }
            }
            
            response = await self.client.post(
                f"{self.server_url}/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", "[]")
                try:
                    memories = json.loads(content) if isinstance(content, str) else content
                    return {
                        "status": "success",
                        "memories": memories,
                        "count": len(memories) if isinstance(memories, list) else 0
                    }
                except json.JSONDecodeError:
                    return {"status": "error", "message": f"Invalid JSON response: {content}"}
            else:
                return {"status": "error", "message": f"Server returned {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_all_memories(self) -> Dict[str, Any]:
        """Get all memories via MCP server"""
        try:
            console.print("📚 [blue]Fetching all memories[/blue]")
            
            # Call the MCP server tool
            payload = {
                "method": "tools/call",
                "params": {
                    "name": "get_all_memories",
                    "arguments": {}
                }
            }
            
            response = await self.client.post(
                f"{self.server_url}/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", "[]")
                try:
                    memories = json.loads(content) if isinstance(content, str) else content
                    return {
                        "status": "success",
                        "memories": memories,
                        "total": len(memories) if isinstance(memories, list) else 0
                    }
                except json.JSONDecodeError:
                    return {"status": "error", "message": f"Invalid JSON response: {content}"}
            else:
                return {"status": "error", "message": f"Server returned {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

class AdvancedGeminiChat:
    """Advanced client for chatting with Gemini including memory"""
    
    def __init__(self, api_key: str, mcp_client: RealMCPClient):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.mcp = mcp_client
        self.conversation_history = []
        self.session_start = datetime.now()
        
    async def get_context_from_memory(self, user_input: str) -> str:
        """Search for relevant context from memory"""
        try:
            result = await self.mcp.search_memories(user_input, limit=3)
            
            if result.get("status") == "success" and result.get("memories"):
                memories = result["memories"]
                if memories:
                    context_parts = []
                    for i, memory in enumerate(memories, 1):
                        context_parts.append(f"{i}. {memory}")
                    
                    return f"""
Relevant context from previous memories:
{chr(10).join(context_parts)}

---
"""
            return ""
        except Exception as e:
            console.print(f"⚠️ [yellow]Memory search warning:[/yellow] {e}")
            return ""
    
    async def chat_with_memory(self, user_input: str, save_conversation: bool = True) -> str:
        """Chat with Gemini including automatic memory management"""
        try:
            # Step 1: Search for relevant context
            context = await self.get_context_from_memory(user_input)
            
            # Step 2: Prepare detailed prompt
            system_prompt = f"""
You are a smart and helpful AI assistant.
{context}

Session time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Session duration: {str(datetime.now() - self.session_start).split('.')[0]}

User question: {user_input}

Instructions:
1. Answer clearly and in detail
2. If there is relevant context from previous memories, use it
3. If the question requires technical information, provide clear examples
4. Be friendly and helpful
"""

            # Step 3: Send to Gemini with spinner
            with console.status("[bold green]🤖 Gemini is thinking...") as status:
                response = self.model.generate_content(system_prompt)
                answer = response.text
            
            # Step 4: Save conversation to memory
            if save_conversation:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conversation_entry = f"""
[{timestamp}] Conversation:
Question: {user_input}
Answer: {answer[:500]}{'...' if len(answer) > 500 else ''}
"""
                await self.mcp.save_memory(conversation_entry)
            
            # Step 5: Update local history
            self.conversation_history.append({
                "timestamp": datetime.now(),
                "user": user_input,
                "assistant": answer,
                "had_context": bool(context.strip())
            })
            
            return answer
            
        except Exception as e:
            error_msg = f"Error communicating with Gemini: {str(e)}"
            console.print(f"❌ [red]{error_msg}[/red]")
            return error_msg
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Current session statistics"""
        total_questions = len(self.conversation_history)
        questions_with_context = sum(1 for conv in self.conversation_history if conv.get("had_context"))
        session_duration = datetime.now() - self.session_start
        
        return {
            "total_questions": total_questions,
            "questions_with_context": questions_with_context,
            "session_duration": str(session_duration).split('.')[0],
            "context_usage_rate": f"{questions_with_context/total_questions*100:.1f}%" if total_questions > 0 else "0%"
        }

async def display_welcome():
    """Display welcome screen"""
    welcome_text = """
[bold green]🤖 Advanced Gemini + MCP-Mem0 Client[/bold green]

[blue]Smart AI assistant with long-term memory[/blue]
[dim]Powered by Google Gemini 2.0 Flash + MCP Memory Server[/dim]

✨ Features:
• Smart conversation with Gemini
• Automatic memory of all conversations
• Search in previous memories
• Relevant context for every question
"""
    
    console.print(Panel(welcome_text, border_style="green", padding=(1, 2)))

async def display_commands():
    """Display available commands"""
    table = Table(title="🛠️ Available Commands", border_style="cyan")
    table.add_column("Command", style="cyan", width=20)
    table.add_column("Description", style="white")
    
    table.add_row("!memory <query>", "Direct search in memory")
    table.add_row("!history", "Show conversation history")
    table.add_row("!stats", "Session statistics")
    table.add_row("!clear", "Clear screen")
    table.add_row("!help", "Show this help")
    table.add_row("exit / quit", "Exit the program")
    
    console.print(table)

async def main():
    """Main function"""
    await display_welcome()
    
    # Check MCP server connection
    mcp_client = RealMCPClient(MCP_SERVER_URL)
    
    console.print("\n🔄 [yellow]Checking MCP server connection...[/yellow]")
    
    if await mcp_client.test_connection():
        console.print("✅ [green]MCP server is running![/green]")
    else:
        console.print("⚠️ [yellow]MCP server not accessible, using simulation mode[/yellow]")
    
    # Initialize Gemini
    console.print("🤖 [blue]Initializing Gemini...[/blue]")
    gemini = AdvancedGeminiChat(GEMINI_API_KEY, mcp_client)
    console.print("✅ [green]Ready to chat![/green]\n")
    
    console.print("💡 [cyan]Type !help for commands or just start asking questions![/cyan]")
    console.print("🚪 [dim]Type 'exit' to quit[/dim]\n")
    
    # Main chat loop
    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]🗣️ Your question")
            
            if not user_input.strip():
                continue
                
            user_input = user_input.strip()
            
            # Special commands
            if user_input.lower() in ['exit', 'quit']:
                stats = gemini.get_session_stats()
                console.print(f"\n📊 [green]Session summary:[/green]")
                console.print(f"   Questions asked: {stats['total_questions']}")
                console.print(f"   Duration: {stats['session_duration']}")
                console.print(f"   Context usage: {stats['context_usage_rate']}")
                console.print("\n👋 [yellow]Goodbye![/yellow]")
                break
                
            elif user_input.lower() in ['clear']:
                console.clear()
                await display_welcome()
                continue
                
            elif user_input.lower() in ['!help']:
                await display_commands()
                continue
                
            elif user_input.lower() in ['!stats']:
                stats = gemini.get_session_stats()
                stats_table = Table(title="📊 Session Statistics", border_style="blue")
                stats_table.add_column("Metric", style="cyan")
                stats_table.add_column("Value", style="white")
                
                for key, value in stats.items():
                    stats_table.add_row(key.replace('_', ' ').title(), str(value))
                
                console.print(stats_table)
                continue
                
            elif user_input.startswith('!memory '):
                query = user_input[8:].strip()
                if query:
                    result = await mcp_client.search_memories(query, limit=5)
                    if result.get("memories"):
                        console.print(f"\n🧠 [green]Found {len(result['memories'])} relevant memories:[/green]")
                        for i, memory in enumerate(result["memories"], 1):
                            console.print(f"{i}. [dim]{memory}[/dim]")
                    else:
                        console.print("\n🔍 [yellow]No relevant memories found[/yellow]")
                else:
                    console.print("❌ [red]Please provide a search query[/red]")
                continue
                
            elif user_input.lower() in ['!history']:
                if gemini.conversation_history:
                    recent_history = gemini.conversation_history[-5:]
                    console.print(f"\n📜 [green]Recent conversation history ({len(recent_history)} entries):[/green]")
                    
                    for i, entry in enumerate(recent_history, 1):
                        time_str = entry["timestamp"].strftime("%H:%M")
                        context_indicator = "🧠" if entry.get("had_context") else "💭"
                        
                        console.print(f"\n[bold]{i}. [{time_str}] {context_indicator}[/bold]")
                        console.print(f"[blue]Q:[/blue] {entry['user']}")
                        console.print(f"[green]A:[/green] {entry['assistant'][:150]}{'...' if len(entry['assistant']) > 150 else ''}")
                else:
                    console.print("\n📜 [yellow]No conversation history yet[/yellow]")
                continue
            
            # Regular question to Gemini
            answer = await gemini.chat_with_memory(user_input)
            
            # Display the answer
            console.print(f"\n[bold green]🤖 Gemini:[/bold green]")
            console.print(Panel(
                Markdown(answer),
                border_style="green",
                padding=(1, 2)
            ))
            
        except KeyboardInterrupt:
            console.print("\n\n👋 [yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n❌ [red]Error:[/red] {e}")
            console.print("[dim]Please try again or type !help for commands[/dim]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Fatal error:[/red] {e}")
        sys.exit(1)
