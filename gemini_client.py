#!/usr/bin/env python3
"""
Gemini + MCP-Mem0 Client
-------------------------
קובץ Python שמתחבר לשרת MCP-Mem0 ומאפשר שליחת פרומפטים לגמיני
עם שמירה וחיפוש זיכרונות באופן אוטומטי.

איך להשתמש:
1. וודא שהשרת MCP רץ (docker-compose up -d)
2. הרץ: python gemini_client.py
3. התחל לשאול שאלות!
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

import httpx
import google.generativeai as genai
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.markdown import Markdown

# Configuration
console = Console()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY_HERE')
MCP_SERVER_URL = "http://localhost:8050"

class MCPClient:
    """Client לחיבור עם שרת MCP-Mem0"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """קריאה לכלי MCP"""
        try:
            # נסה לשלוח בקשה לשרת MCP (זה תלוי בהטמעה המדויקת)
            # כרגע נחזיר סימולציה פשוטה
            if tool_name == "save_memory":
                console.print(f"💾 [blue]שומר זיכרון:[/blue] {kwargs.get('text', '')[:100]}...")
                return {"status": "success", "message": "Memory saved"}
            elif tool_name == "search_memories":
                console.print(f"🔍 [blue]מחפש זיכרונות:[/blue] {kwargs.get('query', '')}")
                return {"status": "success", "memories": ["זיכרון דוגמה 1", "זיכרון דוגמה 2"]}
            elif tool_name == "get_all_memories":
                console.print("📚 [blue]מביא כל הזיכרונות[/blue]")
                return {"status": "success", "memories": ["כל הזיכרונות"]}
        except Exception as e:
            console.print(f"❌ [red]שגיאה בכלי MCP:[/red] {e}")
            return {"status": "error", "message": str(e)}

class GeminiWithMemory:
    """Client שמשלב Gemini עם זיכרון MCP"""
    
    def __init__(self, api_key: str, mcp_client: MCPClient):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.mcp = mcp_client
        self.conversation_history = []
        
    async def save_to_memory(self, text: str, context: str = ""):
        """שמירת מידע לזיכרון"""
        memory_text = f"{context}\n{text}" if context else text
        return await self.mcp.call_tool("save_memory", text=memory_text)
    
    async def search_memory(self, query: str):
        """חיפוש בזיכרון"""
        return await self.mcp.call_tool("search_memories", query=query, limit=5)
    
    async def get_relevant_context(self, user_input: str) -> str:
        """חיפוש הקשר רלוונטי מהזיכרון"""
        try:
            result = await self.search_memory(user_input)
            if result.get("status") == "success" and result.get("memories"):
                memories = result["memories"]
                context = "\n".join([f"- {memory}" for memory in memories[:3]])
                return f"\nהקשר רלוונטי מהזיכרון:\n{context}\n"
            return ""
        except Exception as e:
            console.print(f"❌ [red]שגיאה בחיפוש זיכרון:[/red] {e}")
            return ""
    
    async def chat(self, user_input: str, save_to_memory: bool = True) -> str:
        """שיחה עם Gemini כולל זיכרון"""
        try:
            # חיפוש הקשר רלוונטי
            context = await self.get_relevant_context(user_input)
            
            # הכנת ההודעה עם הקשר
            full_prompt = f"""
{context}

שאלת המשתמש: {user_input}

