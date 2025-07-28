#!/usr/bin/env python3
"""
Direct Gemini Client with Mem0 Memory
Uses Mem0 directly for memory management without MCP protocol
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import google.generativeai as genai
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.markdown import Markdown
    from rich.table import Table
    from mem0 import Memory
except ImportError as e:
    print(f"❌ Missing library: {e}")
    print("🔧 Install with: pip install google-generativeai rich mem0ai")
    sys.exit(1)

# Configuration
console = Console()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY_HERE')
DEFAULT_USER_ID = "user"

class DirectMemoryClient:
    """Direct client that uses Mem0 without MCP"""
    
    def __init__(self):
        # Initialize Mem0 with a PURE GEMINI configuration - NO OPENAI!
        config = {
            "llm": {
                "provider": "gemini",
                "config": {
                    "model": "gemini-2.0-flash-exp",
                    "api_key": GEMINI_API_KEY
                }
            },
            "embedder": {
                "provider": "huggingface",
                "config": {
                    "model": "sentence-transformers/all-MiniLM-L6-v2"
                }
            }
            # Using default vector store (SQLite) for simplicity
        }
        
        try:
            self.memory = Memory.from_config(config)
            console.print("✅ [green]Connected to Mem0 directly[/green]")
        except Exception as e:
            console.print(f"❌ [red]Failed to connect to Mem0: {e}[/red]")
            raise

    def save_memory(self, text: str) -> Dict[str, Any]:
        """Save memory directly to Mem0"""
        try:
            console.print(f"💾 [green]Saving memory:[/green] {text[:80]}{'...' if len(text) > 80 else ''}")
            
            messages = [{"role": "user", "content": text}]
            result = self.memory.add(messages, user_id=DEFAULT_USER_ID)
            
            return {
                "status": "success",
                "message": f"Successfully saved memory: {text[:100]}..." if len(text) > 100 else f"Successfully saved memory: {text}",
                "result": result
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def search_memories(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """Search memories directly in Mem0"""
        try:
            console.print(f"🔍 [blue]Searching memories for:[/blue] {query}")
            
            memories = self.memory.search(query, user_id=DEFAULT_USER_ID, limit=limit)
            
            # Extract just the memory text from the results
            if isinstance(memories, dict) and "results" in memories:
                memory_texts = [memory["memory"] for memory in memories["results"]]
            elif isinstance(memories, list):
                memory_texts = [memory.get("memory", str(memory)) for memory in memories]
            else:
                memory_texts = []
            
            return {
                "status": "success",
                "memories": memory_texts,
                "count": len(memory_texts)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_all_memories(self) -> Dict[str, Any]:
        """Get all memories directly from Mem0"""
        try:
            console.print("📚 [blue]Fetching all memories[/blue]")
            
            memories = self.memory.get_all(user_id=DEFAULT_USER_ID)
            
            # Extract just the memory text from the results
            if isinstance(memories, dict) and "results" in memories:
                memory_texts = [memory["memory"] for memory in memories["results"]]
            elif isinstance(memories, list):
                memory_texts = [memory.get("memory", str(memory)) for memory in memories]
            else:
                memory_texts = []
            
            return {
                "status": "success",
                "memories": memory_texts,
                "total": len(memory_texts)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

class DirectGeminiChat:
    """Gemini chat client with direct Mem0 integration"""
    
    def __init__(self, api_key: str, memory_client: DirectMemoryClient):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.memory = memory_client
        self.conversation_history = []
        self.session_start = datetime.now()
        
    def get_context_from_memory(self, user_input: str) -> str:
        """Search for relevant context from memory"""
        try:
            result = self.memory.search_memories(user_input, limit=3)
            
            if result["status"] == "success" and result["memories"]:
                context = "Previous relevant information:\n"
                for i, memory in enumerate(result["memories"], 1):
                    context += f"{i}. {memory}\n"
                return context
            return ""
        except Exception as e:
            console.print(f"❌ [red]Error searching memories: {e}[/red]")
            return ""
    
    def save_conversation_to_memory(self, user_input: str, answer: str):
        """Save the conversation to memory"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            memory_text = f"[{timestamp}] Conversation:\nQuestion: {user_input}\nAnswer: {answer}"
            
            result = self.memory.save_memory(memory_text)
            if result["status"] == "success":
                console.print("💾 [green]Conversation saved to memory[/green]")
            else:
                console.print(f"❌ [red]Failed to save memory: {result['message']}[/red]")
        except Exception as e:
            console.print(f"❌ [red]Error saving to memory: {e}[/red]")
    
    def chat_with_context(self, user_input: str) -> str:
        """Chat with Gemini including memory context"""
        try:
            # Get relevant context from memory
            context = self.get_context_from_memory(user_input)
            
            # Build the prompt with context
            if context.strip():
                prompt = f"{context}\n\nCurrent question: {user_input}\n\nPlease answer based on the previous context and current question."
            else:
                prompt = user_input
            
            # Generate response
            response = self.model.generate_content(prompt)
            answer = response.text if response.text else "Sorry, I couldn't generate a response."
            
            # Save conversation to memory
            self.save_conversation_to_memory(user_input, answer)
            
            # Update conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
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

def display_welcome():
    """Display welcome screen"""
    welcome_text = """
[bold green]🤖 Direct Gemini + Mem0 Client[/bold green]

[blue]Smart AI assistant with long-term memory[/blue]
[dim]Powered by Google Gemini 2.0 Flash + Direct Mem0 Integration[/dim]

✨ Features:
• Smart conversation with Gemini
• Direct memory integration (no MCP protocol)
• Automatic memory of all conversations
• Search in previous memories
• Relevant context for every question
"""
    
    console.print(Panel(welcome_text, border_style="green", padding=(1, 2)))

def display_help():
    """Display help information"""
    help_text = """
[bold blue]Available Commands:[/bold blue]

[green]/help[/green] - Show this help message
[green]/stats[/green] - Show session statistics
[green]/memories[/green] - Show all saved memories
[green]/search <query>[/green] - Search memories
[green]/clear[/green] - Clear screen
[green]/quit[/green] - Exit the application

[yellow]Just type your question to start chatting![/yellow]
"""
    console.print(Panel(help_text, border_style="blue", padding=(1, 2)))

def display_stats(chat_client: DirectGeminiChat):
    """Display session statistics"""
    stats = chat_client.get_session_stats()
    
    table = Table(title="📊 Session Statistics", border_style="cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Questions", str(stats["total_questions"]))
    table.add_row("Questions with Context", str(stats["questions_with_context"]))
    table.add_row("Context Usage Rate", stats["context_usage_rate"])
    table.add_row("Session Duration", stats["session_duration"])
    
    console.print(table)

def display_memories(memory_client: DirectMemoryClient):
    """Display all saved memories"""
    result = memory_client.get_all_memories()
    
    if result["status"] == "success":
        if result["memories"]:
            console.print(f"\n📚 [bold blue]All Memories ({result['total']} total):[/bold blue]\n")
            for i, memory in enumerate(result["memories"], 1):
                console.print(f"[dim]{i}.[/dim] {memory}")
                console.print()
        else:
            console.print("📚 [yellow]No memories saved yet.[/yellow]")
    else:
        console.print(f"❌ [red]Error fetching memories: {result['message']}[/red]")

def search_memories_interactive(memory_client: DirectMemoryClient):
    """Interactive memory search"""
    query = Prompt.ask("🔍 [blue]Enter search query[/blue]")
    
    if query:
        result = memory_client.search_memories(query, limit=5)
        
        if result["status"] == "success":
            if result["memories"]:
                console.print(f"\n🔍 [bold blue]Search Results for '{query}' ({result['count']} found):[/bold blue]\n")
                for i, memory in enumerate(result["memories"], 1):
                    console.print(f"[dim]{i}.[/dim] {memory}")
                    console.print()
            else:
                console.print(f"🔍 [yellow]No memories found for '{query}'.[/yellow]")
        else:
            console.print(f"❌ [red]Search error: {result['message']}[/red]")

async def main():
    """Main application loop"""
    try:
        display_welcome()
        
        # Initialize memory client
        console.print("🔌 [blue]Connecting to memory...[/blue]")
        memory_client = DirectMemoryClient()
        
        # Initialize chat client
        chat_client = DirectGeminiChat(GEMINI_API_KEY, memory_client)
        
        console.print("✅ [green]Ready! Type '/help' for commands or ask me anything![/green]\n")
        
        while True:
            try:
                user_input = Prompt.ask("\n🗣️ [bold cyan]Your question[/bold cyan]").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['/quit', '/exit', '/q']:
                    console.print("👋 [yellow]Goodbye![/yellow]")
                    break
                elif user_input.lower() == '/help':
                    display_help()
                    continue
                elif user_input.lower() == '/stats':
                    display_stats(chat_client)
                    continue
                elif user_input.lower() == '/memories':
                    display_memories(memory_client)
                    continue
                elif user_input.lower().startswith('/search'):
                    search_memories_interactive(memory_client)
                    continue
                elif user_input.lower() == '/clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    display_welcome()
                    continue
                
                # Regular chat
                console.print(f"🔍 [blue]Searching memories for:[/blue] {user_input}")
                
                with console.status("[bold green]Thinking...") as status:
                    answer = chat_client.chat_with_context(user_input)
                
                console.print("\n🤖 [bold green]Gemini:[/bold green]")
                console.print(Panel(Markdown(answer), border_style="green", padding=(1, 2)))
                
            except KeyboardInterrupt:
                console.print("\n👋 [yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"❌ [red]Error: {e}[/red]")
    
    except Exception as e:
        console.print(f"❌ [red]Fatal error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