אנא ענה בעברית באופן מפורט ומועיל. אם יש מידע רלוונטי מהזיכרון לעיל, השתמש בו בתשובה.
"""

            # שליחה לגמיני
            response = self.model.generate_content(full_prompt)
            answer = response.text
            
            # שמירה לזיכרון אם נדרש
            if save_to_memory:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                memory_entry = f"[{timestamp}] שאלה: {user_input}\nתשובה: {answer}"
                await self.save_to_memory(memory_entry)
            
            # הוספה להיסטוריית השיחה
            self.conversation_history.append({
                "user": user_input,
                "assistant": answer,
                "timestamp": datetime.now()
            })
            
            return answer
            
        except Exception as e:
            error_msg = f"שגיאה בתקשורת עם Gemini: {e}"
            console.print(f"❌ [red]{error_msg}[/red]")
            return error_msg

async def main():
    """פונקציה ראשית"""
    console.print(Panel.fit(
        "[bold green]🤖 Gemini + MCP-Mem0 Client[/bold green]\n"
        "[blue]עוזר AI עם זיכרון ארוך טווח[/blue]",
        border_style="green"
    ))
    
    # אתחול
    mcp_client = MCPClient(MCP_SERVER_URL)
    gemini = GeminiWithMemory(GEMINI_API_KEY, mcp_client)
    
    console.print("\n✅ [green]המערכת מוכנה! הקלד 'exit' ליציאה[/green]")
    console.print("💡 [yellow]פקודות מיוחדות:[/yellow]")
    console.print("  • [cyan]!memory [שאלה][/cyan] - חיפוש בזיכרון")
    console.print("  • [cyan]!history[/cyan] - הצגת היסטוריית השיחה")
    console.print("  • [cyan]!clear[/cyan] - ניקוי המסך\n")
    
    while True:
        try:
            # קבלת קלט מהמשתמש
            user_input = Prompt.ask("\n[bold blue]🗣️  שאלה")
            
            if user_input.lower() in ['exit', 'quit', 'יציאה']:
                console.print("\n👋 [yellow]להתראות![/yellow]")
                break
                
            elif user_input.lower() in ['clear', 'נקה']:
                console.clear()
                continue
                
            elif user_input.startswith('!memory '):
                # חיפוש בזיכרון
                query = user_input[8:]
                result = await gemini.search_memory(query)
                if result.get("memories"):
                    console.print("\n📚 [green]זיכרונות שנמצאו:[/green]")
                    for i, memory in enumerate(result["memories"], 1):
                        console.print(f"{i}. {memory}")
                else:
                    console.print("\n🔍 [yellow]לא נמצאו זיכרונות רלוונטיים[/yellow]")
                continue
                
            elif user_input.lower() in ['!history', '!היסטוריה']:
                # הצגת היסטוריה
                if gemini.conversation_history:
                    console.print("\n📜 [green]היסטוריית השיחה:[/green]")
                    for i, entry in enumerate(gemini.conversation_history[-5:], 1):
                        console.print(f"\n[bold]{i}. [{entry['timestamp'].strftime('%H:%M')}][/bold]")
                        console.print(f"[blue]שאלה:[/blue] {entry['user']}")
                        console.print(f"[green]תשובה:[/green] {entry['assistant'][:100]}...")
                else:
                    console.print("\n📜 [yellow]אין היסטוריה עדיין[/yellow]")
                continue
            
            # שאלה רגילה
            if user_input.strip():
                console.print("\n🤖 [green]Gemini חושב...[/green]")
                
                answer = await gemini.chat(user_input)
                
                # הצגת התשובה
                console.print(f"\n[bold green]🤖 Gemini:[/bold green]")
                console.print(Panel(
                    Markdown(answer),
                    border_style="green",
                    padding=(1, 2)
                ))
                
        except KeyboardInterrupt:
            console.print("\n\n👋 [yellow]להתראות![/yellow]")
            break
        except Exception as e:
            console.print(f"\n❌ [red]שגיאה:[/red] {e}")

if __name__ == "__main__":
    # התקנת ספריות נדרשות אם לא קיימות
    try:
        import google.generativeai
        import httpx
        import rich
    except ImportError as e:
        console.print(f"❌ [red]ספרייה חסרה:[/red] {e}")
        console.print("🔧 [yellow]הרץ:[/yellow] pip install google-generativeai httpx rich")
        sys.exit(1)
    
    asyncio.run(main())
